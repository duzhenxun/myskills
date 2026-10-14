#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地自测：不经过小智，直接用 MCP stdio 调用 pi_server.py。

    uv run --python 3.12 test_pi.py            # 列工具 + 一个短问答
    uv run --python 3.12 test_pi.py --long     # 额外跑一个长任务，演示「先返回、后查询」
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.dirname(os.path.abspath(__file__))


def _text(res) -> str:
    return "".join(c.text for c in res.content if getattr(c, "type", "") == "text")


async def main(do_long: bool) -> None:
    params = StdioServerParameters(command=sys.executable, args=[os.path.join(HERE, "pi_server.py")])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"=== 已注册 {len(tools.tools)} 个工具 ===")
            for t in tools.tools:
                print(f"  - {t.name}: {(t.description or '').splitlines()[0]}")

            print("\n=== pi_status ===")
            print(_text(await session.call_tool("pi_status", {})))

            print("\n=== ask_pi（短问答）===")
            t0 = time.time()
            out = _text(await session.call_tool("ask_pi", {"prompt": "用一句话回答：你是什么模型？"}))
            print(f"[耗时 {time.time() - t0:.1f}s]\n{out[:800]}")

            if do_long:
                print("\n=== ask_pi（长任务，会先返回“处理中”）===")
                t0 = time.time()
                out = _text(
                    await session.call_tool(
                        "ask_pi",
                        {"prompt": "在当前目录下建一个 pi-mcp-test 文件夹，里面写一个 hello.txt 内容是 hello，然后告诉我完成了"},
                    )
                )
                print(f"[耗时 {time.time() - t0:.1f}s]\n{out[:800]}")

                for i in range(1, 7):
                    await asyncio.sleep(10)
                    out = _text(await session.call_tool("check_pi", {}))
                    print(f"\n=== check_pi #{i} ===\n{out[:600]}")
                    if "还在处理中" not in out:
                        break


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--long", action="store_true")
    asyncio.run(main(ap.parse_args().long))
