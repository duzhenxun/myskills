#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dws-xiaozhi-mcp / server.py

一个 stdio MCP Server，把本地 `dws` (DingTalk Workspace CLI) 的能力暴露给大模型。

设计要点（针对小智 AI 语音终端）：
1. 工具名 / 参数名用 ASCII（兼容大模型的 function calling 约束），
   描述用中文，便于小模型选对工具。
2. 每个工具调用都在超时预算内返回（小智服务端对 tool call 约 10s 超时）。
3. 写操作（发消息 / 建待办 / 建日程）自动补上 --yes。
4. 兜底工具 dws_run 默认只允许 read 类命令；write/destructive 需要显式 allow_write=true，
   风险等级通过 `dws schema` 动态判定（fail-closed）。

直接运行（stdio MCP）：
    uv run --python 3.12 server.py
"""

from __future__ import annotations

import asyncio
import json
import os
import shlex
import shutil
import sys

from mcp.server.fastmcp import FastMCP

# --------------------------------------------------------------------------
# 配置
# --------------------------------------------------------------------------

DWS_BIN = os.environ.get("DWS_BIN") or shutil.which("dws") or "dws"

# 单次 dws 调用总超时（秒）。小智默认 10s 超时，所以默认压到 9s。
TOOL_TIMEOUT = float(os.environ.get("DWS_TOOL_TIMEOUT", "9"))
# 传给 `dws --timeout` 的 HTTP 超时（秒），应小于上面的总超时。
HTTP_TIMEOUT = int(os.environ.get("DWS_HTTP_TIMEOUT", "8"))
# 返回给大模型的最大字符数，防止上下文被刷爆。
MAX_CHARS = int(os.environ.get("DWS_MAX_CHARS", "6000"))
# 组织 / 账号 profile（可选），对应 `dws --profile <corpId:userId>`
PROFILE = os.environ.get("DWS_PROFILE", "").strip()

mcp = FastMCP("dws")

# --------------------------------------------------------------------------
# 底层执行
# --------------------------------------------------------------------------

# 绝对禁止通过 MCP 触发的命令（登录态 / 自升级 / 本地配置）
_DENY_HEADS = {"auth", "upgrade", "config", "plugin", "profile", "completion", "dev"}
_DENY_LEAVES = {"logout", "reset", "migrate-keychain", "uninstall", "self-update"}


def _base_args(allow_write: bool) -> list[str]:
    args: list[str] = []
    if PROFILE:
        args += ["--profile", PROFILE]
    args += ["--timeout", str(HTTP_TIMEOUT)]
    if allow_write:
        args += ["--yes"]
    return args


def _truncate(text: str, limit: int = MAX_CHARS) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n…（输出过长，已截断，原长 {len(text)} 字符）"


def _norm_json(text: str) -> str:
    """把 JSON 文本压成单行紧凑形式（语音场景更省 token）。失败则原样返回。"""
    try:
        data = json.loads(text)
    except Exception:
        return text
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


async def _exec(
    tokens: list[str],
    *,
    allow_write: bool = False,
    timeout: float | None = None,
    as_json: bool = False,
) -> tuple[bool, str]:
    """执行一条 dws 命令（tokens 不含 dws 本身），返回 (ok, text)。

    一律使用 argv 数组调用（不经过 shell），stdin 关闭，避免交互式挂起。
    """
    head = tokens[0] if tokens else ""
    if head in _DENY_HEADS or (len(tokens) > 1 and tokens[1] in _DENY_LEAVES):
        return False, f"出于安全考虑，MCP 不允许直接调用 `dws {shlex.join(tokens)}`。"

    cmd = [DWS_BIN, *tokens]
    if as_json:
        cmd += ["--format", "json"]
    cmd += _base_args(allow_write)

    env = dict(os.environ)
    env.setdefault("NO_COLOR", "1")
    env["TERM"] = "dumb"

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
    except FileNotFoundError:
        return False, f"找不到 dws 可执行文件：{DWS_BIN}。请先安装 dws 并确保它在 PATH 中。"

    try:
        out_b, err_b = await asyncio.wait_for(proc.communicate(), timeout=timeout or TOOL_TIMEOUT)
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        await proc.wait()
        return False, (
            f"dws 命令在 {timeout or TOOL_TIMEOUT:.0f} 秒内没有返回（已终止）。"
            "可以缩小查询范围，或调大 DWS_TOOL_TIMEOUT。"
        )

    out = (out_b or b"").decode("utf-8", "replace").strip()
    err = (err_b or b"").decode("utf-8", "replace").strip()
    text = out or err

    if proc.returncode != 0:
        return False, f"dws 执行失败 (exit={proc.returncode}):\n{_truncate(text)}"

    return True, _truncate(text)


async def _run_json(tokens: list[str], *, allow_write: bool = False, timeout: float | None = None) -> tuple[bool, str]:
    ok, text = await _exec(tokens, allow_write=allow_write, timeout=timeout, as_json=True)
    return ok, _norm_json(text) if ok else text


def _find_event_id(text: str) -> str | None:
    """从 dws 返回的 JSON 里递归找 eventId。"""
    try:
        data = json.loads(text)
    except Exception:
        return None

    def walk(node):
        if isinstance(node, dict):
            for key, val in node.items():
                if isinstance(val, str) and key.lower() in ("eventid", "event_id", "id") and "event" in key.lower():
                    return val
                found = walk(val)
                if found:
                    return found
        elif isinstance(node, list):
            for item in node:
                found = walk(item)
                if found:
                    return found
        return None

    return walk(data)


async def _schema_effect(tokens: list[str]) -> str | None:
    """通过 `dws schema` 查询命令的 effect(read/write/destructive)，查不到返回 None。"""
    path: list[str] = []
    for t in tokens:
        if t.startswith("-"):
            break
        path.append(t)
        if len(path) >= 3:
            break
    while path:
        ok, text = await _exec(
            ["schema", "--cli-path", " ".join(path), "--compact", "--format", "json"],
            timeout=min(TOOL_TIMEOUT, 6),
        )
        if ok:
            try:
                effect = json.loads(text).get("effect")
                if effect:
                    return str(effect)
            except Exception:
                pass
        path.pop()
    return None


# --------------------------------------------------------------------------
# 读类工具
# --------------------------------------------------------------------------


@mcp.tool()
async def search_person(query: str, dimension: str = "all") -> str:
    """在钉钉通讯录里按 姓名/部门/职位/职责/上级/下级/手机号/工号 搜索同事，返回 userId 等信息。
    当用户问「XX 是谁」「XX 在哪个部门」「我的上级是谁」时使用。
    dimension 取值：all/name/department/position/duty/supervisor/subordinate/phone/jobNumber。"""
    return (await _run_json(["aisearch", "person", "--query", query, "--dimension", dimension or "all"]))[1]


@mcp.tool()
async def search_knowledge(query: str, types: str = "all", time_range: str = "") -> str:
    """搜索企业内部知识（文档/IM消息/日历/待办/会议纪要/日志/邮件等），用于回答公司内部业务问题。
    query 为关键词，多个用逗号分隔；types 取值 all/document/im/calendar/todo/minute/report/image/link；
    time_range 仅在用户明确说时间时填，如「今天」「本周」「9月」。"""
    args = ["aisearch", "enterprise", "--queries", query, "--types", types or "all"]
    if time_range:
        args += ["--time-range", time_range]
    return (await _run_json(args))[1]


@mcp.tool()
async def list_unread_chats(count: int = 15) -> str:
    """列出我有未读消息的钉钉会话（群聊/单聊）。当用户问「我有什么未读消息」「有没有新消息」时使用。"""
    return (await _run_json(["chat", "+unread-chats", "--count", str(max(1, min(int(count), 100)))]))[1]


@mcp.tool()
async def search_messages(query: str = "", group: str = "", sender: str = "", at_me: bool = False, days: int = 3, limit: int = 20) -> str:
    """按关键词/群名/发送人搜索钉钉聊天消息，也可以只查 @我的消息。
    例如「项目群里关于发布的讨论」「张三最近发的消息」「有没有人@我」。
    group 传群名，sender 传姓名，days 是回溯天数。"""
    args = ["chat", "+search-msg", "--days", str(max(1, min(int(days), 60))), "--limit", str(max(1, min(int(limit), 50)))]
    if query:
        args += ["--query", query]
    if group:
        args += ["--group", group]
    if sender:
        args += ["--senders", sender]
    if at_me:
        args += ["--at-me"]
    return (await _run_json(args))[1]


@mcp.tool()
async def list_my_groups(limit: int = 50) -> str:
    """列出我加入的钉钉群聊，返回群名和会话 ID。当用户问「我有哪些群」时使用。"""
    return (await _run_json(["chat", "+my-groups", "--limit", str(max(1, min(int(limit), 200)))]))[1]


@mcp.tool()
async def list_todos(due_today: bool = False, all_pages: bool = False) -> str:
    """查询我的钉钉待办列表。due_today=true 时只查今天到期的待办；all_pages=true 时拉取全部分页。
    当用户问「我有什么待办」「今天要做什么」时使用。"""
    if due_today:
        args = ["todo", "+due-today"]
    else:
        args = ["todo", "+get-my-tasks"]
        if all_pages:
            args += ["--all", "--max-pages", "5"]
    return (await _run_json(args))[1]


@mcp.tool()
async def query_schedule(when: str = "today") -> str:
    """查询我的钉钉日程。when 取值：today（今天）、tomorrow（明天）、week（本周）、next（接下来最近的一个日程）。
    当用户问「我今天有什么安排」「下一个会是什么」时使用。"""
    mapping = {
        "today": ["calendar", "+today"],
        "今天": ["calendar", "+today"],
        "tomorrow": ["calendar", "+tomorrow"],
        "明天": ["calendar", "+tomorrow"],
        "week": ["calendar", "+week"],
        "本周": ["calendar", "+week"],
        "next": ["calendar", "+next-event"],
        "next_event": ["calendar", "+next-event"],
    }
    args = mapping.get((when or "today").strip().lower(), ["calendar", "+today"])
    return (await _run_json(args))[1]


@mcp.tool()
async def get_my_profile() -> str:
    """获取当前登录用户的钉钉资料（姓名、userId、部门、邮箱、手机号）。当用户问「我是谁」「我的 userId」时使用。"""
    return (await _run_json(["contact", "user", "get-self"]))[1]


# --------------------------------------------------------------------------
# 写类工具（会自动加 --yes）
# --------------------------------------------------------------------------


@mcp.tool()
async def send_message(target: str, content: str, is_group: bool = False) -> str:
    """给某个人或某个群发送钉钉消息。target 填姓名或花名（群聊时填群名）；is_group=true 表示发到群。
    当用户说「给张三发消息说……」「在XX群里发……」「通知一下XX」时使用。"""
    if is_group:
        args = ["chat", "+send-to-group", "--group", target, "--content", content]
    else:
        args = ["chat", "+dm", "--to", target, "--content", content]
    ok, text = await _run_json(args, allow_write=True)
    return f"已发送给 {target}。{text}" if ok else text


@mcp.tool()
async def send_ding(target: str, content: str, ding_type: str = "app") -> str:
    """给指定人发 DING 强提醒消息。target 填姓名，多个用逗号分隔。
    ding_type 取值 app（应用内）、sms（短信）、call（电话）。仅在用户明确要求「DING 一下」时使用。"""
    args = ["ding", "+send-personal", "--users", target, "--content", content, "--type", ding_type or "app"]
    ok, text = await _run_json(args, allow_write=True)
    return f"已发出 DING 给 {target}。{text}" if ok else text


@mcp.tool()
async def create_todo(title: str, due: str = "", assignee: str = "") -> str:
    """创建一条钉钉待办。assignee 留空表示给自己建；填姓名（多个用逗号分隔）表示指派给别人。
    due 是截止时间，ISO8601 格式，如 2026-09-25T18:00:00+08:00，可为空。
    当用户说「提醒我做……」「记一个待办」「给张三派个任务」时使用。"""
    if assignee:
        args = ["todo", "+assign", "--to", assignee, "--task", title]
        if due:
            args += ["--due", due]
    else:
        args = ["todo", "+remind", "--task", title]
        if due:
            args += ["--at", due]
    ok, text = await _run_json(args, allow_write=True)
    return f"已创建待办：{title}。{text}" if ok else text


@mcp.tool()
async def complete_todo(title_keyword: str) -> str:
    """按标题关键词把我的一条钉钉待办标记为已完成。当用户说「XX 那件事做完了」「把 XX 待办关掉」时使用。"""
    ok, text = await _run_json(["todo", "+todo-done", "--task", title_keyword], allow_write=True)
    return f"已把待办「{title_keyword}」标记为完成。{text}" if ok else text


@mcp.tool()
async def create_event(title: str, start: str, end: str, attendees: str = "", location: str = "", description: str = "") -> str:
    """创建一个钉钉日程/会议，可邀请参会人（按姓名，逗号分隔）。
    start/end 用 ISO8601，如 2026-09-25T14:00:00+08:00。
    当用户说「帮我约个会」「安排明天下午三点和XX开会」时使用。"""
    args = ["calendar", "+book", "--title", title, "--start", start, "--end", end]
    if attendees:
        args += ["--with", attendees]
    ok, text = await _run_json(args, allow_write=True)
    if not ok:
        return text

    result = f"已创建日程：{title}（{start} ~ {end}）。{text}"
    if location or description:
        event_id = _find_event_id(text)
        if not event_id:
            return result + "（未能取到 eventId，地点/描述未写入）"
        upd = ["calendar", "+update", "--event", event_id, "--title", title, "--start", start, "--end", end]
        if location:
            upd += ["--location", location]
        if description:
            upd += ["--desc", description]
        ok2, text2 = await _run_json(upd, allow_write=True)
        result += ("" if ok2 else "（补充地点/描述失败）") + text2
    return result


# --------------------------------------------------------------------------
# 通用 / 发现类工具
# --------------------------------------------------------------------------


@mcp.tool()
async def dws_help(command_path: str = "") -> str:
    """查看 dws 命令的帮助。command_path 如 "chat"、"todo"、"calendar event"，留空则列出所有服务。
    当不确定某个 dws 能力怎么用时，先用这个工具查帮助，再用 dws_run 执行。"""
    tokens = shlex.split(command_path) if command_path.strip() else []
    ok, text = await _exec([*tokens, "--help"], timeout=min(TOOL_TIMEOUT, 8))
    if not ok:
        return text
    # 去掉重复的全局 flags 段落，省 token
    for marker in ("Global Flags:", "\nFlags:"):
        idx = text.find(marker)
        if idx > 200:
            text = text[:idx]
            break
    return _truncate(text, 3000)


@mcp.tool()
async def dws_run(command: str, allow_write: bool = False) -> str:
    """兜底工具：直接执行任意 dws 命令（不含开头的 dws 本身），
    例如 "chat +at-me --days 1"、"contact user get --ids xxx"。
    默认只允许只读(read)命令；如果命令是写/删除类（发消息、建群、删除等），
    必须先向用户确认，然后才能把 allow_write 设为 true。
    不确定参数写法时，先用 dws_help 查看。"""
    tokens = shlex.split(command)
    if not tokens:
        return "命令为空。"

    effect = await _schema_effect(tokens)
    if effect in ("write", "destructive") and not allow_write:
        return (
            f"`dws {command}` 属于 {effect} 操作，需要用户明确确认。"
            "请先向用户复述将要执行的操作，得到确认后把 allow_write 设为 true 再调用。"
        )
    if effect is None and not allow_write:
        return (
            f"无法确认 `dws {command}` 的安全等级，默认拒绝执行。"
            "请先用 dws_help 确认命令，或在用户确认后把 allow_write 设为 true。"
        )

    ok, text = await _run_json(tokens, allow_write=allow_write)
    return text


def main() -> None:
    if not (shutil.which(DWS_BIN) or os.path.exists(DWS_BIN)):
        print(f"[dws-mcp] 警告：找不到 dws 可执行文件（DWS_BIN={DWS_BIN}）", file=sys.stderr)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
