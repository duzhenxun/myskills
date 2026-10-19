#!/usr/bin/env bash
#
# Undo install.sh: stop the adapter, restore config.toml, remove files.
#
#   ./uninstall.sh                 # restore the newest config.toml backup
#   ./uninstall.sh --keep-config   # only stop/remove the adapter
#   ./uninstall.sh --purge         # also delete ~/.codex/models.json
set -euo pipefail

CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
LABEL=""
KEEP_CONFIG=0
PURGE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --codex-home) CODEX_HOME_DIR="${2:-}"; shift 2 ;;
    --label) LABEL="${2:-}"; shift 2 ;;
    --keep-config) KEEP_CONFIG=1; shift ;;
    --purge) PURGE=1; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

CODEX_HOME_DIR="${CODEX_HOME_DIR/#\~/$HOME}"
ADIR="$CODEX_HOME_DIR/deepseek-adapter"
OS="$(uname -s)"
[ -n "$LABEL" ] || LABEL="com.$(id -un).codex-deepseek-adapter"

echo "==> Codex + DeepSeek uninstaller"

case "$OS" in
  Darwin)
    PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null && echo "    stopped $LABEL" || true
    if [ -f "$PLIST" ]; then rm -f "$PLIST"; echo "    removed $PLIST"; fi
    ;;
  Linux)
    if command -v systemctl >/dev/null 2>&1; then
      systemctl --user disable --now "$LABEL.service" 2>/dev/null && echo "    stopped $LABEL" || true
      rm -f "$HOME/.config/systemd/user/$LABEL.service"
      systemctl --user daemon-reload 2>/dev/null || true
    fi
    ;;
esac

if [ "$KEEP_CONFIG" = "0" ]; then
  CONFIG="$CODEX_HOME_DIR/config.toml"
  BACKUP="$(ls -1t "$CONFIG".bak-* 2>/dev/null | head -1 || true)"
  if [ -n "$BACKUP" ]; then
    cp "$BACKUP" "$CONFIG"
    echo "    config.toml restored from $(basename "$BACKUP")"
  fi

  # Run the cleanup on whatever we ended up with, backup or not. A backup taken
  # by a *re*-install already contains the adapter settings (install.sh backs up
  # on every run), so restoring alone is not enough to make uninstall complete.
  # This pass is idempotent and only removes our own artifacts.
  if [ -f "$CONFIG" ]; then
    python3 - "$CONFIG" <<'PY'
import re, sys

path = sys.argv[1]
lines = open(path, encoding="utf-8").read().split("\n")
changed = False

# 1. drop the managed block + the tagged-backup comment, restore disabled lines
out, inside = [], False
for line in lines:
    s = line.strip()
    if s.startswith("# >>> codex-deepseek: managed block"):
        inside = True
        changed = True
        continue
    if inside:
        if s.startswith("# <<< codex-deepseek: end managed block"):
            inside = False
        continue
    if s.startswith("#[codex-deepseek:disabled] "):
        line = line.replace("#[codex-deepseek:disabled] ", "", 1)
        changed = True
    if line.strip().startswith("# --- previous settings, tagged by install.sh"):
        changed = True
        continue
    out.append(line)

# 2. drop [model_providers.*] tables that point at the local adapter, so the
#    copied bearer token does not survive an uninstall.
LOOPBACK = re.compile(r"^\s*base_url\s*=\s*[\"']https?://(127\.0\.0\.1|localhost)(:\d+)?/?[\"']\s*$")
kept, dropped, i = [], [], 0
while i < len(out):
    m = re.match(r"^\s*\[([^\]]+)\]\s*$", out[i])
    if m and m.group(1).startswith("model_providers."):
        j = i + 1
        while j < len(out) and not re.match(r"^\s*\[", out[j]):
            j += 1
        table = out[i:j]
        if any(LOOPBACK.match(t) for t in table):
            dropped.append(m.group(1))
            changed = True
            i = j
            while kept and not kept[-1].strip():
                kept.pop()
            if kept:
                kept.append("")
            continue
        kept.extend(table)
        i = j
        continue
    kept.append(out[i])
    i += 1

if changed:
    body = "\n".join(kept).rstrip("\n")
    open(path, "w", encoding="utf-8").write(body + "\n" if body else "")
    msg = "    config.toml cleaned of adapter settings"
    if dropped:
        msg += "; dropped provider(s): " + ", ".join(dropped)
    print(msg)
PY
  fi
fi

if [ -d "$ADIR" ]; then rm -rf "$ADIR"; echo "    removed $ADIR"; fi
if [ "$PURGE" = "1" ]; then
  rm -f "$CODEX_HOME_DIR/models.json" && echo "    removed $CODEX_HOME_DIR/models.json"
fi

echo "==> done. Restart the Codex desktop app if it is running."
