#!/usr/bin/env bash
#
# Codex + DeepSeek installer (nexita relay).
#
# Installs a tiny local adapter in front of the relay, points Codex at it and
# writes a matching model catalog. Idempotent: re-running is safe.
#
#   ./install.sh --key sk-xxxxxxxx
#
# See README.md for what it changes and how to verify / revert.
set -euo pipefail

SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SELF/files"

KEY=""
BASE_URL="https://codeapi.nexita.net"
MODEL="deepseek-v4.1-flash"
MODEL_ALT="deepseek-v4-pro"
PORT="8899"
CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
OPENAI_KEY=""
REPOINT=""
LABEL=""
INSTALL_SERVICE=1
VERIFY=1
CAPTURE=1
UI=1
CAPTURE_DIR=""
CAPTURE_KEEP_DAYS=""

usage() {
  cat <<'EOF'
Usage: ./install.sh --key <API_KEY> [options]
       ./install.sh                     guided setup: asks for the key instead

Required
  --key KEY               relay API key used for deepseek/glm/kimi models
                          (omit it and run in a terminal for the Q&A wizard)

Options
  --base-url URL          upstream relay (default https://codeapi.nexita.net)
  --model SLUG            primary model (default deepseek-v4.1-flash)
  --model-alt SLUG        second catalog entry (default deepseek-v4-pro, "" = none)
  --port N                local adapter port (default 8899)
  --codex-home DIR        Codex home (default $CODEX_HOME or ~/.codex)
  --openai-key KEY        second key for gpt-* models (optional; only needed if
                          you also keep using OpenAI models through this adapter)
  --repoint-provider NAME extra provider id to point at the adapter, e.g. OpenAI.
                          Use this when old threads recorded another provider.
  --label NAME            service label (default com.<user>.codex-deepseek-adapter)
  --capture-dir DIR       where request/response logs go
                          (default <codex-home>/deepseek-adapter/logs/exchanges)
  --capture-keep-days N   delete capture days older than N (default 7, 0 = keep)
  --no-capture            do not record request/response bodies at all
  --no-ui                 do not serve the live web UI on /__ui
  --no-service            write files + config, do not register a service
  --skip-verify           do not run the health / model / codex smoke tests
  -h, --help              this text
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --key) KEY="${2:-}"; shift 2 ;;
    --base-url) BASE_URL="${2:-}"; shift 2 ;;
    --model) MODEL="${2:-}"; shift 2 ;;
    --model-alt) MODEL_ALT="${2:-}"; shift 2 ;;
    --port) PORT="${2:-}"; shift 2 ;;
    --codex-home) CODEX_HOME_DIR="${2:-}"; shift 2 ;;
    --openai-key) OPENAI_KEY="${2:-}"; shift 2 ;;
    --repoint-provider) REPOINT="${2:-}"; shift 2 ;;
    --label) LABEL="${2:-}"; shift 2 ;;
    --capture-dir) CAPTURE_DIR="${2:-}"; shift 2 ;;
    --capture-keep-days) CAPTURE_KEEP_DAYS="${2:-}"; shift 2 ;;
    --no-capture) CAPTURE=0; shift ;;
    --no-ui) UI=0; shift ;;
    --no-service) INSTALL_SERVICE=0; shift ;;
    --skip-verify) VERIFY=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

# -------------------------------------------------------------- guided setup
# Defined here, called after the environment checks below. Without --key it asks
# for the couple of things we cannot guess; everything else keeps its
# recommended default, so the wizard is 1-2 questions. Exits 3 if the user
# cancels, so wrappers can tell "cancelled" apart from "failed".
guided_setup() {
  [ -z "$KEY" ] || return 0
  if [ ! -t 0 ]; then
    echo "error: --key is required (run ./install.sh in a terminal for guided setup)" >&2
    usage >&2
    exit 2
  fi

  mask_key() {
    _k="$1"
    if [ "${#_k}" -le 10 ]; then
      printf '****'
    else
      printf '%s…%s' "$(printf '%s' "$_k" | cut -c1-4)" \
                     "$(printf '%s' "$_k" | rev | cut -c1-4 | rev)"
    fi
  }

  cat <<'BANNER'

  ┌──────────────────────────────────────────────┐
  │   Codex 改用 DeepSeek · 引导式安装           │
  └──────────────────────────────────────────────┘
  只问 1~2 个问题，其余都用推荐默认值。
  按回车 = 采用默认；中途放弃按 Control-C。
BANNER

  # If the clipboard already holds something key-shaped, offer it as the answer.
  # Only accept plausible credentials: a URL or a sentence must not be offered.
  CLIP=""
  if command -v pbpaste >/dev/null 2>&1; then
    CLIP="$(pbpaste 2>/dev/null | tr -d '\r\n' || true)"
  fi
  case "$CLIP" in
    sk-*|key-*|*[!A-Za-z0-9._~-]*) CLIP="" ;;
  esac
  [ "${#CLIP}" -ge 20 ] || CLIP=""

  while [ -z "$KEY" ]; do
    if [ -n "$CLIP" ]; then
      printf '\n  剪贴板里已有一串像 key 的文本（%s），直接回车就用它：\n  key: ' "$(mask_key "$CLIP")"
    else
      printf '\n  请粘贴网关 key（输入时不显示字符，粘贴后回车）：\n  key: '
    fi
    read -rs _REPLY || true
    printf '\n'
    if [ -n "$_REPLY" ]; then KEY="$_REPLY"; else KEY="$CLIP"; fi
    [ -n "$KEY" ] || printf '  ✗ key 不能为空，再试一次。\n'
  done

  printf '\n  你还会用 gpt-*（OpenAI）模型吗？会就用 --openai-key 那把；\n  不会就直接回车跳过。\n  gpt key（可留空）: '
  read -rs _REPLY2 || true
  printf '\n'
  OPENAI_KEY="${_REPLY2:-}"

  # Old sessions recorded model_provider = "OpenAI"; pointing that provider at
  # the adapter keeps them working. Harmless and reversible, so default to yes.
  REPOINT="OpenAI"
  printf '\n  以前在这台机器上跑过 gpt-* 的 Codex 任务吗？\n  （老会话续聊需要这一项，随时可还原）回车 = 是：'
  read -r _REPLY3 || true
  case "${_REPLY3:-Y}" in
    [Nn]*) REPOINT="" ;;
  esac

  if [ -n "$REPOINT" ]; then _OLD=是; else _OLD=否; fi
  if [ -n "$OPENAI_KEY" ]; then
    _GPT="$(mask_key "$OPENAI_KEY")"
  else
    _GPT="（未提供，gpt 请求继续用 Codex 自己已有的凭据）"
  fi
  cat <<EOF

  ── 将按下面的设置安装 ──────────────────────────────
  key          : $(mask_key "$KEY")
  gpt key      : $_GPT
  网关         : $BASE_URL
  模型         : $MODEL${MODEL_ALT:+ / $MODEL_ALT}
  本地适配器   : http://127.0.0.1:$PORT   （日志网页 /__ui）
  Codex 目录   : $CODEX_HOME_DIR
  兼容老会话   : $_OLD
  ────────────────────────────────────────────────────

EOF
  printf '  开始安装？回车 = 开始，输入 n 取消：'
  read -r _CONFIRM || true
  case "${_CONFIRM:-Y}" in
    [Nn]*) echo "  已取消，什么都没改。"; exit 3 ;;
  esac
  echo
}
[ -f "$SRC/adapter.py" ] || { echo "error: $SRC/adapter.py missing" >&2; exit 1; }
[ -f "$SRC/models.json" ] || { echo "error: $SRC/models.json missing" >&2; exit 1; }

PY="$(command -v python3 || true)"
[ -n "$PY" ] || { echo "error: python3 not found (macOS: install Xcode CLT)" >&2; exit 1; }

guided_setup
[ -n "$KEY" ] || { echo "error: --key is required" >&2; usage >&2; exit 2; }

CODEX_HOME_DIR="${CODEX_HOME_DIR/#\~/$HOME}"
ADIR="$CODEX_HOME_DIR/deepseek-adapter"
OS="$(uname -s)"
[ -n "$LABEL" ] || LABEL="com.$(id -un).codex-deepseek-adapter"

echo "==> Codex + DeepSeek installer"
echo "    codex home : $CODEX_HOME_DIR"
echo "    adapter    : $ADIR (port $PORT -> $BASE_URL)"
echo "    model      : $MODEL${MODEL_ALT:+ / $MODEL_ALT}"

# ---------------------------------------------------------------- adapter files
mkdir -p "$ADIR/logs"
install -m 755 "$SRC/adapter.py" "$ADIR/adapter.py"
install -m 755 "$SRC/captures.py" "$ADIR/captures.py"
( umask 077; "$PY" - "$ADIR/settings.json" "$CAPTURE" "$CAPTURE_DIR" "$CAPTURE_KEEP_DAYS" "$UI" <<'PY'
import json, sys

dest, capture, capture_dir, keep_days, ui = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
cfg = {
    "_comment": "capture/UI settings for adapter.py and captures.py; env vars override this file",
    "capture": capture != "0",
    "capture_dir": capture_dir or None,
    "capture_keep_days": int(keep_days) if keep_days else 7,
    "capture_max_bytes": 8 * 1024 * 1024,
    "capture_max_total_bytes": 2 * 1024 ** 3,
    "ui": ui != "0",
}
if not cfg["capture_dir"]:
    del cfg["capture_dir"]
with open(dest, "w", encoding="utf-8") as fh:
    json.dump(cfg, fh, indent=2)
    fh.write("\n")
PY
)
chmod 600 "$ADIR/settings.json"
( umask 077; "$PY" - "$ADIR/keys.json" "$KEY" "$OPENAI_KEY" <<'PY'
import json, sys
dest, key, openai_key = sys.argv[1], sys.argv[2], sys.argv[3]
cfg = {
    "_comment": "model -> upstream credential routing for adapter.py; keep mode 600",
    "open_model_key": key,
}
if openai_key:
    cfg["openai_key"] = openai_key
with open(dest, "w", encoding="utf-8") as fh:
    json.dump(cfg, fh, indent=2)
    fh.write("\n")
PY
)
chmod 600 "$ADIR/keys.json"
echo "==> adapter.py + captures.py + settings.json + keys.json installed"

# ------------------------------------------------------- config.toml + catalog
set -- --codex-home "$CODEX_HOME_DIR" --key "$KEY" --adapter-url "http://127.0.0.1:$PORT" \
       --model "$MODEL" --model-alt "$MODEL_ALT" --catalog-src "$SRC/models.json"
if [ -n "$REPOINT" ]; then set -- "$@" --repoint-provider "$REPOINT"; fi
"$PY" "$SRC/setup_config.py" "$@"

# ------------------------------------------------------- background service
if [ "$INSTALL_SERVICE" = "1" ]; then
  case "$OS" in
    Darwin)
      PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
      mkdir -p "$HOME/Library/LaunchAgents"
      cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$ADIR/adapter.py</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>CODEX_ADAPTER_PORT</key>
        <string>$PORT</string>
        <key>CODEX_ADAPTER_UPSTREAM</key>
        <string>$BASE_URL</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>ThrottleInterval</key>
    <integer>10</integer>
    <key>ProcessType</key>
    <string>Background</string>
    <key>StandardOutPath</key>
    <string>$ADIR/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$ADIR/logs/stderr.log</string>
</dict>
</plist>
EOF
      launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
      launchctl bootstrap "gui/$(id -u)" "$PLIST"
      launchctl kickstart -k "gui/$(id -u)/$LABEL" >/dev/null
      echo "==> launchd service '$LABEL' started (auto-start + auto-restart)"
      echo "    restart: launchctl kickstart -k gui/$(id -u)/$LABEL"
      ;;
    Linux)
      if command -v systemctl >/dev/null 2>&1; then
        UNIT_DIR="$HOME/.config/systemd/user"
        mkdir -p "$UNIT_DIR"
        cat > "$UNIT_DIR/$LABEL.service" <<EOF
[Unit]
Description=Codex DeepSeek adapter
After=network-online.target

[Service]
ExecStart=$PY $ADIR/adapter.py
Environment=CODEX_ADAPTER_PORT=$PORT
Environment=CODEX_ADAPTER_UPSTREAM=$BASE_URL
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF
        systemctl --user daemon-reload
        systemctl --user enable --now "$LABEL.service"
        echo "==> systemd --user unit '$LABEL' started"
        echo "    (tip: loginctl enable-linger $(id -un) to keep it running after logout)"
      else
        echo "==> no systemd: start it yourself, e.g."
        echo "    CODEX_ADAPTER_PORT=$PORT nohup $PY '$ADIR/adapter.py' >> '$ADIR/logs/stdout.log' 2>&1 &"
      fi
      ;;
    *)
      echo "!! unknown OS '$OS': start the adapter manually:"
      echo "   CODEX_ADAPTER_PORT=$PORT $PY '$ADIR/adapter.py'"
      ;;
  esac
else
  echo "==> --no-service: start it yourself:"
  echo "    CODEX_ADAPTER_PORT=$PORT $PY '$ADIR/adapter.py' &"
fi

# ---------------------------------------------------------------- verification
if [ "$VERIFY" = "1" ]; then
  echo "==> verifying"
  HEALTHY=0
  for _ in $(seq 1 30); do
    if curl -fsS --max-time 5 "http://127.0.0.1:$PORT/__health" >/dev/null 2>&1; then HEALTHY=1; break; fi
    sleep 0.5
  done
  if [ "$HEALTHY" != "1" ]; then
    echo "!! adapter not responding on 127.0.0.1:$PORT" >&2
    echo "   check: tail -20 $ADIR/logs/stderr.log" >&2
    echo "   log  : tail -20 $ADIR/logs/adapter.log" >&2
    exit 1
  fi
  echo "    health: ok"

  BODY=$("$PY" -c 'import json,sys; print(json.dumps({"model": sys.argv[1], "input": "Reply with exactly: INSTALL-OK", "reasoning": {"effort": "high"}}))' "$MODEL")
  CODE=$(curl -sS --max-time 300 -o /tmp/codex-deepseek-install-check.json -w '%{http_code}' \
    -X POST "http://127.0.0.1:$PORT/responses" \
    -H "Authorization: Bearer $KEY" -H 'content-type: application/json' \
    -d "$BODY" || echo 000)
  if [ "$CODE" = "200" ]; then
    echo "    model call ($MODEL, effort=high): 200"
  else
    echo "!! model call failed: HTTP $CODE" >&2
    head -c 400 /tmp/codex-deepseek-install-check.json >&2; echo >&2
    echo "   this is usually a key/model mismatch; check: $BASE_URL/v1/models" >&2
    exit 1
  fi

  if command -v codex >/dev/null 2>&1; then
    TMPDIR_CHECK="$(mktemp -d)"
    echo "    codex exec smoke test (this takes ~10s)"
    SMOKE_OK=0
    for _ in 1 2; do
      if (cd "$TMPDIR_CHECK" && CODEX_HOME="$CODEX_HOME_DIR" codex exec --skip-git-repo-check \
          "Reply with exactly: CODEX-OK" > /tmp/codex-deepseek-smoke.log 2>&1); then
        SMOKE_OK=1; break
      fi
      sleep 3
    done
    if [ "$SMOKE_OK" = "1" ]; then
      echo "    codex exec: ok"
    elif grep -qE "Error loading config|Invalid request body|not supported by any configured account|401 |404 Not Found|catalog" /tmp/codex-deepseek-smoke.log; then
      echo "!! codex exec smoke test found a configuration problem:" >&2
      tail -15 /tmp/codex-deepseek-smoke.log >&2
      rm -rf "$TMPDIR_CHECK"
      exit 1
    else
      # Relay-side quota / overload / network hiccups are not install failures.
      echo "    ! codex exec smoke test inconclusive (relay-side, retried twice):"
      tail -3 /tmp/codex-deepseek-smoke.log | sed 's/^/      /'
    fi
    rm -rf "$TMPDIR_CHECK"
  else
    echo "    (codex CLI not on PATH, skipped the codex exec smoke test)"
  fi
fi

cat <<EOF

==> done

Next steps
  1. If the Codex desktop app is running, quit it completely and reopen it:
     it reads config.toml when the app-server process starts.
  2. Watch what Codex sends:   tail -f $ADIR/logs/adapter.log
     (each line shows model=, effort=, whether max_output_tokens was injected,
     and the capture=<file> reference of that exchange)
  3. Live web UI (real-time, grouped by question):
       http://127.0.0.1:$PORT/__ui
     In-flight requests stream token by token; history is folded into one parent
     per question (问题 + 时间 + 最终回复) with every request of that turn as a
     child row. Add ?expand=1 to open all groups. Loopback only and token-free;
     add \"ui_token\" to $ADIR/settings.json to require ?token=...
  4. Full request + model reply logs: $ADIR/logs/exchanges/<date>/
     one .json (everything) + one .txt (readable) per request. Browse them with
       $ADIR/captures.py            # table of the last 20
       $ADIR/captures.py --show 1   # the newest exchange in full
       $ADIR/captures.py --grep PAT # search all captured text
     Defaults: keep 7 days, <= 2 GiB, bodies capped at 8 MiB per exchange.
     They contain your prompts and the answers: treat them as transcripts.
  5. Revert any time: $SELF/uninstall.sh
EOF
