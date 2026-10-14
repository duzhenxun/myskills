#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pi-xiaozhi-mcp / pi_server.py

把本机的 **Pi coding agent** 通过 MCP 暴露给小智 AI。

为什么要有这个 server：
- `pi -p "..."` 冷启动一次要 12~22 秒，远超小智 tool call 的 ~10s 超时。
- 所以这里维持一个**常驻的 `pi --mode rpc` 子进程**（热进程），
  简单问答 ~2 秒返回；耗时任务则用「先返回、后查询」的异步任务模式。

工具：
  ask_pi      提交任务给 Pi（最多等 wait_seconds 秒，超时先返回“处理中”）
  check_pi    查询刚才那个任务的结果
  cancel_pi   中断当前任务
  pi_status   查看 Pi 进程状态
  reset_pi    重启 Pi 进程（清空对话上下文）

环境变量：
  PI_BIN             pi 可执行文件（默认自动探测）
  PI_MCP_CWD         Pi 的工作目录（默认启动目录）
  PI_MCP_PROVIDER    模型 provider（默认 nexita-anthropic）
  PI_MCP_MODEL       模型（默认 deepseek-v4.1-flash）
  PI_MCP_EXTRA_ARGS  追加给 pi 的参数
  PI_MCP_WAIT        默认最大等待秒数（默认 8，会被限制在 1~9）
  PI_MCP_MAX_CHARS   返回给大模型的最大字符数（默认 4000）
  PI_MCP_APPROVE     设为 1 时给 pi 传 --approve（信任项目内文件，默认不传）
"""

from __future__ import annotations

import asyncio
import atexit
import json
import os
import shlex
import shutil
import signal
import sys
import time
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# --------------------------------------------------------------------------
# 配置
# --------------------------------------------------------------------------

PI_BIN = os.environ.get("PI_BIN") or shutil.which("pi") or "pi"
PI_CWD = os.path.abspath(os.environ.get("PI_MCP_CWD") or os.getcwd())
PI_PROVIDER = os.environ.get("PI_MCP_PROVIDER", "nexita-anthropic").strip()
PI_MODEL = os.environ.get("PI_MCP_MODEL", "deepseek-v4.1-flash").strip()
PI_EXTRA_ARGS = shlex.split(os.environ.get("PI_MCP_EXTRA_ARGS", ""))
PI_MAX_WAIT = float(os.environ.get("PI_MCP_WAIT", "8"))
PI_MAX_CHARS = int(os.environ.get("PI_MCP_MAX_CHARS", "4000"))
PI_APPROVE = os.environ.get("PI_MCP_APPROVE", "").strip() in ("1", "true", "yes")


def _truncate(text: str, limit: int = PI_MAX_CHARS) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n…（内容过长，已截断，原长 {len(text)} 字符）"


# --------------------------------------------------------------------------
# 常驻 Pi RPC 进程管理
# --------------------------------------------------------------------------


class PiWorker:
    """维护一个常驻的 `pi --mode rpc` 子进程，串行执行任务。"""

    def __init__(self) -> None:
        self.proc: asyncio.subprocess.Process | None = None
        self.lock = asyncio.Lock()
        self.state = "stopped"  # stopped | idle | running
        self.answer: str | None = None
        self.error: str | None = None
        self.tools_used: list[str] = []
        self.started_at: float | None = None
        self.finished_at: float | None = None
        self.progress = ""
        self.last_stderr: list[str] = []
        self.session_info: dict[str, Any] = {}
        self._settled = asyncio.Event()
        self._responses: dict[str, Any] = {}
        self._reader: asyncio.Task | None = None
        self._err_reader: asyncio.Task | None = None
        self._start_lock = asyncio.Lock()

    # ---- 进程生命周期 ----

    def _build_env(self) -> dict[str, str]:
        env = dict(os.environ)
        # 避免把「当前这个 pi 会话」的状态带进子进程
        for key in ("PI_SESSION_FILE", "PI_SESSION_ID", "PI_PROVIDER", "PI_MODEL", "PI_REASONING_LEVEL"):
            env.pop(key, None)
        env["PI_OFFLINE"] = env.get("PI_OFFLINE", "1")
        return env

    def _build_cmd(self) -> list[str]:
        cmd = [PI_BIN, "--mode", "rpc", "--no-session"]
        if PI_PROVIDER:
            cmd += ["--provider", PI_PROVIDER]
        if PI_MODEL:
            cmd += ["--model", PI_MODEL]
        if PI_APPROVE:
            cmd.append("--approve")
        cmd += PI_EXTRA_ARGS
        return cmd

    async def ensure_started(self) -> None:
        if self.proc is not None and self.proc.returncode is None:
            return
        async with self._start_lock:
            if self.proc is not None and self.proc.returncode is None:
                return

            cmd = self._build_cmd()
            self.last_stderr = []
            self.proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=PI_CWD,
                env=self._build_env(),
            )
            self.state = "idle"
            self._settled.set()
            self._reader = asyncio.create_task(self._read_loop())
            self._err_reader = asyncio.create_task(self._stderr_loop())

            # 握手确认 RPC 循环已就绪
            ok = await self._request({"id": "__ready__", "type": "get_state"}, "__ready__", timeout=40)
            if ok is None:
                raise RuntimeError("Pi RPC 进程启动超时或已退出")

    async def _request(self, payload: dict, req_id: str, timeout: float) -> Any | None:
        if not self.proc or not self.proc.stdin:
            return None
        self.proc.stdin.write((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
        await self.proc.stdin.drain()
        deadline = time.time() + timeout
        while time.time() < deadline:
            if req_id in self._responses:
                return self._responses.pop(req_id)
            if self.proc.returncode is not None:
                return None
            await asyncio.sleep(0.05)
        return None

    async def _read_loop(self) -> None:
        assert self.proc and self.proc.stdout
        try:
            while True:
                line = await self.proc.stdout.readline()
                if not line:
                    break
                text = line.decode("utf-8", "replace").strip()
                if not text:
                    continue
                try:
                    event = json.loads(text)
                except json.JSONDecodeError:
                    continue
                self._handle_event(event)
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            pass
        finally:
            self.state = "stopped"
            if self.started_at and not self.finished_at:
                self.finished_at = time.time()
            self._settled.set()

    async def _stderr_loop(self) -> None:
        assert self.proc and self.proc.stderr
        try:
            while True:
                line = await self.proc.stderr.readline()
                if not line:
                    break
                text = line.decode("utf-8", "replace").rstrip()
                if text:
                    self.last_stderr.append(text)
                    del self.last_stderr[:-30]
                    print(f"[pi] {text}", file=sys.stderr, flush=True)
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            pass

    def _handle_event(self, event: dict) -> None:
        etype = event.get("type")

        if etype == "response":
            req_id = event.get("id")
            if req_id is not None:
                self._responses[str(req_id)] = event
            return

        if etype == "session":
            self.session_info = event
            return

        if etype == "message_end":
            message = event.get("message") or {}
            if message.get("role") != "assistant":
                return
            parts = message.get("content") or []
            text = "".join(
                p.get("text", "") for p in parts if isinstance(p, dict) and p.get("type") == "text"
            ).strip()
            if text:
                self.answer = text
            if message.get("errorMessage"):
                self.error = str(message.get("errorMessage"))
            elif message.get("stopReason") == "error":
                self.error = self.error or "模型返回错误"
            return

        if etype == "tool_execution_start":
            name = event.get("toolName") or "tool"
            self.tools_used.append(str(name))
            self.progress = f"正在调用 {name}"
            return

        if etype == "auto_retry_start":
            self.progress = "网络抖动，自动重试中"
            return

        if etype == "compaction_start":
            self.progress = "上下文压缩中"
            return

        if etype == "agent_settled":
            self.state = "idle"
            self.finished_at = time.time()
            self._settled.set()
            return

    # ---- 对外操作 ----

    async def start_task(self, prompt: str) -> tuple[bool, str]:
        await self.ensure_started()
        if self.state == "running":
            return False, self.progress_text()

        self.answer = None
        self.error = None
        self.tools_used = []
        self.started_at = time.time()
        self.finished_at = None
        self.progress = "思考中"
        self.state = "running"
        self._settled.clear()

        req_id = f"prompt-{int(time.time() * 1000)}"
        self.proc.stdin.write(  # type: ignore[union-attr]
            (json.dumps({"id": req_id, "type": "prompt", "message": prompt}, ensure_ascii=False) + "\n").encode("utf-8")
        )
        await self.proc.stdin.drain()  # type: ignore[union-attr]
        return True, "started"

    async def wait_done(self, seconds: float) -> bool:
        try:
            await asyncio.wait_for(self._settled.wait(), timeout=seconds)
            return True
        except asyncio.TimeoutError:
            return False

    def progress_text(self) -> str:
        elapsed = (time.time() - self.started_at) if self.started_at else 0
        parts = [f"Pi 运行中（已 {elapsed:.0f} 秒）", self.progress or "处理中"]
        if self.tools_used:
            recent = "、".join(dict.fromkeys(self.tools_used[-6:]))
            parts.append(f"已用工具：{recent}")
        if self.answer:
            parts.append(f"目前输出片段：{_truncate(self.answer, 300)}")
        return "；".join(parts)

    def result_text(self) -> str:
        if self.state == "running":
            return "【还在处理中】" + self.progress_text()
        if self.error and not self.answer:
            tail = "\n".join(self.last_stderr[-5:])
            return f"【执行失败】{self.error}" + (f"\n最近日志：\n{tail}" if tail else "")
        if not self.answer:
            return "【没有输出】Pi 没有返回任何内容。"
        text = f"【Pi 已完成】\n{self.answer}"
        if self.tools_used:
            text += "\n（本次用到的工具：" + "、".join(dict.fromkeys(self.tools_used)) + "）"
        return _truncate(text)

    async def abort(self) -> str:
        if self.state != "running":
            return "当前没有正在执行的任务。"
        if self.proc and self.proc.stdin:
            self.proc.stdin.write((json.dumps({"id": "abort-1", "type": "abort"}) + "\n").encode("utf-8"))
            await self.proc.stdin.drain()
        await self.wait_done(5)
        return "已请求中断当前任务。"

    async def reset(self) -> str:
        proc = self.proc
        self.proc = None
        for task in (self._reader, self._err_reader):
            if task:
                task.cancel()
        if proc and proc.returncode is None:
            try:
                proc.terminate()
                await asyncio.wait_for(proc.wait(), timeout=5)
            except Exception:  # noqa: BLE001
                try:
                    proc.kill()
                except Exception:  # noqa: BLE001
                    pass
        self.state = "stopped"
        self.answer = None
        self.error = None
        self.tools_used = []
        self.started_at = None
        self.finished_at = None
        self._settled.set()
        return "Pi 进程已重启，对话上下文已清空。"

    def status_text(self) -> str:
        alive = self.proc is not None and self.proc.returncode is None
        lines = [
            f"进程：{'运行中' if alive else '未启动'}（{self.state}）",
            f"工作目录：{PI_CWD}",
            f"模型：{PI_PROVIDER}/{PI_MODEL}",
        ]
        if self.state == "running":
            lines.append(self.progress_text())
        elif self.answer:
            lines.append("上一个任务：已完成")
        return "\n".join(lines)

    def kill(self) -> None:
        if self.proc and self.proc.returncode is None:
            try:
                self.proc.terminate()
            except Exception:  # noqa: BLE001
                pass


worker = PiWorker()


# --------------------------------------------------------------------------
# 启动时预热 Pi 进程：避免用户第一次说话时赶上冷启动（10s+）超时
# --------------------------------------------------------------------------


async def _prewarm() -> None:
    try:
        await asyncio.sleep(0.3)
        await worker.ensure_started()
        print("[pi-mcp] Pi RPC 预热完成", file=sys.stderr, flush=True)
    except asyncio.CancelledError:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"[pi-mcp] 预热失败（首次调用时会再试）：{exc}", file=sys.stderr, flush=True)


@asynccontextmanager
async def _lifespan(_server: FastMCP):
    warm = asyncio.create_task(_prewarm())
    try:
        yield {}
    finally:
        warm.cancel()
        _cleanup_worker()


mcp = FastMCP("pi", lifespan=_lifespan)


# --------------------------------------------------------------------------
# MCP 工具
# --------------------------------------------------------------------------


@mcp.tool()
async def ask_pi(prompt: str, wait_seconds: float = 8) -> str:
    """把任务交给本机的 Pi 编程智能体去执行。Pi 能读写本地文件、运行命令行、修改代码、联网查资料。
    适合：写或修改代码、跑脚本、查/整理本地文件、执行系统命令、抓网页、多步骤的自动化任务。
    不适合：单纯的闲聊、只有钉钉相关的问题（那用钉钉的工具）。

    Pi 执行通常要几十秒到几分钟。本工具最多等 wait_seconds 秒（上限 9 秒）：
    - 如果在这之内跑完，直接返回结果给你，你正常回答用户；
    - 如果超时，会返回「还在处理中」和任务进度，这时请告诉用户任务已经开始了，
      等用户再问「好了吗 / 结果出来了吗」的时候，你来调用 check_pi 取结果。
    同一个 Pi 进程会记住上下文，可以连续追问。"""
    seconds = max(1.0, min(float(wait_seconds or PI_MAX_WAIT), 9.0, PI_MAX_WAIT if PI_MAX_WAIT < 9 else 9.0))
    try:
        started, info = await worker.start_task(prompt)
    except Exception as exc:  # noqa: BLE001
        return f"【无法启动 Pi】{exc}。请检查 pi 是否安装、PI_MCP_CWD 是否存在、模型配置是否可用。"

    if not started:
        return f"【Pi 正在忙】{info}。你可以先告诉用户当前任务还在跑，或调用 cancel_pi 取消它。"

    done = await worker.wait_done(seconds)
    if done:
        return worker.result_text()

    elapsed = time.time() - (worker.started_at or time.time())
    return (
        f"【Pi 还在处理中】已运行 {elapsed:.0f} 秒，当前进度：{worker.progress}。\n"
        "请告诉用户任务已经开始执行了，稍后可以问他「好了吗」，你再用 check_pi 查结果。"
    )


@mcp.tool()
async def check_pi() -> str:
    """查询最近一次交给 Pi 的任务现在做到哪了、有没有结果。
    当用户问「刚才那个任务好了吗」「Pi 有结果了吗」时调用。"""
    return worker.result_text()


@mcp.tool()
async def cancel_pi() -> str:
    """中断 Pi 当前正在执行的任务。当用户说「停下来」「不用做了」「取消」时调用。"""
    return await worker.abort()


@mcp.tool()
async def pi_status() -> str:
    """查看本机 Pi 智能体的运行状态（进程、工作目录、模型、当前任务进度）。"""
    return worker.status_text()


@mcp.tool()
async def reset_pi() -> str:
    """重启 Pi 进程并清空对话上下文。当用户说「忘掉之前的」「重新开始」「换个话题」时调用。"""
    return await worker.reset()


# --------------------------------------------------------------------------
# 退出清理
# --------------------------------------------------------------------------


def _cleanup_worker() -> None:
    worker.kill()


def _handle_term(signum, frame) -> None:  # noqa: ANN001, ARG001
    _cleanup_worker()
    sys.exit(0)


def main() -> None:
    atexit.register(_cleanup_worker)
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, _handle_term)
        except (ValueError, OSError):
            pass

    if not (shutil.which(PI_BIN) or os.path.exists(PI_BIN)):
        print(f"[pi-mcp] 警告：找不到 pi 可执行文件（PI_BIN={PI_BIN}）", file=sys.stderr)
    print(
        f"[pi-mcp] cwd={PI_CWD} model={PI_PROVIDER}/{PI_MODEL} wait<={PI_MAX_WAIT}s",
        file=sys.stderr,
        flush=True,
    )
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
