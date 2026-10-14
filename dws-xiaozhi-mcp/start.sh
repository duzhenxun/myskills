#!/usr/bin/env bash
# 后台常驻启动（nohup），日志写入 .dws-mcp.log
set -euo pipefail
cd "$(dirname "$0")"

PIDFILE=.dws-mcp.pid
LOGFILE=.dws-mcp.log

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "已在运行，PID=$(cat "$PIDFILE")"
  exit 0
fi

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

nohup uv run --python 3.12 pipe.py >>"$LOGFILE" 2>&1 &
echo $! >"$PIDFILE"
sleep 2
if kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "已启动，PID=$(cat "$PIDFILE")，日志：$(pwd)/$LOGFILE"
  tail -n 5 "$LOGFILE" || true
else
  echo "启动失败，请查看 $LOGFILE"
  exit 1
fi
