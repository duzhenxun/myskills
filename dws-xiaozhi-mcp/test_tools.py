#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地自测脚本：不经过小智，直接用 MCP stdio 协议调用 server.py 的工具。

    uv run --python 3.12 test_tools.py            # 只列工具 + 跑只读用例
    uv run --python 3.12 test_tools.py --write    # 额外跑一个写用例（真的发消息/建待办）
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.dirname(os.path.abspath(__file__))


async def main(include_write: bool) -> None:
    params = StdioServerParameters(command=sys.executable, args=[os.path.join(HERE, "server.py")])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"=== 已注册 {len(tools.tools)} 个工具 ===")
            for t in tools.tools:
                print(f"  - {t.name}: {(t.description or '').splitlines()[0]}")

            cases = [
                ("query_schedule", {"when": "today"}),
                ("list_unread_chats", {"count": 3}),
                ("list_todos", {"due_today": True}),
                ("get_my_profile", {}),
            ]
            for name, args in cases:
                print(f"\n=== 调用 {name} {args} ===")
                try:
                    res = await session.call_tool(name, args)
                    text = "".join(c.text for c in res.content if getattr(c, "type", "") == "text")
                    print(text[:1200])
                except Exception as exc:  # noqa: BLE001
                    print("调用失败:", exc)

            if include_write:
                print("\n=== 调用 dws_run（写操作，未授权，应被拒绝） ===")
                res = await session.call_tool("dws_run", {"command": "chat +dm --to 张三 --content 测试"})
                print("".join(c.text for c in res.content if getattr(c, "type", "") == "text")[:500])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    asyncio.run(main(ap.parse_args().write))
