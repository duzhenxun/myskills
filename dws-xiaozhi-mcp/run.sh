#!/usr/bin/env bash
# 启动 dws-xiaozhi-mcp：把本地 dws 能力接入小智 AI 的 MCP 接入点
set -euo pipefail
cd "$(dirname "$0")"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

exec uv run --python 3.12 pipe.py "$@"
