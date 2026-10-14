#!/usr/bin/env python3
"""Local adapter for the codeapi.nexita.net relay used by Codex.

Why this exists
---------------
The relay (LiteLLM-style) defaults Anthropic `max_tokens` to 4096 and derives
`thinking.budget_tokens` from the OpenAI `reasoning.effort` value:

    low / medium      -> budget <= 4096   (passes with the 4096 default)
    high              -> budget 8192      (needs max_tokens >= 12288)
    xhigh / max       -> budget 16384     (needs max_tokens >= 32768)

Anthropic rejects requests where max_tokens <= thinking.budget_tokens, so every
Codex request with effort >= high failed with:

    Invalid request body: max_tokens is less than thinking.budget_tokens

Codex never sends `max_output_tokens` on model requests (verified in the
0.154.0 binary and by capturing live requests), and its provider config has no
extra-body knob. So this adapter sits in front of the relay, adds
`max_output_tokens` when Codex omits it, and streams everything back unchanged.

It also routes the upstream credential by model name. Sessions created before
the DeepSeek switch recorded `model_provider = "OpenAI"` (870 of 908 rollout
files), and Codex keeps using a thread's recorded provider while taking the
model from the current config. Those requests therefore arrive with the
OpenAI key while asking for `deepseek-v4.1-flash`, and the relay answers:

    404 Model "deepseek-v4.1-flash" is not supported by any configured
    account in this group

The two keys have disjoint catalogs (open models vs OpenAI models), so the
adapter maps model -> key from keys.json. Without keys.json it is a pure
pass-through and credentials come from Codex.

What gets captured
------------------
Because this is the only place that sees the raw HTTP exchange, it can also
write each request from Codex and the full upstream response (including every
SSE event) to disk:

    logs/exchanges/<YYYY-MM-DD>/<HH-MM-SS>-<pid>-<seq>-<model>.json  full data
    logs/exchanges/<YYYY-MM-DD>/<HH-MM-SS>-<pid>-<seq>-<model>.txt   readable

Files are mode 600, directories 700. They contain your prompts and the model's
answers, so treat them like the transcripts they are. Disable with
CODEX_ADAPTER_CAPTURE=0, move them with CODEX_ADAPTER_CAPTURE_DIR, keep fewer
days with CODEX_ADAPTER_CAPTURE_KEEP_DAYS, cap the retained response bytes with
CODEX_ADAPTER_CAPTURE_MAX_BYTES. Capture never raises into the request path.
"""

import hashlib
import itertools
import json
import os
import queue
import re
import shutil
import socket
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = os.environ.get("CODEX_ADAPTER_UPSTREAM", "https://codeapi.nexita.net")
PORT = int(os.environ.get("CODEX_ADAPTER_PORT", "8899"))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 32768 > the 16384 budget used for xhigh/max, and a harmless cap otherwise.
MIN_MAX_OUTPUT_TOKENS = int(os.environ.get("CODEX_ADAPTER_MIN_MAX_OUTPUT_TOKENS", "32768"))
UPSTREAM_TIMEOUT = float(os.environ.get("CODEX_ADAPTER_TIMEOUT", "900"))
LOG_PATH = os.environ.get("CODEX_ADAPTER_LOG", os.path.join(BASE_DIR, "logs", "adapter.log"))
KEYS_PATH = os.environ.get("CODEX_ADAPTER_KEYS", os.path.join(BASE_DIR, "keys.json"))
SETTINGS_PATH = os.environ.get("CODEX_ADAPTER_SETTINGS", os.path.join(BASE_DIR, "settings.json"))
MAX_LOG_BYTES = 5 * 1024 * 1024


def _load_settings():
    """settings.json written by install.sh; env vars still win over it."""
    try:
        with open(SETTINGS_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


SETTINGS = _load_settings()

# Request/response capture (see the module docstring).
CAPTURE = str(os.environ.get("CODEX_ADAPTER_CAPTURE",
                             "1" if SETTINGS.get("capture", True) else "0")).lower() \
    not in ("0", "false", "no", "off")
CAPTURE_DIR = os.environ.get(
    "CODEX_ADAPTER_CAPTURE_DIR",
    SETTINGS.get("capture_dir") or os.path.join(BASE_DIR, "logs", "exchanges"))
CAPTURE_MAX_BYTES = int(os.environ.get(
    "CODEX_ADAPTER_CAPTURE_MAX_BYTES", str(SETTINGS.get("capture_max_bytes", 8 * 1024 * 1024))))
CAPTURE_KEEP_DAYS = int(os.environ.get(
    "CODEX_ADAPTER_CAPTURE_KEEP_DAYS", str(SETTINGS.get("capture_keep_days", 7))))
CAPTURE_MAX_TOTAL_BYTES = int(os.environ.get(
    "CODEX_ADAPTER_CAPTURE_MAX_TOTAL_BYTES",
    str(SETTINGS.get("capture_max_total_bytes", 2 * 1024 ** 3))))
CAPTURE_CLIP = int(os.environ.get("CODEX_ADAPTER_CAPTURE_CLIP", "8000"))

# Live web UI on the same loopback port: /__ui
UI = str(os.environ.get("CODEX_ADAPTER_UI", "1" if SETTINGS.get("ui", True) else "0")).lower() \
    not in ("0", "false", "no", "off")
UI_TOKEN = SETTINGS.get("ui_token") or ""
INDEX_PATH = os.path.join(CAPTURE_DIR, "index.jsonl")
GROUP_GAP_SECONDS = int(os.environ.get("CODEX_ADAPTER_GROUP_GAP_SECONDS", "7200"))
LIVE_MAX_CHARS = int(os.environ.get("CODEX_ADAPTER_LIVE_MAX_CHARS", "200000"))

# Models served by the open-model (Anthropic-converted) endpoint of the relay.
OPEN_MODEL_MARKERS = ("deepseek", "glm", "kimi", "moonshot", "z-ai")

HOP_BY_HOP = {
    "host", "content-length", "connection", "keep-alive", "proxy-authenticate",
    "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade",
    "accept-encoding",
}

_log_lock = threading.Lock()
_capture_lock = threading.Lock()
_capture_seq = itertools.count(1)

# Live fan-out: every subscriber gets every event, tagged with the exchange uid.
_subs_lock = threading.Lock()
_subs = []
_live_lock = threading.Lock()
_live = {}


def subscribe():
    q = queue.Queue(maxsize=2000)
    with _subs_lock:
        _subs.append(q)
    return q


def unsubscribe(q):
    with _subs_lock:
        if q in _subs:
            _subs.remove(q)


def publish(payload):
    with _subs_lock:
        targets = list(_subs)
    if not targets:
        return
    data = json.dumps(payload, ensure_ascii=False)
    for q in targets:
        try:
            q.put_nowait(data)
        except Exception:
            pass


def live_snapshot():
    with _live_lock:
        return [ex.snapshot() for ex in list(_live.values())]


def _index_append(entry):
    try:
        line = json.dumps(entry, ensure_ascii=False)
        fd = os.open(INDEX_PATH, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass


def index_entries(limit=40):
    """Newest-first summaries. Falls back to a filename listing if there is no index."""
    lines = []
    try:
        with open(INDEX_PATH, encoding="utf-8") as fh:
            lines = fh.readlines()
    except Exception:
        lines = []
    entries = []
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except Exception:
            continue
        if len(entries) >= limit:
            break
    if entries:
        return entries
    return _filename_entries(limit)


def _filename_entries(limit):
    found = []
    for root, _dirs, names in os.walk(CAPTURE_DIR):
        for name in names:
            if name.endswith(".json"):
                path = os.path.join(root, name)
                found.append((os.path.getmtime(path), os.path.relpath(path, CAPTURE_DIR)[:-5]))
    found.sort(reverse=True)
    return [{"file": rel, "started_at": time.strftime("%Y-%m-%dT%H:%M:%S",
                                                      time.localtime(mtime))}
            for mtime, rel in found[:limit]]


def rebuild_index(max_files=300):
    """One-off index build for captures taken before the index existed."""
    if not CAPTURE:
        return 0
    found = []
    for root, _dirs, names in os.walk(CAPTURE_DIR):
        for name in names:
            if name.endswith(".json"):
                path = os.path.join(root, name)
                found.append((os.path.getmtime(path), path))
    # Oldest first so the index stays append-only in time order (readers reverse it),
    # and only the newest max_files get indexed.
    found.sort()
    built = 0
    for _mtime, path in found[-max_files:]:
        try:
            with open(path, encoding="utf-8") as fh:
                record = json.load(fh)
        except Exception:
            continue
        request_doc = record.get("request")
        question, user_turns, ckey = conversation_key(request_doc)
        codex = _codex_meta(request_doc)
        derived = record.get("response") or {}
        _index_append({
            "file": os.path.relpath(path, CAPTURE_DIR)[:-5],
            "started_at": record.get("started_at"),
            "ended_at": record.get("ended_at"),
            "status": record.get("status"),
            "model": record.get("model"),
            "effort": _effort_of(record.get("adapter_note")),
            "ckey": ckey,
            "question": question[:600],
            "user_turns": user_turns,
            "thread": _thread_of(request_doc),
            "thread_id": codex["thread_id"],
            "turn_id": codex["turn_id"],
            "thread_source": codex["thread_source"],
            "turn_trigger": codex["turn_trigger"],
            "request_kind": codex["request_kind"],
            "subagent_kind": codex["subagent_kind"],
            "turn_started_ms": codex["turn_started_ms"],
            "message_id": _last_user_message_id(request_doc),
            "duration_ms": record.get("duration_ms"),
            "request_bytes": record.get("request_bytes"),
            "response_bytes": record.get("response_bytes"),
            "usage": derived.get("usage"),
            "text": (derived.get("text") or "")[:400],
            "tool_names": [c.get("name") for c in (derived.get("tool_calls") or [])],
            "error": record.get("error"),
        })
        built += 1
    return built


def index_needs_rebuild():
    """True when the index predates question/ckey (so grouping would be wrong)."""
    try:
        with open(INDEX_PATH, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if "ckey" not in data or "thread" not in data or "message_id" not in data:
                        return True
                except Exception:
                    return True
    except Exception:
        return False
    return False


def _effort_of(note):
    match = re.search(r"effort=(\S+)", note or "")
    return match.group(1) if match else "-"


def _thread_of(doc):
    """Codex sends the thread id as prompt_cache_key; it is stable per session."""
    if isinstance(doc, dict):
        value = doc.get("prompt_cache_key")
        if isinstance(value, str):
            return value
    return ""


CODEX_META_FIELDS = ("thread_id", "session_id", "turn_id", "root_turn_id", "parent_turn_id",
                     "request_kind", "thread_source", "turn_trigger", "subagent_kind", "agent_name")


def _codex_meta(doc):
    """Ids Codex puts in client_metadata: session, turn, and what triggered it.

    `thread_id` identifies the conversation, `turn_id` one user question (every
    request of that turn repeats it), `thread_source` says who asked (user /
    automation / guardian_review / memory_consolidation / system).
    """
    out = dict.fromkeys(CODEX_META_FIELDS, "")
    out["turn_started_ms"] = None
    if not isinstance(doc, dict):
        return out
    client = doc.get("client_metadata")
    if not isinstance(client, dict):
        return out
    for key in ("thread_id", "session_id", "turn_id", "root_turn_id", "parent_turn_id"):
        value = client.get(key)
        if isinstance(value, str):
            out[key] = value
    if client.get("x-openai-subagent") or client.get("x-codex-parent-thread-id"):
        out["subagent_kind"] = out["subagent_kind"] or str(client.get("x-openai-subagent") or "subagent")
    meta = client.get("x-codex-turn-metadata")
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except Exception:
            meta = None
    if isinstance(meta, dict):
        for key in CODEX_META_FIELDS:
            value = meta.get(key)
            if isinstance(value, str) and value:
                out[key] = value
        started = meta.get("turn_started_at_unix_ms")
        if isinstance(started, (int, float)):
            out["turn_started_ms"] = int(started)
    return out


INTERNAL_SOURCES = ("system", "memory_consolidation", "guardian_review", "thread_title")
SOURCE_LABELS = {"user": "你", "automation": "自动化", "guardian_review": "守卫审查",
                 "memory_consolidation": "记忆整理", "system": "系统", "thread_title": "会话标题",
                 "": "未知"}


def _ts_str(ms):
    if not isinstance(ms, (int, float)):
        return ""
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(ms / 1000.0))


def _last_user_message_id(doc):
    """Item id (msg_...) of the newest user message, when Codex sends one."""
    items = doc.get("input") if isinstance(doc, dict) else None
    if not isinstance(items, list):
        return ""
    found = ""
    for item in items:
        if isinstance(item, dict) and item.get("role") == "user" and isinstance(item.get("id"), str):
            found = item["id"]
    return found


SECRET_HEADER_NAMES = ("authorization", "proxy-authorization", "cookie", "set-cookie",
                       "x-api-key", "api-key", "openai-api-key", "x-goog-api-key")
SECRET_HEADER_HINTS = ("token", "secret", "password", "api-key")


def _mask(value):
    """Keep the shape of a credential but not its value: 'Bearer sk-...1cae'."""
    text = str(value)
    scheme, sep, token = text.partition(" ")
    if sep and token:
        tail = token[-4:] if len(token) > 4 else ""
        return "%s ****%s" % (scheme, tail)
    return "****" + (text[-4:] if len(text) > 4 else "")


def _redact_headers(headers):
    """Copy headers for storage, masking anything credential-like."""
    out = {}
    for key, value in (headers or {}).items():
        name = str(key).lower()
        if name in SECRET_HEADER_NAMES or any(hint in name for hint in SECRET_HEADER_HINTS):
            out[str(key)] = _mask(value)
        else:
            out[str(key)] = str(value)
    return out


def _message_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict):
                text = part.get("text") or part.get("input_text") or part.get("output_text")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts)
    return ""


def _looks_like_envelope(text):
    """Codex prepends machine context (AGENTS.md, environment) as user messages."""
    head = text.lstrip()[:40]
    return head.startswith("<") or head.startswith("# AGENTS.md") or head.startswith("# AGENTS.MD")


def conversation_key(doc):
    """(question, user message count, group key) for one request payload.

    Codex resends the whole conversation every request, so the newest user
    message identifies the question being worked on; the number of user messages
    keeps two identical questions in the same thread apart.
    """
    items = doc.get("input") if isinstance(doc, dict) else None
    question = ""
    count = 0
    if isinstance(items, str):
        question, count = items, 1
    elif isinstance(items, list):
        for item in items:
            if not isinstance(item, dict) or item.get("role") != "user":
                continue
            count += 1
            text = _message_text(item.get("content")).strip()
            if text and not _looks_like_envelope(text):
                question = text
    key = hashlib.sha1(("%s|%d" % (question, count)).encode("utf-8")).hexdigest()[:16]
    return question, count, (key if count else "")


def _is_internal(question, source="", request_kind=""):
    """Side jobs Codex runs through the same endpoint (titles, memory, review)."""
    if source in INTERNAL_SOURCES or (request_kind and request_kind != "turn"):
        return True
    head = (question or "").lstrip()
    return bool(re.match(r"^(Generate a concise|Summarize the|Write a concise|You are a summarizer)",
                         head))


def group_entries(entries, gap_seconds=None):
    """Fold a newest-first request list into question groups (newest first).

    Requests of one Codex turn share `prompt_cache_key` (the thread id) and the
    same number of user messages; every new question increments that count. The
    match is global rather than by adjacency, because a slow request can finish
    after a faster later one, which would otherwise split a turn in two. A run is
    also cut when the gap exceeds `gap_seconds`, so a repeated question in a
    recycled thread does not merge two different sessions.
    """
    gap_seconds = GROUP_GAP_SECONDS if gap_seconds is None else gap_seconds
    buckets = {}
    for entry in entries:
        thread_id = entry.get("thread_id") or ""
        turn_id = entry.get("turn_id") or ""
        thread = entry.get("thread") or ""
        count = entry.get("user_turns") or 0
        if thread_id and turn_id:
            key = "t:%s:%s" % (thread_id, turn_id)      # exact: one user question
        elif thread and count:
            key = "c:%s:%d" % (thread, count)            # fallback: thread + user messages
        else:
            key = entry.get("ckey") or ("solo:%s" % entry.get("file"))
        buckets.setdefault(key, []).append(entry)

    groups = []
    for key, reqs in buckets.items():
        reqs.sort(key=lambda r: r.get("started_at") or "")
        exact = key.startswith("t:")
        run = []
        for entry in reqs:
            if (not exact and run
                    and _gap_seconds(run[-1].get("started_at"), entry.get("started_at")) > gap_seconds):
                groups.append(_finish_group(key, run))
                run = []
            run.append(entry)
        if run:
            groups.append(_finish_group(key, run))
    groups.sort(key=lambda g: g.get("ended_at") or g.get("started_at") or "", reverse=True)
    return groups


def _ts(value):
    try:
        return time.mktime(time.strptime(value, "%Y-%m-%dT%H:%M:%S"))
    except Exception:
        return 0.0


def _gap_seconds(first, second):
    return abs(_ts(second or "") - _ts(first or ""))


def _finish_group(key, run):
    """run is oldest-first; return the parent record the UI renders."""
    newest, oldest = run[-1], run[0]
    questions = [r.get("question") for r in run if (r.get("question") or "").strip()]
    question = questions[-1] if questions else ""
    source = newest.get("thread_source") or ""
    inputs = [r["usage"].get("input_tokens") or 0 for r in run if isinstance(r.get("usage"), dict)]
    outputs = [r["usage"].get("output_tokens") or 0 for r in run if isinstance(r.get("usage"), dict)]
    final = next((r for r in reversed(run) if (r.get("text") or "").strip()), None)
    error = next((r.get("error") for r in run if r.get("error")), None)
    if not error and newest.get("status") not in (200, None):
        error = "HTTP %s" % newest.get("status")
    return {
        "key": key,
        "question": question,
        "internal": _is_internal(question, source, newest.get("request_kind") or ""),
        "source": source,
        "source_label": SOURCE_LABELS.get(source, source or "未知"),
        "trigger": newest.get("turn_trigger") or newest.get("request_kind") or "",
        "subagent_kind": newest.get("subagent_kind") or "",
        "thread_id": newest.get("thread_id") or "",
        "turn_id": newest.get("turn_id") or "",
        "message_id": (oldest.get("message_id") or ""),
        "started_at": _ts_str(newest.get("turn_started_ms")) or oldest.get("started_at"),
        "ended_at": newest.get("ended_at") or newest.get("started_at"),
        "count": len(run),
        "status": newest.get("status"),
        "model": newest.get("model"),
        "effort": newest.get("effort"),
        "thread": (newest.get("thread") or "")[:8],
        "duration_ms": sum(r.get("duration_ms") or 0 for r in run),
        "usage": {"input_tokens": max(inputs) if inputs else None,
                  "output_tokens": sum(outputs) if outputs else None},
        "final_text": (final or {}).get("text") or "",
        "final_file": (final or {}).get("file"),
        "tools": [n for r in run for n in (r.get("tool_names") or [])],
        "error": error,
        "requests": run,
    }


def load_keys():
    """Read the model -> key routing table. Missing/broken file = pass-through."""
    try:
        with open(KEYS_PATH, encoding="utf-8") as fh:
            cfg = json.load(fh)
        return cfg if isinstance(cfg, dict) else {}
    except Exception:
        return {}


def route_for(model):
    """Pick the upstream credential for a model.

    Returns (authorization_value or None, needs_max_output_tokens).
    """
    if not model:
        return None, False
    open_model = any(m in model.lower() for m in OPEN_MODEL_MARKERS)
    if open_model:
        key = KEYS.get("open_model_key")
        return ("Bearer " + key if key else None), True
    key = KEYS.get("openai_key")
    return ("Bearer " + key if key else None), False


def log(line):
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with _log_lock:
            if os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) > MAX_LOG_BYTES:
                os.replace(LOG_PATH, LOG_PATH + ".1")
            with open(LOG_PATH, "a", encoding="utf-8") as fh:
                fh.write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S"), line))
    except Exception:
        pass


def rewrite_body(path, body):
    """Route the credential and add max_output_tokens for Responses requests.

    Returns (body, authorization_header_or_None, note).
    """
    if "responses" not in path:
        return body, None, ""
    try:
        payload = json.loads(body)
    except Exception:
        return body, None, ""
    if not isinstance(payload, dict) or "input" not in payload:
        return body, None, ""

    model = payload.get("model")
    auth, inject = route_for(model if isinstance(model, str) else None)
    name = model if isinstance(model, str) else "-"

    effort = None
    reasoning = payload.get("reasoning")
    if isinstance(reasoning, dict):
        effort = reasoning.get("effort")

    if not inject:
        # OpenAI models are not converted to Anthropic by the relay: leave alone.
        return body, auth, "model=%s effort=%s (passthrough)" % (name, effort)

    current = payload.get("max_output_tokens")
    if not isinstance(current, int):
        current = 0
    if current >= MIN_MAX_OUTPUT_TOKENS:
        return body, auth, "model=%s effort=%s mt=%s (kept)" % (name, effort, current)

    payload["max_output_tokens"] = MIN_MAX_OUTPUT_TOKENS
    return json.dumps(payload, ensure_ascii=False).encode("utf-8"), auth, \
        "model=%s effort=%s mt=%s->%s" % (name, effort, current or "-", MIN_MAX_OUTPUT_TOKENS)


class Exchange(object):
    """One Codex request plus the upstream response, written to disk.

    Lands in <CAPTURE_DIR>/<YYYY-MM-DD>/<HH-MM-SS>-<pid>-<seq>-<model>.{json,txt}
    (mode 600, dir 700). Every method swallows its own errors: capture must
    never break a request.
    """

    def __init__(self, method, path, request_body, note, request_headers=None, auth_note=""):
        self.method = method
        self.path = path
        self.request_body = request_body
        self.note = note
        self.request_headers = _redact_headers(request_headers)
        self.auth_note = auth_note
        self.started = time.time()
        self.status = None
        self.headers = {}
        self.chunks = []
        self.kept = 0
        self.size = 0
        self.truncated = False
        self.error = None
        self.duration_ms = 0
        with _capture_lock:
            self.seq = next(_capture_seq)
        self.uid = "%d-%03d" % (os.getpid(), self.seq)
        self.model = None
        self.effort = None
        try:
            doc = json.loads(request_body) if request_body else None
        except Exception:
            doc = None
        if isinstance(doc, dict):
            self.model = doc.get("model")
            reasoning = doc.get("reasoning")
            if isinstance(reasoning, dict):
                self.effort = reasoning.get("effort")
        self.live_text = []
        self.live_reasoning = []
        self.live_tools = []
        self.live_usage = None
        self.live_chars = 0
        self._buf = b""
        self.question, self.user_turns, self.ckey = conversation_key(doc)
        self.thread = _thread_of(doc)
        self.codex = _codex_meta(doc)
        self.message_id = _last_user_message_id(doc)
        if UI:
            with _live_lock:
                _live[self.uid] = self
            publish({"event": "started", "uid": self.uid, "model": self.model,
                     "effort": self.effort, "path": self.path,
                     "question": self.question[:600], "ckey": self.ckey,
                     "started_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(self.started)),
                     "note": self.note})

    def snapshot(self):
        return {"event": "started", "uid": self.uid, "model": self.model, "effort": self.effort,
                "path": self.path, "note": self.note, "ckey": self.ckey,
                "question": self.question[:600],
                "started_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(self.started)),
                "elapsed_ms": int((time.time() - self.started) * 1000), "status": self.status,
                "text": "".join(self.live_text), "reasoning": "".join(self.live_reasoning),
                "tool_calls": self.live_tools, "usage": self.live_usage}

    def set_response(self, status, headers):
        self.status = status
        self.headers = {k.lower(): v for k, v in (headers or {}).items()}
        if UI:
            publish({"event": "status", "uid": self.uid, "status": status})

    def feed(self, chunk):
        self.size += len(chunk)
        if CAPTURE:
            if self.kept < CAPTURE_MAX_BYTES:
                self.chunks.append(chunk)
                self.kept += len(chunk)
            else:
                self.truncated = True
        if UI:
            self._publish_events(chunk)

    def _publish_events(self, chunk):
        """Parse complete SSE blocks and forward a compact live event for each."""
        self._buf += chunk
        while b"\n\n" in self._buf:
            block, self._buf = self._buf.split(b"\n\n", 1)
            for line in block.decode("utf-8", "replace").splitlines():
                line = line.strip()
                if not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if not payload or payload == "[DONE]":
                    continue
                try:
                    event = json.loads(payload)
                except Exception:
                    continue
                if isinstance(event, dict):
                    self._publish_live_event(event)

    def _publish_live_event(self, event):
        kind = event.get("type")
        out = {"event": "delta", "uid": self.uid, "kind": kind}
        if kind == "response.output_text.delta":
            delta = event.get("delta") or ""
            self.live_text.append(delta)
            self.live_chars += len(delta)
            out["text"] = delta
        elif kind in ("response.reasoning_summary_text.delta", "response.reasoning_text.delta"):
            delta = event.get("delta") or ""
            self.live_reasoning.append(delta)
            self.live_chars += len(delta)
            out["reasoning"] = delta
        elif kind == "response.function_call_arguments.done":
            out["tool_args"] = event.get("arguments")
        elif kind == "response.output_item.done":
            item = event.get("item") or {}
            if item.get("type") == "function_call":
                entry = {"name": item.get("name"), "arguments": item.get("arguments")}
                self.live_tools.append(entry)
                out["tool"] = entry
        elif kind == "response.completed":
            response = event.get("response") or {}
            self.live_usage = response.get("usage") or self.live_usage
            out["usage"] = self.live_usage
        elif kind in ("error", "response.failed"):
            out["error"] = event
        if self.live_chars > LIVE_MAX_CHARS:
            return
        publish(out)

    def finish(self, error=None):
        """Publish the live 'done' event and, when capturing, write both files."""
        if error and not self.error:
            self.error = error
        self.duration_ms = int((time.time() - self.started) * 1000)
        base = None
        if CAPTURE:
            try:
                base = self._write(error)
            except Exception:
                base = None
        if UI:
            try:
                with _live_lock:
                    _live.pop(self.uid, None)
                publish({"event": "done", "uid": self.uid, "status": self.status,
                         "model": self.model, "effort": self.effort, "file": base,
                         "duration_ms": self.duration_ms, "error": self.error,
                         "usage": self.live_usage, "bytes": self.size,
                         "text": "".join(self.live_text)[-4000:],
                         "tool_calls": self.live_tools})
            except Exception:
                pass
        return base

    def _write(self, error):
        raw = b"".join(self.chunks)
        content_type = self.headers.get("content-type", "")
        doc, events = _parse_events(raw, content_type)
        derived = _derive(doc, events)
        try:
            request_doc = json.loads(self.request_body) if self.request_body else None
        except Exception:
            request_doc = None
        model = request_doc.get("model") if isinstance(request_doc, dict) else None

        record = {
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(self.started)),
            "ended_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "duration_ms": int((time.time() - self.started) * 1000),
            "method": self.method,
            "path": self.path,
            "upstream": UPSTREAM.rstrip("/") + self.path,
            "status": self.status,
            "model": model,
            "adapter_note": self.note,
            "request_bytes": len(self.request_body or b""),
            "response_bytes": self.size,
            "response_content_type": content_type,
            "response_truncated": self.truncated,
            "error": error,
            "auth": self.auth_note,
            "request_headers": self.request_headers,
            "response_headers": self.headers,
            "codex": dict(self.codex, message_id=self.message_id,
                           source_label=SOURCE_LABELS.get(self.codex["thread_source"],
                                                          self.codex["thread_source"] or "未知")),
            "request": request_doc if request_doc is not None else {
                "_unparsed": _clip((self.request_body or b"").decode("utf-8", "replace"))},
            "response": {
                "text": derived["text"],
                "reasoning": derived["reasoning"],
                "tool_calls": derived["tool_calls"],
                "usage": derived["usage"],
                "errors": derived["errors"],
                "event_types": derived["event_types"],
                "events": events,
                "document": doc if events is None else None,
            },
        }

        with _capture_lock:
            seq = next(_capture_seq)
        day = time.strftime("%Y-%m-%d", time.localtime(self.started))
        base = "%s-%d-%03d-%s" % (time.strftime("%H-%M-%S", time.localtime(self.started)),
                                  os.getpid(), self.seq, _sanitize(model or "model"))
        day_dir = os.path.join(CAPTURE_DIR, day)
        _ensure_dir(day_dir)
        _write_file(os.path.join(day_dir, base + ".json"),
                    json.dumps(record, ensure_ascii=False, indent=2))
        _write_file(os.path.join(day_dir, base + ".txt"), self._render(record, derived, request_doc))
        _index_append({
            "file": "%s/%s" % (day, base),
            "started_at": record["started_at"],
            "ended_at": record["ended_at"],
            "status": record["status"],
            "model": model,
            "effort": self.effort,
            "ckey": self.ckey,
            "question": self.question[:600],
            "user_turns": self.user_turns,
            "thread": self.thread,
            "thread_id": self.codex["thread_id"],
            "turn_id": self.codex["turn_id"],
            "thread_source": self.codex["thread_source"],
            "turn_trigger": self.codex["turn_trigger"],
            "request_kind": self.codex["request_kind"],
            "subagent_kind": self.codex["subagent_kind"],
            "turn_started_ms": self.codex["turn_started_ms"],
            "message_id": self.message_id,
            "duration_ms": record["duration_ms"],
            "request_bytes": record["request_bytes"],
            "response_bytes": record["response_bytes"],
            "usage": derived["usage"],
            "text": (derived["text"] or "")[:400],
            "tool_names": [c.get("name") for c in derived["tool_calls"]],
            "error": error,
        })
        return "%s/%s" % (day, base)

    def _render(self, record, derived, request_doc):
        out = ["=" * 78,
               "%s  %s %s -> %s  (%d ms, %d B)" % (
                   record["started_at"], record["method"], record["path"], record["status"],
                   record["duration_ms"], record["response_bytes"]),
               "model   : %s" % (record["model"] or "-"),
               "note    : %s" % (self.note or "-"),
               "upstream: %s" % record["upstream"]]
        codex = record.get("codex") or {}
        if codex.get("thread_id") or codex.get("turn_id"):
            out.append("thread  : %s" % (codex.get("thread_id") or "-"))
            out.append("turn    : %s   (%s)" % (codex.get("turn_id") or "-",
                                                 codex.get("source_label") or "-"))
            if codex.get("message_id"):
                out.append("message : %s" % codex["message_id"])
            extra = [codex.get("request_kind"), codex.get("turn_trigger"), codex.get("subagent_kind")]
            extra = [e for e in extra if e]
            if extra:
                out.append("kind    : %s" % " / ".join(extra))
        if record.get("auth"):
            out.append("auth    : %s" % record["auth"])
        out.append("")
        out.append("--- REQUEST HEADERS ---")
        out += _render_headers(record.get("request_headers"),
                               "(none)" if not record.get("request_headers") else "")
        out.append("")
        out.append("--- RESPONSE HEADERS ---")
        out += _render_headers(record.get("response_headers"), "(none)")
        if record["error"]:
            out.append("error   : %s" % record["error"])
        out += ["=" * 78, "", "--- REQUEST (%d bytes) ---" % record["request_bytes"]]
        out += _render_request(request_doc)
        out += ["", "--- RESPONSE (%d bytes, %s) ---" % (
            record["response_bytes"], record["response_content_type"] or "-")]
        if derived["usage"]:
            out.append("usage: %s" % json.dumps(derived["usage"], ensure_ascii=False))
        if derived["errors"]:
            out.append("errors: %s" % json.dumps(derived["errors"], ensure_ascii=False)[:2000])
        if derived["reasoning"]:
            out.append("reasoning summary:")
            out += _indent(derived["reasoning"], "  ")
        for call in derived["tool_calls"]:
            out.append("tool_call: %s %s" % (call.get("name"), _clip(call.get("arguments") or "", 600)))
        if derived["text"]:
            out.append("text:")
            out += _indent(derived["text"], "  ")
        else:
            out.append("(no text in this response)")
        out.append("")
        if derived["event_types"]:
            out.append("event types: %s" % ", ".join(derived["event_types"]))
        out.append("raw request/response: the sibling .json file")
        return "\n".join(out) + "\n"


def _render_headers(headers, empty="", first=("authorization", "content-type", "user-agent")):
    """Render a header dict for the .txt view; credentials are already masked."""
    if not headers:
        return ["  %s" % empty] if empty else []
    names = list(headers)
    head = [n for key in first for n in names if key in n.lower()]
    rest = sorted(n for n in names if n not in head)
    return ["  %s: %s" % (name, _clip(headers[name], 400)) for name in head + rest]


def _ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path, mode=0o700, exist_ok=True)
    try:
        os.chmod(path, 0o700)
    except Exception:
        pass


def _write_file(path, text):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(text.encode("utf-8"))


def _sanitize(name):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", str(name))[:60] or "model"


def _clip(text, limit=None):
    if not isinstance(text, str):
        text = json.dumps(text, ensure_ascii=False)
    limit = limit or CAPTURE_CLIP
    if len(text) <= limit:
        return text
    return text[:limit] + "\n  ... (+%d chars, full text in the .json)" % (len(text) - limit)


def _indent(text, prefix="  "):
    if not isinstance(text, str):
        text = json.dumps(text, ensure_ascii=False)
    return [prefix + line for line in _clip(text).splitlines()] or [prefix]


def _parse_events(raw, content_type):
    """Return (single_document_or_None, [event objects]) for a response body."""
    text = raw.decode("utf-8", "replace")
    if "event-stream" in (content_type or ""):
        events = []
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if not payload or payload == "[DONE]":
                continue
            try:
                events.append(json.loads(payload))
            except Exception:
                pass
        return None, events
    try:
        return json.loads(text), None
    except Exception:
        return None, None


def _derive(doc, events):
    """Pull text / reasoning / tool calls / usage / errors out of a response."""
    out = {"text": "", "reasoning": "", "tool_calls": [], "usage": None,
           "errors": [], "event_types": []}
    if events is None:
        events = [doc] if isinstance(doc, dict) else []
    texts, reasons = [], []

    def from_message(item, target):
        for part in item.get("content") or []:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                target.append(part["text"])

    for ev in events:
        if not isinstance(ev, dict):
            continue
        kind = ev.get("type")
        if kind:
            out["event_types"].append(kind)
        if kind == "response.output_text.delta":
            texts.append(ev.get("delta") or "")
        elif kind in ("response.reasoning_summary_text.delta", "response.reasoning_text.delta"):
            reasons.append(ev.get("delta") or "")
        elif kind == "response.output_text.done" and not texts:
            texts.append(ev.get("text") or "")
        elif kind == "response.output_item.done":
            item = ev.get("item") or {}
            if item.get("type") == "function_call":
                out["tool_calls"].append({"name": item.get("name"),
                                         "arguments": item.get("arguments")})
            elif item.get("type") == "message" and not texts:
                # Only when no delta arrived, otherwise the text is duplicated.
                from_message(item, texts)
        elif kind in ("error", "response.failed"):
            out["errors"].append(ev)
        elif kind == "response.completed" and isinstance(ev.get("response"), dict):
            resp = ev["response"]
            out["usage"] = resp.get("usage") or out["usage"]
            for item in resp.get("output") or []:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "message" and not texts:
                    from_message(item, texts)
                elif item.get("type") == "function_call" and not out["tool_calls"]:
                    out["tool_calls"].append({"name": item.get("name"),
                                              "arguments": item.get("arguments")})

    if isinstance(doc, dict):
        out["usage"] = doc.get("usage") or out["usage"]
        if doc.get("error"):
            out["errors"].append(doc["error"])
        for item in doc.get("output") or []:
            if isinstance(item, dict) and item.get("type") == "message" and not texts:
                from_message(item, texts)

    out["text"] = "".join(texts)
    out["reasoning"] = "".join(reasons)
    return out


def _render_request(doc):
    """Human-readable rendering of the Responses payload Codex sent."""
    if not isinstance(doc, dict):
        return ["(request body is not JSON; raw text follows)"] + \
            _indent(doc if isinstance(doc, str) else json.dumps(doc, ensure_ascii=False))
    lines = []
    if doc.get("instructions"):
        lines.append("instructions:")
        lines += _indent(doc["instructions"])
    for key in ("model", "reasoning", "max_output_tokens", "stream", "store", "tool_choice",
                "parallel_tool_calls", "temperature", "top_p", "prompt_cache_key", "tools"):
        if key not in doc or key == "tools":
            continue
        lines.append("%s: %s" % (key, json.dumps(doc[key], ensure_ascii=False)))
    tools = [t for t in (doc.get("tools") or []) if isinstance(t, dict)]
    if tools:
        lines.append("tools (%d): %s" % (
            len(tools), ", ".join(str(t.get("name") or t.get("type") or "?") for t in tools)))
    items = doc.get("input")
    if isinstance(items, str):
        lines.append("input:")
        lines += _indent(items)
    elif isinstance(items, list):
        lines.append("input (%d items):" % len(items))
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                lines.append("  [%d] %s" % (i, _clip(item)))
                continue
            head = "  [%d] %s" % (i, item.get("type") or ("message" if item.get("role") else "?"))
            for key in ("role", "name", "call_id", "status"):
                if item.get(key):
                    head += " %s=%s" % (key, item[key])
            lines.append(head)
            content = item.get("content")
            if isinstance(content, str):
                lines += _indent(content, "      ")
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict):
                        lines.append("      (%s)" % (part.get("type") or "?"))
                        text = part.get("text")
                        if isinstance(text, str):
                            lines += _indent(text, "        ")
                        else:
                            lines += _indent(json.dumps(part, ensure_ascii=False), "        ")
                    else:
                        lines += _indent(part, "      ")
            for key in ("arguments", "output", "summary"):
                if item.get(key) not in (None, ""):
                    lines.append("      %s:" % key)
                    lines += _indent(item[key], "        ")
    return lines


def _dir_size(path):
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(root, name))
            except Exception:
                pass
    return total


def _dir_day(path, name):
    """Day directory key: parse the YYYY-MM-DD name, else fall back to mtime.

    Parsing the name (instead of trusting mtime) keeps retention predictable
    when directories are copied, restored or touched.
    """
    try:
        return time.mktime(time.strptime(name, "%Y-%m-%d"))
    except Exception:
        return os.path.getmtime(path)


def prune_captures():
    """Drop capture day directories older than CAPTURE_KEEP_DAYS, then the
    oldest ones until the whole tree fits in CAPTURE_MAX_TOTAL_BYTES."""
    if not CAPTURE:
        return 0
    try:
        days = sorted((_dir_day(os.path.join(CAPTURE_DIR, n), n), os.path.join(CAPTURE_DIR, n))
                      for n in os.listdir(CAPTURE_DIR)
                      if os.path.isdir(os.path.join(CAPTURE_DIR, n)))
    except Exception:
        return 0

    removed = 0
    if CAPTURE_KEEP_DAYS > 0:
        cutoff = time.time() - CAPTURE_KEEP_DAYS * 86400
        for key, path in [d for d in days]:
            if key < cutoff:
                shutil.rmtree(path, ignore_errors=True)
                days.remove((key, path))
                removed += 1

    if CAPTURE_MAX_TOTAL_BYTES > 0:
        sized = [(path, _dir_size(path)) for _key, path in days]
        total = sum(size for _path, size in sized)
        for path, size in sized:
            if total <= CAPTURE_MAX_TOTAL_BYTES:
                break
            shutil.rmtree(path, ignore_errors=True)
            total -= size
            removed += 1
    return removed


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "codex-deepseek-adapter/1.0"

    def log_message(self, *args):
        pass

    def _health(self):
        body = b"ok\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _finish_capture(self, ex, error=None):
        """Write the captured exchange; return a log fragment referencing it."""
        if ex is None:
            return ""
        base = ex.finish(error)
        return " capture=%s" % base if base else ""

    # ------------------------------------------------------------- live web UI
    def _send(self, status, payload, content_type):
        data = payload if isinstance(payload, bytes) else payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def _send_json(self, payload, status=200):
        self._send(status, json.dumps(payload, ensure_ascii=False), "application/json; charset=utf-8")

    def _send_text(self, text, status=200, content_type="text/plain; charset=utf-8"):
        self._send(status, text, content_type)

    def _query(self):
        return urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

    def _capture_file(self, name, suffix):
        """Resolve a capture name inside CAPTURE_DIR, refusing anything else."""
        if not name or not re.match(r"^[0-9A-Za-z._/-]+$", name) or ".." in name:
            return None
        path = os.path.abspath(os.path.join(CAPTURE_DIR, name + suffix))
        root = os.path.abspath(CAPTURE_DIR) + os.sep
        return path if path.startswith(root) and os.path.isfile(path) else None

    def _ui(self):
        path = urllib.parse.urlparse(self.path).path.rstrip("/") or "/__ui"
        query = self._query()
        if UI_TOKEN and query.get("token", [""])[0] != UI_TOKEN:
            return self._send_text("forbidden\n", 403)
        if self.command not in ("GET", "HEAD"):
            return self._send_text("method not allowed\n", 405)
        if path in ("/__ui", "/__ui/index.html"):
            return self._send_text(UI_HTML.replace("__TOKEN__", UI_TOKEN), 200,
                                   "text/html; charset=utf-8")
        if path == "/__ui/api/list":
            try:
                limit = max(1, min(2000, int(query.get("limit", ["200"])[0])))
            except ValueError:
                limit = 200
            entries = index_entries(limit)
            return self._send_json({"live": live_snapshot(), "recent": entries,
                                    "groups": group_entries(entries),
                                    "capture_dir": CAPTURE_DIR, "capture": CAPTURE})
        if path == "/__ui/api/live":
            return self._sse()
        if path == "/__ui/api/text":
            return self._capture_view(query, ".txt")
        if path == "/__ui/api/json":
            return self._capture_view(query, ".json")
        if path == "/__ui/api/answer":
            return self._capture_answer(query)
        return self._send_text("not found\n", 404)

    def _capture_answer(self, query):
        """Full final reply of one capture (the index only keeps a short preview)."""
        name = query.get("file", [""])[0]
        file_path = self._capture_file(name, ".json")
        if not file_path:
            return self._send_text("no such capture\n", 404)
        try:
            with open(file_path, encoding="utf-8") as fh:
                record = json.load(fh)
        except Exception as exc:
            return self._send_text("cannot read capture: %s\n" % exc, 500)
        response = record.get("response") or {}
        return self._send_json({
            "file": name,
            "text": response.get("text") or "",
            "reasoning": response.get("reasoning") or "",
            "tool_calls": response.get("tool_calls") or [],
            "usage": response.get("usage"),
            "model": record.get("model"),
            "effort": _effort_of(record.get("adapter_note")),
            "started_at": record.get("started_at"),
            "duration_ms": record.get("duration_ms"),
        })

    def _capture_view(self, query, suffix):
        file_path = self._capture_file(query.get("file", [""])[0], suffix)
        if not file_path:
            return self._send_text("no such capture\n", 404)
        with open(file_path, encoding="utf-8", errors="replace") as fh:
            payload = fh.read()
        return self._send_text(payload, 200, "text/plain; charset=utf-8")

    def _sse(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        q = subscribe()
        try:
            self.wfile.write(b": connected\n\n")
            for snap in live_snapshot():
                self.wfile.write(("data: %s\n\n" % json.dumps(snap, ensure_ascii=False)).encode("utf-8"))
            self.wfile.flush()
            while True:
                try:
                    item = q.get(timeout=15)
                except queue.Empty:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
                    continue
                self.wfile.write(("data: %s\n\n" % item).encode("utf-8"))
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            unsubscribe(q)
            self.close_connection = True

    def _proxy(self):
        if self.path.startswith("/__ui"):
            if not UI:
                return self._send_text("web UI disabled (settings.json: \"ui\": false)\n", 404)
            return self._ui()
        if self.path.rstrip("/") in ("/__health", "/healthz"):
            return self._health()
        if self.path.rstrip("/") == "/favicon.ico":
            # Browser noise: never forward upstream and never capture it.
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        length = int(self.headers.get("content-length") or 0)
        body = self.rfile.read(length) if length else None
        note = ""
        auth = None
        if body:
            body, auth, note = rewrite_body(self.path, body)
        # Only model traffic is worth capturing/live-streaming.
        interesting = "responses" in self.path
        if auth:
            auth_note = "adapter injected %s (keys.json)" % _mask(auth)
        elif self.headers.get("Authorization"):
            auth_note = "caller credential forwarded (%s)" % _mask(self.headers.get("Authorization"))
        else:
            auth_note = "none"
        ex = Exchange(self.command, self.path, body, note, dict(self.headers), auth_note) \
            if (CAPTURE or UI) and interesting else None

        headers = {k: v for k, v in self.headers.items() if k.lower() not in HOP_BY_HOP}
        if auth:
            headers["Authorization"] = auth
        headers["Accept-Encoding"] = "identity"
        if body is not None:
            headers["Content-Length"] = str(len(body))

        url = UPSTREAM.rstrip("/") + self.path
        req = urllib.request.Request(url, data=body, method=self.command, headers=headers)
        started = time.time()
        try:
            resp = urllib.request.urlopen(req, timeout=UPSTREAM_TIMEOUT)
        except urllib.error.HTTPError as exc:
            data = exc.read()
            if ex:
                ex.set_response(exc.code, dict(exc.headers))
                ex.feed(data)
            log("%s %s -> %s %s %s%s" % (
                self.command, self.path, exc.code, note, _tail(data),
                self._finish_capture(ex, "upstream HTTP %s" % exc.code)))
            self.send_response(exc.code)
            for k, v in exc.headers.items():
                if k.lower() not in HOP_BY_HOP:
                    self.send_header(k, v)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(data)
            return
        except Exception as exc:
            log("%s %s -> 502 %s (%s)%s" % (
                self.command, self.path, note, exc, self._finish_capture(ex, "upstream error: %s" % exc)))
            data = json.dumps({"error": {"type": "upstream_error", "message": str(exc)}}).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        status = resp.status
        if ex:
            ex.set_response(status, dict(resp.headers))
        self.send_response(status)
        for k, v in resp.headers.items():
            if k.lower() not in HOP_BY_HOP:
                self.send_header(k, v)
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()
        total = 0
        try:
            while True:
                chunk = resp.read(32768)
                if not chunk:
                    break
                total += len(chunk)
                if ex:
                    ex.feed(chunk)
                self.wfile.write(b"%X\r\n" % len(chunk) + chunk + b"\r\n")
                self.wfile.flush()
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            log("%s %s -> %s client-disconnect after %d bytes%s" % (
                self.command, self.path, status, total,
                self._finish_capture(ex, "client disconnected")))
            self.close_connection = True
            return
        log("%s %s -> %s %s %dB %.1fs%s" % (
            self.command, self.path, status, note or "-", total, time.time() - started,
            self._finish_capture(ex)))

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_HEAD = do_OPTIONS = _proxy


def _tail(data, limit=160):
    try:
        return data[:limit].decode("utf-8", "replace").replace("\n", " ")
    except Exception:
        return ""


UI_HTML = r"""<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<title>Codex ⇄ DeepSeek 实时日志</title>
<script>
// Set the theme before the body renders so there is no flash.
try {
  var m = new URLSearchParams(location.search).get("theme") || localStorage.getItem("codex-deepseek-theme") || "auto";
  if (m === "auto") m = matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  document.documentElement.dataset.theme = m;
} catch (e) {}
</script>
<style>
  :root { color-scheme: dark;
          --bg:#0f1115; --panel:#171a21; --line:#262b36; --fg:#d8dee9; --dim:#8b94a5;
          --ok:#3ddc97; --warn:#ffb454; --bad:#ff6b6b; --acc:#6ea8fe;
          --head:rgba(15,17,21,.94); --hover:#1c202a; --sub:#12151b; --line2:#1b1f28;
          --code:#0b0d11; --codebg:#1b2029; --btn:#222836; --faint:#5f6878;
          --overlay:rgba(0,0,0,.72); --open:#33405a;
          --srcuser:#9ecbff; --srcuserline:#33507a; --srcautoline:#5a4a2a; }
  [data-theme="light"] { color-scheme: light;
          --bg:#f6f7f9; --panel:#ffffff; --line:#dde1e8; --fg:#1f2430; --dim:#667085;
          --ok:#0b8a4b; --warn:#a35b00; --bad:#d92d20; --acc:#1d4ed8;
          --head:rgba(246,247,249,.94); --hover:#eef1f6; --sub:#f4f6fa; --line2:#e8ecf2;
          --code:#f7f9fc; --codebg:#eef1f6; --btn:#eef1f6; --faint:#98a2b3;
          --overlay:rgba(15,23,42,.45); --open:#9db4e0;
          --srcuser:#1d4ed8; --srcuserline:#b9caf5; --srcautoline:#f0cf9a; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--fg);
         font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif; }
  header { display:flex; align-items:center; gap:12px; padding:12px 18px; border-bottom:1px solid var(--line);
           position:sticky; top:0; background:var(--head); backdrop-filter:blur(6px); z-index:5; }
  .themebox { display:flex; border:1px solid var(--line); border-radius:8px; overflow:hidden; }
  .themebox button { border:0; border-radius:0; background:transparent; color:var(--dim);
                     padding:4px 10px; font-size:12px; cursor:pointer; }
  .themebox button.on { background:var(--btn); color:var(--fg); }
  header h1 { font-size:15px; margin:0; font-weight:600; }
  header .sp { flex:1; }
  .pill { font-size:12px; padding:2px 8px; border:1px solid var(--line); border-radius:999px; color:var(--dim); }
  .dot { width:8px; height:8px; border-radius:50%; background:var(--bad); display:inline-block; }
  .dot.on { background:var(--ok); }
  main { padding:18px; max-width:1500px; margin:0 auto; }
  h2 { font-size:13px; text-transform:uppercase; letter-spacing:.08em; color:var(--dim);
       margin:22px 0 10px; font-weight:600; }
  h2:first-child { margin-top:0; }
  .card { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:12px 14px; margin-bottom:12px; }
  .card .top { display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:8px; }
  .model { font-weight:600; }
  .meta { color:var(--dim); font-size:12px; }
  .badge { font-size:11px; padding:1px 7px; border-radius:999px; border:1px solid var(--line); }
  .badge.run { color:var(--acc); border-color:var(--acc); }
  .badge.ok { color:var(--ok); border-color:var(--ok); }
  .badge.bad { color:var(--bad); border-color:var(--bad); }
  pre { margin:6px 0 0; padding:10px 12px; background:var(--code); border:1px solid var(--line);
        border-radius:8px; max-height:340px; overflow:auto; white-space:pre-wrap; word-break:break-word;
        font:12.5px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace; }
  details summary { cursor:pointer; color:var(--dim); font-size:12px; margin-top:8px; }
  .tools { margin-top:8px; font:12.5px/1.5 ui-monospace,Menlo,monospace; color:var(--warn); }
  .q { margin-top:6px; color:var(--fg); font-size:13px; white-space:pre-wrap; word-break:break-word; }
  .answer { margin-top:8px; padding:10px 12px; background:var(--code); border:1px solid var(--line);
            border-radius:8px; max-height:420px; overflow:auto; font-size:13px; line-height:1.6; }
  .answer p { margin:0 0 8px; }
  .answer p:last-child { margin-bottom:0; }
  .answer ul, .answer ol { margin:0 0 8px; padding-left:22px; }
  .answer .mdh { font-weight:600; margin:10px 0 6px; }
  .answer code { background:var(--codebg); padding:1px 5px; border-radius:4px;
                 font:12px/1.5 ui-monospace,Menlo,monospace; }
  .answer pre.mdc { background:var(--code); border:1px solid var(--line); border-radius:6px; padding:8px 10px;
                    overflow:auto; font:12px/1.55 ui-monospace,Menlo,monospace; white-space:pre; }
  .answer table.mdt { border-collapse:collapse; margin:4px 0 10px; font-size:12.5px; }
  .answer table.mdt th, .answer table.mdt td { border:1px solid var(--line); padding:4px 9px; white-space:nowrap; }
  .answer table.mdt th { background:var(--codebg); color:var(--dim); }
  .hint { color:var(--faint); font-size:11.5px; margin-top:4px; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  th, td { text-align:left; padding:7px 10px; border-bottom:1px solid var(--line); white-space:nowrap; }
  th { color:var(--dim); font-weight:600; font-size:12px; position:sticky; top:57px; background:var(--bg); }
  tbody tr { cursor:pointer; }
  tbody tr:hover { background:var(--hover); }
  td.preview { white-space:normal; color:var(--dim); max-width:560px; }
  input[type=search] { background:var(--code); border:1px solid var(--line); color:var(--fg);
        border-radius:8px; padding:5px 9px; font-size:13px; }
  label.chk { color:var(--dim); font-size:12px; display:flex; align-items:center; gap:5px; }
  #modal { position:fixed; inset:0; background:var(--overlay); display:none; z-index:20; padding:3vh 3vw; }
  #modal.on { display:block; }
  #modal .box { background:var(--panel); border:1px solid var(--line); border-radius:12px; height:94%; display:flex; flex-direction:column; }
  #modal .bar { display:flex; align-items:center; gap:10px; padding:10px 14px; border-bottom:1px solid var(--line); }
  #modal pre { flex:1; max-height:none; margin:0; border:0; border-radius:0 0 12px 12px; }
  button { background:var(--btn); color:var(--fg); border:1px solid var(--line); border-radius:8px;
           padding:5px 11px; cursor:pointer; font-size:13px; }
  a { color:var(--acc); text-decoration:none; }
  .empty { color:var(--dim); padding:10px 2px; font-size:13px; }
  .grp { background:var(--panel); border:1px solid var(--line); border-radius:10px; margin-bottom:10px; overflow:hidden; }
  .grp.open { border-color:var(--open); }
  .gq-head { display:flex; align-items:flex-start; gap:10px; padding:11px 14px; cursor:pointer; }
  .gq-head:hover { background:var(--hover); }
  .caret { color:var(--dim); font-size:12px; padding-top:2px; width:10px; }
  .gq-body { flex:1; min-width:0; }
  .gq-text { font-weight:600; font-size:14px; white-space:pre-wrap; word-break:break-word;
             display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }
  .grp.open .gq-text { -webkit-line-clamp:unset; }
  .gq-final { color:var(--dim); font-size:12.5px; margin-top:5px; white-space:pre-wrap; word-break:break-word;
              display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
  .grp.open .gq-final { -webkit-line-clamp:unset; }
  .answer code { background:var(--codebg); padding:1px 5px; border-radius:4px; }
  .gq-meta { text-align:right; color:var(--dim); font-size:12px; white-space:nowrap; }
  .gq-meta .big { color:var(--fg); font-size:12.5px; }
  .kids { border-top:1px solid var(--line); background:var(--sub); padding:2px 0; }
  .kids.hidden { display:none; }
  .src { font-size:11px; padding:1px 7px; border-radius:999px; border:1px solid var(--line); color:var(--dim); }
  .src.user { color:var(--srcuser); border-color:var(--srcuserline); }
  .src.automation { color:var(--warn); border-color:var(--srcautoline); }
  .ids { color:var(--faint); font-size:11px; }
  .kids .req { display:flex; gap:12px; padding:7px 14px 7px 26px; font-size:12.5px;
               border-bottom:1px solid var(--line2); cursor:pointer; align-items:baseline;
               white-space:nowrap; }
  .kids .req:last-child { border-bottom:0; }
  .kids .req:hover { background:var(--hover); }
  .kids .req .idx { color:var(--dim); width:26px; }
  .kids .req .t { width:74px; color:var(--dim); }
  .kids .req .st { width:38px; }
  .kids .req .mdl { width:196px; color:var(--dim); overflow:hidden; text-overflow:ellipsis; }
  .kids .req .num { width:104px; color:var(--dim); }
  .kids .req .prev { flex:1; min-width:0; color:var(--dim); overflow:hidden; text-overflow:ellipsis; }
  .kids .req .go { color:var(--acc); white-space:nowrap; }
  .kids .hdr { display:flex; gap:12px; padding:5px 14px 5px 26px; font-size:11.5px; color:var(--faint);
               border-bottom:1px solid var(--line2); text-transform:uppercase; letter-spacing:.04em; }
  .kids .hdr .idx { width:26px; } .kids .hdr .t { width:74px; } .kids .hdr .st { width:38px; }
  .kids .hdr .mdl { width:196px; } .kids .hdr .num { width:104px; } .kids .hdr .prev { flex:1; }
</style>
</head>
<body>
<header>
  <span class="dot" id="dot"></span>
  <h1>Codex ⇄ DeepSeek 实时日志</h1>
  <span class="pill" id="where"></span>
  <span class="sp"></span>
  <span class="meta" id="stats"></span>
  <div class="themebox" id="themebox">
    <button data-theme="auto" title="跟随系统">自动</button>
    <button data-theme="dark" title="暗色">暗</button>
    <button data-theme="light" title="亮色">亮</button>
  </div>
</header>
<main>
  <h2>进行中 <span class="meta" id="livecount"></span></h2>
  <div id="live"><div class="empty">暂无请求。在 Codex 里发一句话，这里会实时出现。</div></div>

  <h2>历史 <span class="meta" id="gcount"></span></h2>
  <div style="display:flex; gap:12px; align-items:center; margin-bottom:10px">
    <input type="search" id="filter" placeholder="搜索 问题 / 回复 / 模型 / 时间 …" style="flex:1">
    <label class="chk"><input type="checkbox" id="onlyErr"> 只看失败</label>
    <label class="chk"><input type="checkbox" id="showInternal"> 显示内部请求（标题/记忆/审查等）</label>
    <button id="expand">展开全部</button>
    <button id="reload">刷新</button>
  </div>
  <div id="groups"></div>
  <div class="empty" id="noRows" style="display:none">没有匹配的记录。</div>
</main>

<div id="modal"><div class="box">
  <div class="bar"><strong id="mtitle"></strong><span class="sp" style="flex:1"></span>
    <a id="mraw" target="_blank" rel="noreferrer">原始 JSON</a>
    <button id="mclose">关闭 (Esc)</button></div>
  <pre id="mbody"></pre>
</div></div>

<script>
const TOKEN = "__TOKEN__";

// ---- 主题：自动 / 暗 / 亮（选择存在 localStorage，?theme= 可临时覆盖） ----
const THEME_KEY = "codex-deepseek-theme";
const prefersLight = window.matchMedia("(prefers-color-scheme: light)");
function currentThemeChoice() {
  try { return localStorage.getItem(THEME_KEY) || "auto"; } catch (e) { return "auto"; }
}
function applyTheme(mode, persist) {
  const resolved = mode === "auto" ? (prefersLight.matches ? "light" : "dark") : mode;
  document.documentElement.dataset.theme = resolved;
  document.querySelectorAll("#themebox button").forEach(b => b.classList.toggle("on", b.dataset.theme === mode));
  if (persist) { try { localStorage.setItem(THEME_KEY, mode); } catch (e) {} }
}
(function initTheme() {
  const fromUrl = new URLSearchParams(location.search).get("theme");
  applyTheme(fromUrl || currentThemeChoice(), false);
  document.querySelectorAll("#themebox button").forEach(b => {
    b.onclick = () => applyTheme(b.dataset.theme, true);
  });
  prefersLight.addEventListener("change", () => { if (currentThemeChoice() === "auto") applyTheme("auto", false); });
})();
const url = (p) => p + (TOKEN ? (p.includes("?") ? "&" : "?") + "token=" + encodeURIComponent(TOKEN) : "");
const esc = (s) => String(s == null ? "" : s).replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
const fmtBytes = (n) => n == null ? "-" : (n < 1024 ? n + " B" : (n / 1024 < 1024 ? (n / 1024).toFixed(1) + " K" : (n / 1048576).toFixed(1) + " M"));
const fmtMs = (n) => n == null ? "-" : (n < 1000 ? n + " ms" : (n / 1000).toFixed(1) + " s");
const fmtTokens = (u) => !u ? "-" : ((u.input_tokens || 0) + " → " + (u.output_tokens || 0));

// ---- 文本友好化：折叠时给一行摘要，展开时按 markdown 渲染 ----
function plainPreview(text, limit) {
  let t = String(text == null ? "" : text);
  t = t.replace(/```[\s\S]*?```/g, " [代码块] ")
       .split("\n").filter(l => !/^\s*\|/.test(l)).join(" ")
       .replace(/(^|\s)[-*+]\s+/g, "$1")
       .replace(/[#>``*_]/g, "")
       .replace(/\s+/g, " ").trim();
  return t.length > limit ? t.slice(0, limit) + "…" : t;
}

function mdInline(s) {
  return esc(s)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
    .replace(/\[([^\]]+)\]\((https?:[^)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
}

function mdRender(src) {
  const lines = String(src == null ? "" : src).replace(/\r\n?/g, "\n").split("\n");
  const out = [];
  let para = [], list = null, code = false, codeBuf = [];
  const flushPara = () => { if (para.length) { out.push("<p>" + para.map(mdInline).join("<br>") + "</p>"); para = []; } };
  const flushList = () => {
    if (list) { out.push("<" + list.tag + ">" + list.items.map(x => "<li>" + mdInline(x) + "</li>").join("") + "</" + list.tag + ">"); list = null; }
  };
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/^\s*```/.test(line)) {
      if (code) { out.push('<pre class="mdc">' + esc(codeBuf.join("\n")) + "</pre>"); codeBuf = []; code = false; }
      else { flushPara(); flushList(); code = true; }
      continue;
    }
    if (code) { codeBuf.push(line); continue; }
    if (/^\s*\|.*\|\s*$/.test(line)) {
      flushPara(); flushList();
      const rows = [];
      while (i < lines.length && /^\s*\|.*\|\s*$/.test(lines[i])) {
        const cells = lines[i].trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map(c => c.trim());
        if (!cells.every(c => /^:?-{2,}:?$/.test(c))) rows.push(cells);
        i++;
      }
      i--;
      if (rows.length) {
        const head = rows.shift();
        out.push('<table class="mdt"><thead><tr>' + head.map(c => "<th>" + mdInline(c) + "</th>").join("") +
          "</tr></thead><tbody>" + rows.map(r => "<tr>" + r.map(c => "<td>" + mdInline(c) + "</td>").join("") +
          "</tr>").join("") + "</tbody></table>");
      }
      continue;
    }
    const heading = line.match(/^#{1,6}\s+(.*)$/);
    if (heading) { flushPara(); flushList(); out.push('<div class="mdh">' + mdInline(heading[1]) + "</div>"); continue; }
    const item = line.match(/^\s*(?:([-*+])|(\d+)\.)\s+(.*)$/);
    if (item) {
      flushPara();
      const tag = item[2] ? "ol" : "ul";
      if (!list || list.tag !== tag) { flushList(); list = { tag: tag, items: [] }; }
      list.items.push(item[3]);
      continue;
    }
    if (!line.trim()) { flushPara(); flushList(); continue; }
    flushList();
    para.push(line);
  }
  if (code) out.push('<pre class="mdc">' + esc(codeBuf.join("\n")) + "</pre>");
  flushPara(); flushList();
  return out.join("");
}

function metaLine(rec) {
  const bits = [];
  if (rec.model) bits.push(rec.model);
  if (rec.effort) bits.push("effort=" + rec.effort);
  if (rec.usage) bits.push(fmtTokens(rec.usage) + " tokens");
  return bits.join(" · ");
}

let groups = [];
const live = new Map();

const timeOf = (s) => String(s || "").replace("T", " ").slice(0, 19);
const hhmmss = (s) => String(s || "").slice(11, 19) || "-";

function liveCard(uid) {
  let c = live.get(uid);
  if (c) return c;
  const el = document.createElement("div");
  el.className = "card";
  el.innerHTML = '<div class="top"><span class="model"></span><span class="badge run">进行中</span>' +
    '<span class="meta m"></span><span class="sp" style="flex:1"></span><span class="meta t"></span></div>' +
    '<div class="q"></div><div class="tools"></div><pre class="txt" style="display:none"></pre>' +
    '<details class="rd"><summary>推理过程</summary><pre class="rsn"></pre></details>';
  const box = document.getElementById("live");
  const empty = box.querySelector(".empty");
  if (empty) empty.remove();
  box.prepend(el);
  c = { el: el, started: Date.now(), n: 0 };
  live.set(uid, c);
  liveCount();
  return c;
}

function liveCount() {
  document.getElementById("livecount").textContent = live.size ? "(" + live.size + ")" : "";
  if (!live.size) {
    const box = document.getElementById("live");
    if (!box.querySelector(".card")) box.innerHTML = '<div class="empty">暂无请求。在 Codex 里发一句话，这里会实时出现。</div>';
  }
}

function onStart(ev) {
  const c = liveCard(ev.uid);
  const el = c.el;
  el.querySelector(".model").textContent = ev.model || "-";
  el.querySelector(".m").textContent = (ev.effort ? "effort=" + ev.effort + " · " : "") + (ev.path || "");
  if (ev.question) el.querySelector(".q").textContent = "问题：" + ev.question;
  if (ev.status) setStatus(c, ev.status);
  tick();
}

function setStatus(c, status) {
  const b = c.el.querySelector(".badge");
  b.textContent = status;
  b.className = "badge " + (status === 200 ? "run" : "bad");
}

function append(c, sel, text) {
  const pre = c.el.querySelector(sel);
  if (!text) return;
  const atBottom = pre.scrollTop + pre.clientHeight >= pre.scrollHeight - 30;
  pre.style.display = "block";
  pre.appendChild(document.createTextNode(text));
  if (atBottom) pre.scrollTop = pre.scrollHeight;
}

function onDelta(ev) {
  const c = liveCard(ev.uid);
  if (ev.error) append(c, ".txt", "\n[error] " + JSON.stringify(ev.error).slice(0, 400));
  if (ev.text) append(c, ".txt", ev.text);
  if (ev.reasoning) {
    const d = c.el.querySelector(".rd");
    d.open = true;
    append(c, ".rsn", ev.reasoning);
  }
  if (ev.tool_args != null) c.pendingArgs = ev.tool_args;
  if (ev.tool) {
    const t = c.el.querySelector(".tools");
    t.textContent += "tool_call: " + (ev.tool.name || "?") + " " +
      String(ev.tool.arguments || c.pendingArgs || "").slice(0, 300) + "\n";
    c.pendingArgs = null;
  }
  if (ev.usage) c.el.querySelector(".t").textContent = fmtTokens(ev.usage);
}

function onDone(ev) {
  const c = liveCard(ev.uid);
  const b = c.el.querySelector(".badge");
  b.textContent = (ev.status || "?") + (ev.error ? " " + String(ev.error).slice(0, 40) : "");
  b.className = "badge " + (ev.status === 200 && !ev.error ? "ok" : "bad");
  c.el.querySelector(".t").textContent =
    fmtMs(ev.duration_ms) + " · " + fmtBytes(ev.bytes) + " · " + fmtTokens(ev.usage);
  c.done = true;
  live.delete(ev.uid);
  liveCount();
  if (ev.file) {
    const a = document.createElement("a");
    a.textContent = "  查看完整请求/返回";
    a.href = "#";
    a.onclick = (e) => { e.preventDefault(); openCapture(ev.file); };
    c.el.querySelector(".top").appendChild(a);
  }
  load();
}

function tick() {
  live.forEach((c) => {
    if (c.done) return;
    const s = Math.round((Date.now() - c.started) / 1000);
    c.el.querySelector(".t").textContent = s < 60 ? s + " s" : Math.floor(s / 60) + "m " + (s % 60) + "s";
  });
  setTimeout(tick, 1000);
}

function render() {
  const needle = document.getElementById("filter").value.trim().toLowerCase();
  const onlyErr = document.getElementById("onlyErr").checked;
  const showInternal = document.getElementById("showInternal").checked;
  const box = document.getElementById("groups");
  box.innerHTML = "";
  let shown = 0;
  for (const g of groups) {
    if (g.internal && !showInternal) continue;
    const hay = [g.question, g.final_text, g.model, g.effort, g.started_at,
                 g.thread_id, g.turn_id, g.message_id, g.source_label]
      .concat((g.requests || []).map(r => (r.text || "") + " " + (r.tool_names || []).join(",")))
      .join(" ").toLowerCase();
    if (onlyErr && !g.error) continue;
    if (needle && !hay.includes(needle)) continue;
    shown++;
    box.appendChild(groupCard(g));
  }
  document.getElementById("noRows").style.display = shown ? "none" : "block";
  document.getElementById("gcount").textContent = groups.length ? "（" + groups.length + " 个问题 / " +
    groups.reduce((n, g) => n + g.count, 0) + " 次请求）" : "";
  document.getElementById("stats").textContent = groups.length + " 个问题 · " +
    groups.reduce((n, g) => n + g.count, 0) + " 次请求";
}

function groupCard(g) {
  const wrap = document.createElement("div");
  wrap.className = "grp";
  wrap._group = g;
  const bad = !!g.error;
  const head = document.createElement("div");
  head.className = "gq-head";
  const srcClass = "src " + esc(g.source || "");
  head.innerHTML = '<span class="caret">▸</span>' +
    '<div class="gq-body"><div class="gq-text"></div><div class="gq-final"></div>' +
      '<div class="ids"></div></div>' +
    '<div class="gq-meta"><span class="big">' + esc(timeOf(g.started_at)) + '</span>' +
      '<span class="' + srcClass + '">' + esc(g.source_label || "未知") + '</span><br>' +
      esc(g.count) + ' 次请求 · ' + fmtMs(g.duration_ms) + '<br>' +
      (bad ? '<span style="color:var(--bad)">' + esc(g.status ?? "-") + ' ' +
             esc(String(g.error).slice(0, 30)) + '</span>'
           : '<span style="color:var(--ok)">' + esc(g.status ?? "-") + '</span>') +
      ' · ' + esc(g.effort || "-") + ' · ' + fmtTokens(g.usage) + '</div>';
  const q = head.querySelector(".gq-text");
  q.textContent = (g.internal ? "[内部] " : "") + (g.question ? g.question : "（未抓到用户问题）");
  const fin = head.querySelector(".gq-final");
  const full = g.final_text || "";
  if (full.trim()) {
    fin.textContent = "最终回复：" + plainPreview(full, 220);
  } else {
    fin.textContent = "最终回复：（本轮没有独立回复，展开看每次请求的输出）";
  }
  const answer = document.createElement("div");
  answer.className = "answer";
  answer.hidden = true;
  const ids = head.querySelector(".ids");
  const bits = [];
  if (g.turn_id) bits.push("turn " + g.turn_id.slice(0, 8));
  if (g.thread_id) bits.push("thread " + g.thread_id.slice(0, 8));
  if (g.message_id) bits.push("msg " + g.message_id.slice(4, 12));
  if (g.trigger) bits.push(g.trigger);
  if (g.subagent_kind) bits.push("subagent " + g.subagent_kind);
  if (g.ended_at) bits.push("结束 " + timeOf(g.ended_at).slice(11));
  ids.textContent = bits.join(" · ");
  ids.title = "thread_id = " + (g.thread_id || "-") + "\nturn_id   = " + (g.turn_id || "-") +
              "\nmessage   = " + (g.message_id || "-") + "\nsource    = " + (g.source || "-") + " / " +
              (g.trigger || "-");
  const kids = document.createElement("div");
  kids.className = "kids hidden";
  kids.innerHTML = '<div class="hdr"><span class="idx"></span><span class="t">时间</span>' +
      '<span class="st">HTTP</span><span class="mdl">模型 · 档位</span>' +
      '<span class="num">耗时</span><span class="num">请求 → 返回</span>' +
      '<span class="num">tokens</span><span class="prev">本轮输出 / 工具</span></div>' +
    (g.requests || []).map((r, i) => {
    const rb = r.error || r.status !== 200;
    const info = plainPreview(r.text || "", 120) ||
      ((r.tool_names || []).length ? "工具调用: " + (r.tool_names || []).join(", ") : "");
    return '<div class="req" data-file="' + esc(r.file) + '" title="' +
        esc("message = " + (r.message_id || "-") + "\nthread  = " + (r.thread_id || "-") +
            "\nturn    = " + (r.turn_id || "-") + "\nsource  = " + (r.thread_source || "-") +
            "\n点击查看完整请求头/返回头/请求体") + '">' +
      '<span class="idx">#' + (i + 1) + '</span>' +
      '<span class="t">' + esc(hhmmss(r.started_at)) + '</span>' +
      '<span class="st" style="color:' + (rb ? "var(--bad)" : "var(--ok)") + '">' +
        esc(r.status ?? "-") + '</span>' +
      '<span class="mdl">' + esc(r.model || "-") + ' · ' + esc(r.effort || "-") + '</span>' +
      '<span class="num">' + fmtMs(r.duration_ms) + '</span>' +
      '<span class="num">' + fmtBytes(r.request_bytes) + ' → ' + fmtBytes(r.response_bytes) + '</span>' +
      '<span class="num">' + fmtTokens(r.usage) + '</span>' +
      '<span class="prev">' + esc(info) + '</span>' +
      '<span class="go">查看</span></div>';
  }).join("");
  kids.querySelectorAll(".req").forEach((row) => {
    row.onclick = (e) => { e.stopPropagation(); openCapture(row.dataset.file); };
  });
  head.onclick = () => {
    const open = kids.classList.toggle("hidden") === false;
    wrap.classList.toggle("open", open);
    head.querySelector(".caret").textContent = open ? "▾" : "▸";
    answer.hidden = !open;
    if (open && !answer.dataset.loaded) {
      answer.dataset.loaded = "1";
      answer.textContent = "载入完整回复…";
      loadAnswer(g, answer);
    }
  };
  wrap.appendChild(head);
  wrap.appendChild(answer);
  wrap.appendChild(kids);
  return wrap;
}

async function loadAnswer(g, box) {
  if (!g.final_file) {
    box.innerHTML = '<div class="hint">本轮没有独立的最终回复（只有工具调用），展开下面的请求可以看到每次输出。</div>';
    return;
  }
  try {
    const res = await fetch(url("/__ui/api/answer?file=" + encodeURIComponent(g.final_file)));
    const data = await res.json();
    const html = mdRender(data.text || "");
    box.innerHTML = (html || '<div class="hint">（空回复）</div>') +
      '<div class="hint">' + esc(metaLine(data)) + " · 全文 " + (data.text || "").length + " 字" +
      " · <a href=\"#\" class=\"rawlink\">看原始请求/返回</a></div>";
    const link = box.querySelector(".rawlink");
    if (link) link.onclick = (e) => { e.preventDefault(); openCapture(g.final_file); };
  } catch (e) {
    box.textContent = "载入失败：" + e;
  }
}

async function load() {
  try {
    const res = await fetch(url("/__ui/api/list?limit=300"));
    const data = await res.json();
    groups = data.groups || [];
    document.getElementById("where").textContent = data.capture_dir || "";
    for (const snap of (data.live || [])) onStart(snap);
    render();
  } catch (e) { /* adapter restarted, the stream will reconnect */ }
}

async function openCapture(file) {
  if (!file) return;
  const res = await fetch(url("/__ui/api/text?file=" + encodeURIComponent(file)));
  document.getElementById("mbody").textContent = await res.text();
  document.getElementById("mtitle").textContent = file;
  document.getElementById("mraw").href = url("/__ui/api/json?file=" + encodeURIComponent(file));
  document.getElementById("modal").classList.add("on");
}

document.getElementById("mclose").onclick = () => document.getElementById("modal").classList.remove("on");
document.getElementById("modal").onclick = (e) => { if (e.target.id === "modal") e.currentTarget.classList.remove("on"); };
document.addEventListener("keydown", (e) => { if (e.key === "Escape") document.getElementById("modal").classList.remove("on"); });
document.getElementById("filter").oninput = render;
document.getElementById("onlyErr").onchange = render;
document.getElementById("showInternal").onchange = render;
document.getElementById("reload").onclick = load;
document.getElementById("expand").onclick = (e) => {
  const open = e.target.textContent === "展开全部";
  document.querySelectorAll(".grp").forEach((g) => {
    g.querySelector(".kids").classList.toggle("hidden", !open);
    g.classList.toggle("open", open);
    g.querySelector(".caret").textContent = open ? "▾" : "▸";
    const ans = g.querySelector(".answer");
    if (ans) {
      ans.hidden = !open;
      if (open && !ans.dataset.loaded) {
        ans.dataset.loaded = "1";
        ans.textContent = "载入完整回复…";
        if (g._group) loadAnswer(g._group, ans);
      }
    }
  });
  e.target.textContent = open ? "收起全部" : "展开全部";
};

load();
tick();
// ?expand=1 opens every group (handy for a link or a screenshot).
if (new URLSearchParams(location.search).has("expand")) {
  setTimeout(() => { const b = document.getElementById("expand"); if (b.textContent === "展开全部") b.click(); }, 400);
}
const es = new EventSource(url("/__ui/api/live"));
es.onopen = () => document.getElementById("dot").classList.add("on");
es.onerror = () => document.getElementById("dot").classList.remove("on");
es.onmessage = (e) => {
  const ev = JSON.parse(e.data);
  if (ev.event === "started") onStart(ev);
  else if (ev.event === "status") setStatus(liveCard(ev.uid), ev.status);
  else if (ev.event === "delta") onDelta(ev);
  else if (ev.event === "done") onDone(ev);
};
</script>
</body>
</html>
"""


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    address_family = socket.AF_INET


KEYS = load_keys()


def main():
    port = PORT
    while True:
        try:
            httpd = Server(("127.0.0.1", port), Handler)
            break
        except OSError as exc:
            if port == PORT:
                # Requested port busy: fail loudly so launchd can retry.
                print("cannot bind 127.0.0.1:%d: %s" % (port, exc), file=sys.stderr, flush=True)
                raise SystemExit(1)
            port += 1
    log("listening on 127.0.0.1:%d -> %s (min max_output_tokens=%d, key routing=%s, capture=%s)" % (
        port, UPSTREAM, MIN_MAX_OUTPUT_TOKENS, "on" if KEYS else "off",
        CAPTURE_DIR if CAPTURE else "off"))
    pruned = prune_captures()
    if pruned:
        log("capture: pruned %d directory(ies) (keep %d days / %d MiB)" % (
            pruned, CAPTURE_KEEP_DAYS, CAPTURE_MAX_TOTAL_BYTES // (1024 * 1024)))
    if CAPTURE:
        if index_needs_rebuild():
            try:
                os.remove(INDEX_PATH)
            except OSError:
                pass
        if not os.path.exists(INDEX_PATH):
            built = rebuild_index()
            if built:
                log("capture: built index for %d existing exchange(s)" % built)
    if UI:
        log("live UI: http://127.0.0.1:%d/__ui%s" % (port, " (token required)" if UI_TOKEN else ""))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
