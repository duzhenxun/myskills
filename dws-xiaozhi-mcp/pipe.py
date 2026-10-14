#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dws-xiaozhi-mcp / pipe.py

把小智 AI 的 MCP 接入点 (WebSocket) 和本地 stdio MCP Server 桥接起来：

    小智设备/App  <->  小智云  <->  wss://api.xiaozhi.me/mcp/?token=...
                                        ^
                                        |  (本脚本作为 WebSocket 客户端连接)
                                        v
                                   pipe.py  <-- stdio JSON-RPC -->  server.py  <-->  dws CLI

用法：
    export MCP_ENDPOINT='wss://api.xiaozhi.me/mcp/?token=...'
    uv run --python 3.12 pipe.py

也可以把 endpoint 写在 .env 文件里（同目录），本脚本会自动加载。
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import signal
import subprocess
import sys

import websockets
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("dws-pipe")

INITIAL_BACKOFF = 1.0
MAX_BACKOFF = 60.0

# 本地 MCP server 启动命令
SERVER_CMD: list[str] = []


def _resolve_server_cmd() -> list[str]:
    override = os.environ.get("DWS_MCP_CMD", "").strip()
    if override:
        import shlex

        return shlex.split(override)
    # 默认：用当前 Python 启动同目录的 server.py
    here = os.path.dirname(os.path.abspath(__file__))
    return [sys.executable, os.path.join(here, "server.py")]


async def _pump_ws_to_proc(ws, proc: subprocess.Popen) -> None:
    """WebSocket -> 本地进程 stdin"""
    async for message in ws:
        if isinstance(message, (bytes, bytearray)):
            message = message.decode("utf-8", "replace")
        logger.debug("<< %s", message[:200])
        proc.stdin.write(message.rstrip("\n") + "\n")
        proc.stdin.flush()


async def _pump_proc_to_ws(proc: subprocess.Popen, ws) -> None:
    """本地进程 stdout -> WebSocket（逐行 JSON-RPC）"""
    while True:
        line = await asyncio.to_thread(proc.stdout.readline)
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        logger.debug(">> %s", line[:200])
        await ws.send(line)


async def _pump_stderr(proc: subprocess.Popen) -> None:
    while True:
        line = await asyncio.to_thread(proc.stderr.readline)
        if not line:
            break
        sys.stderr.write("[server] " + line)


async def _session(endpoint: str) -> None:
    """一次完整的连接会话：连上 WS -> 拉起 server.py -> 双向转发。"""
    logger.info("正在连接 MCP 接入点 ...")
    async with websockets.connect(
        endpoint,
        ping_interval=20,
        ping_timeout=20,
        open_timeout=30,
        close_timeout=10,
        max_size=None,
    ) as ws:
        logger.info("已连接 MCP 接入点，启动本地 MCP server：%s", " ".join(SERVER_CMD))
        env = dict(os.environ)
        env.setdefault("PYTHONUNBUFFERED", "1")
        proc = subprocess.Popen(
            SERVER_CMD,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=1,
            env=env,
        )
        try:
            await asyncio.gather(
                _pump_ws_to_proc(ws, proc),
                _pump_proc_to_ws(proc, ws),
                _pump_stderr(proc),
            )
        finally:
            logger.info("会话结束，关闭本地 MCP server")
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass


async def _main(endpoint: str) -> None:
    backoff = INITIAL_BACKOFF
    attempt = 0
    while True:
        try:
            await _session(endpoint)
            attempt = 0
            backoff = INITIAL_BACKOFF
            logger.info("连接已正常关闭，3 秒后重连 ...")
            await asyncio.sleep(3)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001
            attempt += 1
            logger.warning("连接断开（第 %d 次）：%s", attempt, exc)
            logger.info("%.0f 秒后重连 ...", backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, MAX_BACKOFF)


def main() -> None:
    global SERVER_CMD

    parser = argparse.ArgumentParser(description="小智 MCP 接入点 <-> 本地 dws MCP server 桥接")
    parser.add_argument("--endpoint", "-e", default=os.environ.get("MCP_ENDPOINT", ""), help="wss://api.xiaozhi.me/mcp/?token=...")
    parser.add_argument("--verbose", "-v", action="store_true", help="打印每条 JSON-RPC 报文")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if not args.endpoint:
        logger.error("缺少 MCP 接入点地址。请设置环境变量 MCP_ENDPOINT，或写入 .env 文件，或用 --endpoint 传入。")
        sys.exit(1)

    SERVER_CMD = _resolve_server_cmd()

    try:
        asyncio.run(_main(args.endpoint))
    except KeyboardInterrupt:
        logger.info("已退出")


if __name__ == "__main__":
    main()
