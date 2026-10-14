#!/usr/bin/env bash
# 停止后台进程（会同时清理 uv / pipe.py / server.py 子进程）
set -euo pipefail
cd "$(dirname "$0")"

PIDFILE=.dws-mcp.pid
if [ -f "$PIDFILE" ]; then
  PID="$(cat "$PIDFILE")"
  if kill -0 "$PID" 2>/dev/null; then
    kill "$PID" 2>/dev/null || true
    sleep 1
    kill -9 "$PID" 2>/dev/null || true
  fi
  rm -f "$PIDFILE"
fi

pkill -f "dws-xiaozhi-mcp/pipe.py" 2>/dev/null || true
pkill -f "dws-xiaozhi-mcp/server.py" 2>/dev/null || true
echo "已停止"
