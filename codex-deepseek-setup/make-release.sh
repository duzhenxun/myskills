#!/usr/bin/env bash
#
# Build a distributable archive of this folder.
#
#   ./make-release.sh                 # -> dist/codex-deepseek-setup.tgz (+ .zip)
#   ./make-release.sh --out DIR       # write somewhere else
#   ./make-release.sh --tgz-only      # skip the .zip
#
# Only the files listed in FILES ship: nothing else in this folder is read.
# That list is also a safety gate — keys.json / settings.json are created by
# install.sh on the target machine and must never end up in an archive.
set -euo pipefail

SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="codex-deepseek-setup"
OUT="$SELF/dist"
MAKE_ZIP=1

while [ $# -gt 0 ]; do
  case "$1" in
    --out) OUT="${2:-}"; shift 2 ;;
    --tgz-only) MAKE_ZIP=0; shift ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

# ---------------------------------------------------------------- what ships
FILES=(
  "install.sh"
  "uninstall.sh"
  "一键安装.command"
  "一键卸载.command"
  "README.md"
  "files/adapter.py"
  "files/captures.py"
  "files/models.json"
  "files/setup_config.py"
)

cd "$SELF"
for f in "${FILES[@]}"; do
  [ -f "$f" ] || { echo "error: missing $f" >&2; exit 1; }
done

PY="$(command -v python3 || true)"

STAGE="$(mktemp -d)"
VERIFY="$(mktemp -d)"
cleanup() { rm -rf "$STAGE" "$VERIFY"; }
trap cleanup EXIT

DEST="$STAGE/$NAME"
mkdir -p "$DEST/files"
for f in "${FILES[@]}"; do cp -p "$f" "$DEST/$f"; done

# ------------------------------------------------------- gate: no credentials
LEAKS="$(grep -rlE 'sk-[A-Za-z0-9_-]{16,}' "$DEST" 2>/dev/null || true)"
if [ -n "$LEAKS" ]; then
  echo "!! refusing to package: key-shaped string found in" >&2
  echo "$LEAKS" | sed 's/^/     /' >&2
  exit 1
fi
if [ -e "$DEST/files/keys.json" ] || [ -e "$DEST/files/settings.json" ]; then
  echo "!! refusing to package: keys.json / settings.json must not ship" >&2
  exit 1
fi

# ------------------------------------------------------------------- perms
chmod 755 "$DEST/install.sh" "$DEST/uninstall.sh" "$DEST"/*.command
chmod 644 "$DEST/README.md" "$DEST/files"/*

# ------------------------------------------------------------------- build
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"
TGZ="$OUT/$NAME.tgz"
ZIP="$OUT/$NAME.zip"
rm -f "$TGZ" "$ZIP"

# COPYFILE_DISABLE keeps macOS from adding ._* AppleDouble entries to the tar.
( cd "$STAGE" && COPYFILE_DISABLE=1 tar --exclude='.DS_Store' -czf "$TGZ" "$NAME" )

# Info-ZIP 3.0 (Apple's /usr/bin/zip) stores non-ASCII names without the UTF-8
# flag, which mangles 一键安装.command on Windows and older tools. Python's
# zipfile sets that flag, so build the zip with it and keep the exec bits.
if [ "$MAKE_ZIP" = "1" ] && [ -n "$PY" ]; then
  "$PY" - "$STAGE" "$NAME" "$ZIP" <<'PY'
import os, sys, zipfile

stage, name, out = sys.argv[1], sys.argv[2], sys.argv[3]
root = os.path.join(stage, name)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        rel = os.path.relpath(dirpath, stage)
        if rel != ".":
            arc = rel.replace(os.sep, "/") + "/"
            info = zipfile.ZipInfo(arc, (1980, 1, 1, 0, 0, 0))
            info.external_attr = (0o40755 << 16) | 0x10
            zf.writestr(info, b"")
        for fn in sorted(filenames):
            path = os.path.join(dirpath, fn)
            arc = os.path.relpath(path, stage).replace(os.sep, "/")
            info = zipfile.ZipInfo.from_file(path, arc)
            # writestr() with an explicit ZipInfo keeps that object's
            # compress_type (ZIP_STORED), so ask for deflate here.
            info.compress_type = zipfile.ZIP_DEFLATED
            with open(path, "rb") as fh:
                zf.writestr(info, fh.read())
PY
elif [ "$MAKE_ZIP" = "1" ] && command -v zip >/dev/null 2>&1; then
  ( cd "$STAGE" && zip -q -r -X "$ZIP" "$NAME" -x '*.DS_Store' )
else
  MAKE_ZIP=0
fi

# --------------------------------------------------- verify the archive works
tar xzf "$TGZ" -C "$VERIFY"
"$VERIFY/$NAME/install.sh" --help >/dev/null
for f in install.sh uninstall.sh "$NAME/一键安装.command" "$NAME/一键卸载.command"; do
  case "$f" in
    "$NAME"/*) bash -n "$VERIFY/$f" ;;
    *) bash -n "$VERIFY/$NAME/$f" ;;
  esac
done
if [ -n "$PY" ]; then
  "$PY" -m py_compile "$VERIFY/$NAME/files/adapter.py" \
                       "$VERIFY/$NAME/files/captures.py" \
                       "$VERIFY/$NAME/files/setup_config.py"
fi
[ -x "$VERIFY/$NAME/一键安装.command" ] || { echo "!! exec bit lost in archive" >&2; exit 1; }

# The zip is the one that silently breaks on Windows if the UTF-8 name flag is
# missing, so assert it here instead of finding out from a bug report.
if [ "$MAKE_ZIP" = "1" ] && [ -n "$PY" ]; then
  "$PY" - "$ZIP" <<'PY'
import sys, zipfile

zf = zipfile.ZipFile(sys.argv[1])
infos = zf.infolist()
bad = [i.filename for i in infos if not i.filename.isascii() and not i.flag_bits & 0x800]
if bad:
    raise SystemExit("!! zip entries without the UTF-8 flag: %s" % bad)
print("    zip: %d entries, non-ASCII names UTF-8 flagged" % len(infos))
PY
fi

# ------------------------------------------------------------------- report
sum() {
  if command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1"
  else sha256sum "$1"; fi
}

echo "==> built"
printf '    %s  (%s)\n' "$TGZ" "$(du -h "$TGZ" | cut -f1)"
[ "$MAKE_ZIP" = "1" ] && printf '    %s  (%s)\n' "$ZIP" "$(du -h "$ZIP" | cut -f1)"
echo "==> sha256"
sum "$TGZ" | sed 's/^/    /'
[ "$MAKE_ZIP" = "1" ] && sum "$ZIP" | sed 's/^/    /'

echo "==> contents"
tar tzf "$TGZ" | sed 's/^/    /'

cat <<EOF

==> how to hand this over

  receiver runs:   tar xzf $NAME.tgz && cd $NAME && open 一键安装.command

  If the file came through a browser / IM / AirDrop, macOS quarantines it and
  the first double-click is blocked ("Apple 无法检查…"). Tell them to
  right-click the .command file -> 打开 -> 打开, or run once:
      xattr -dr com.apple.quarantine .
EOF
