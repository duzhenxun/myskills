#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ -f .dws-mcp.pid ] && kill -0 "$(cat .dws-mcp.pid)" 2>/dev/null; then
  echo "运行中，PID=$(cat .dws-mcp.pid)"
else
  echo "未运行"
fi
echo "--- 最近日志 ---"
tail -n 20 .dws-mcp.log 2>/dev/null || echo "(暂无日志)"
