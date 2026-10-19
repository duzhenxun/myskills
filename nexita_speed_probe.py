#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nexita_speed_probe.py
探测 https://codeapi.nexita.net 网关下所有可用模型的响应速度。

特性:
  * 自动拉取 /v1/models, 用两个 key 各自探测其可见模型
  * 流式 chat/completions, 测量:
      - TTFT(any)   : 首个 token(含推理) 延迟
      - TTFT(正文)  : 首个可见正文 token 延迟(对推理模型更有感知意义)
      - 生成速度    : 正文 tokens/s
      - 总耗时 / 推理 token 数 / 正文 token 数
  * 网关有排队/限流 -> 默认低并发(2) + 自动重试, 取各模型最优结果
  * 超时/报错优雅降级, 最终输出排行 + JSON 报告

用法:
  python3 nexita_speed_probe.py                       # 全部文本模型
  python3 nexita_speed_probe.py --all                 # 包含 audio/image 等全部模型
  python3 nexita_speed_probe.py --models gpt-5.6-luna deepseek-v4-flash
  python3 nexita_speed_probe.py --list                # 只列出模型, 不探测
  python3 nexita_speed_probe.py --concurrency 4 --retries 3 --timeout 120
  python3 nexita_speed_probe.py --count 200 --max-tokens 2048
  python3 nexita_speed_probe.py --json report.json

key 配置(默认用脚本内置的, 可用环境变量覆盖):
  NEXITA_DS_KEY      deepseek 系列
  NEXITA_CODEX_KEY   codex 系列
"""
import argparse
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.environ.get("NEXITA_BASE", "https://codeapi.nexita.net")
DEFAULT_DS_KEY = "sk-8790f7c98856f21ec6f6652d0ac9c1e3fe56934697a047aecfdc75221c0f1cae"
DEFAULT_CODEX_KEY = "sk-53a4e0b42541b6f50d49e72609122d65b20eeb82d042c91e787b6d23ea5737aa"
UA = "nexita-speed-probe/1.0"
PLOCK = threading.Lock()

# 默认跳过这些 id(非文本对话模型)
SKIP_HINTS = ("audio", "image", "realtime", "reserve", "auto-review", "whisper", "tts", "embedd")


def fetch_models(key: str) -> list:
    req = urllib.request.Request(
        f"{BASE}/v1/models",
        headers={"Authorization": f"Bearer {key}", "User-Agent": UA},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8", "replace"))
    return [m["id"] for m in data.get("data", [])]


def is_text_model(mid: str) -> bool:
    return not any(h in mid for h in SKIP_HINTS)


def estimate_tokens(text: str) -> int:
    """usage 缺失时的粗估: 拉丁字符约 4 字符/token, 中文约 1 字/token"""
    cjk = len(re.findall(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]", text))
    latin = len(text) - cjk
    return cjk + max(1, round(latin / 4))


def probe_model(mid: str, key: str, prompt: str, max_tokens: int,
                timeout: int) -> dict:
    """对单个模型做一次流式探测, 返回指标 dict(永不抛异常)"""
    res = {"model": mid, "status": "ERROR", "error": "", "ttft_any": None,
           "ttft_content": None, "total_s": None, "gen_s": None,
           "tok_s": None, "prompt_tokens": None, "completion_tokens": None,
           "content_chars": 0, "reasoning_chars": 0, "finish_reason": None}
    body = {
        "model": mid,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "max_tokens": max_tokens,
        "stream_options": {"include_usage": True},
        "temperature": 0.7,
    }
    req = urllib.request.Request(
        f"{BASE}/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept-Encoding": "identity",
            "User-Agent": UA,
        },
        method="POST",
    )
    t0 = time.monotonic()
    deadline = t0 + timeout
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            res["ttft_headers"] = round(time.monotonic() - t0, 3)
            content_buf, reason_buf = [], []
            first_any = first_content = None
            usage = {}
            for raw in r:
                if time.monotonic() > deadline:
                    res["status"] = "TIMEOUT"
                    res["error"] = f"wall-clock > {timeout}s"
                    break
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue                      # 跳过 : ping 等注释
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                if chunk.get("usage"):
                    usage = chunk["usage"]
                choices = chunk.get("choices") or []
                if not choices:
                    continue
                ch = choices[0]
                delta = ch.get("delta") or {}
                if ch.get("finish_reason"):
                    res["finish_reason"] = ch["finish_reason"]
                txt = delta.get("content") or ""
                rsn = delta.get("reasoning_content") or ""
                if rsn:
                    reason_buf.append(rsn)
                    if first_any is None:
                        first_any = time.monotonic()
                if txt:
                    content_buf.append(txt)
                    if first_any is None:
                        first_any = time.monotonic()
                    if first_content is None:
                        first_content = time.monotonic()
            content = "".join(content_buf)
            reasoning = "".join(reason_buf)
            t_end = time.monotonic()
            res["content_chars"] = len(content)
            res["reasoning_chars"] = len(reasoning)
            res["ttft_any"] = round(first_any - t0, 3) if first_any else None
            res["ttft_content"] = round(first_content - t0, 3) if first_content else None
            res["total_s"] = round(t_end - t0, 3)
            res["gen_s"] = round(t_end - (first_content or t0), 3)
            res["prompt_tokens"] = usage.get("prompt_tokens")
            res["completion_tokens"] = usage.get("completion_tokens")
            if usage.get("completion_tokens_details"):
                res["reasoning_tokens"] = usage["completion_tokens_details"].get("reasoning_tokens")
            if res["completion_tokens"] is None:
                res["completion_tokens"] = estimate_tokens(content) + estimate_tokens(reasoning)
            if res["ttft_content"] is not None and res["completion_tokens"]:
                gen_toks = res["completion_tokens"]
                if res.get("reasoning_tokens"):
                    gen_toks = max(1, res["completion_tokens"] - res["reasoning_tokens"])
                res["tok_s"] = round(gen_toks / res["gen_s"], 2) if res["gen_s"] > 0 else None
            if res["status"] != "TIMEOUT" and content:
                res["status"] = "OK"
            elif res["status"] != "TIMEOUT":
                res["status"] = "EMPTY"
                res["error"] = "no content tokens received"
    except urllib.error.HTTPError as e:
        res["total_s"] = round(time.monotonic() - t0, 3)
        try:
            msg = json.loads(e.read().decode("utf-8", "replace"))
            res["error"] = f"HTTP {e.code}: {msg.get('error', {}).get('message', msg)}"
        except Exception:
            res["error"] = f"HTTP {e.code}"
    except Exception as e:
        res["total_s"] = round(time.monotonic() - t0, 3)
        if isinstance(e, (TimeoutError, urllib.error.URLError, OSError)) or "timed out" in str(e):
            res["status"] = "TIMEOUT"
            res["error"] = f"timeout > {timeout}s: {str(e)[:100]}"
        else:
            res["error"] = str(e)[:200]
    return res


def probe_with_retries(mid, key, prompt, max_tokens, timeout, retries, backoff):
    """探测多次, 返回合并后的最优结果"""
    runs = []
    last = None
    for i in range(retries):
        last = probe_model(mid, key, prompt, max_tokens, timeout)
        runs.append(last)
        if last["status"] == "OK":
            break
        if i < retries - 1:
            time.sleep(backoff * (i + 1))
    merged = dict(last)                       # 基础字段取最后一次
    merged["runs"] = runs
    merged["attempts"] = len(runs)
    ok_runs = [r for r in runs if r["status"] == "OK"]
    if ok_runs:
        merged["status"] = "OK"
        merged["error"] = ""
        merged["ttft_content"] = min(r["ttft_content"] for r in ok_runs)
        merged["ttft_any"] = min(r["ttft_any"] for r in ok_runs)
        merged["tok_s"] = max(r["tok_s"] for r in ok_runs)
        merged["total_s"] = min(r["total_s"] for r in ok_runs)
        merged["gen_s"] = min(r["gen_s"] for r in ok_runs)
        merged["completion_tokens"] = max(r["completion_tokens"] for r in ok_runs)
        merged["reasoning_tokens"] = max((r.get("reasoning_tokens") or 0 for r in ok_runs), default=0)
        best = min(ok_runs, key=lambda r: r["total_s"])
        merged["content_chars"] = best["content_chars"]
        merged["reasoning_chars"] = best["reasoning_chars"]
        merged["prompt_tokens"] = best["prompt_tokens"]
        merged["finish_reason"] = best["finish_reason"]
    elif any(r["status"] == "TIMEOUT" for r in runs):
        merged["status"] = "TIMEOUT"
    return merged


def fmt_s(v):
    return "  -  " if v is None else f"{v:>5.2f}"


def fmt_t(v):
    return "  -  " if v is None else f"{v:>5}"


def main():
    ap = argparse.ArgumentParser(description="nexita 网关模型响应速度探测")
    ap.add_argument("--all", action="store_true", help="包含 audio/image 等全部模型")
    ap.add_argument("--models", nargs="*", help="只探测指定模型 id")
    ap.add_argument("--list", action="store_true", help="只列出模型不探测")
    ap.add_argument("--concurrency", type=int, default=2,
                    help="并发数(网关有排队/限流, 建议 2-3, 默认2)")
    ap.add_argument("--retries", type=int, default=2, help="每模型最多探测次数(默认2)")
    ap.add_argument("--backoff", type=float, default=3.0, help="重试间隔秒数(默认3)")
    ap.add_argument("--timeout", type=int, default=90, help="单次探测超时秒数(默认90)")
    ap.add_argument("--count", type=int, default=200, help="让模型数到 N(生成长度控制, 默认200)")
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--prompt", help="自定义 prompt(默认从1数到N)")
    ap.add_argument("--json", help="输出 JSON 报告路径")
    args = ap.parse_args()

    ds_key = os.environ.get("NEXITA_DS_KEY", DEFAULT_DS_KEY)
    cx_key = os.environ.get("NEXITA_CODEX_KEY", DEFAULT_CODEX_KEY)

    # 1. 拉模型列表
    groups = [("deepseek", ds_key), ("codex", cx_key)]
    targets = []
    for gname, key in groups:
        try:
            mids = fetch_models(key)
        except Exception as e:
            print(f"[warn] {gname}: 拉取模型列表失败: {e}")
            continue
        for mid in mids:
            if not args.all and not is_text_model(mid):
                continue
            targets.append({"model": mid, "key": key, "group": gname})
    # 去重(同一 id 只探测一次, 优先 deepseek 分组)
    seen, uniq = set(), []
    for t in targets:
        if t["model"] not in seen:
            seen.add(t["model"])
            uniq.append(t)
    targets = uniq

    if args.models:
        wanted = set(args.models)
        targets = [t for t in targets if t["model"] in wanted]
        missing = wanted - {t["model"] for t in targets}
        if missing:
            print(f"[warn] 未找到模型: {', '.join(sorted(missing))}")

    if args.list or not targets:
        print(f"共 {len(targets)} 个模型:")
        for t in targets:
            print(f"  [{t['group']:>8}] {t['model']}")
        return

    prompt = args.prompt or (
        f"请从1数到{args.count}，输出每个数字，用逗号分隔，不要输出任何其他内容。")
    print(f"探测 {len(targets)} 个模型 (并发{args.concurrency}, 重试{args.retries}, "
          f"超时{args.timeout}s, prompt: 数到{args.count}, max_tokens={args.max_tokens})")
    print("-" * 118)

    results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = {ex.submit(probe_with_retries, t["model"], t["key"], prompt,
                          args.max_tokens, args.timeout, args.retries, args.backoff): t
                for t in targets}
        for fut in as_completed(futs):
            t = futs[fut]
            try:
                r = fut.result()
            except Exception as e:           # 理论上不会发生
                r = {"model": t["model"], "status": "ERROR", "error": str(e)[:100]}
            r["group"] = t["group"]
            results.append(r)
            s = r.get("status", "ERROR")
            extra = f"(x{r.get('attempts', 1)}次)" if r.get("attempts", 1) > 1 else ""
            if s == "OK":
                with PLOCK:
                    print(f"  {r['model']:<40} [{t['group']:<8}] ttft正文={fmt_s(r['ttft_content'])}s "
                          f"首token={fmt_s(r['ttft_any'])}s tok/s={fmt_t(r['tok_s'])} "
                          f"总{fmt_s(r['total_s'])}s 正文{r.get('completion_tokens','?')}tok "
                          f"推理{r.get('reasoning_tokens', 0)}tok {extra}")
            else:
                with PLOCK:
                    print(f"  {r['model']:<40} [{t['group']:<8}] {s:<7} {r.get('error','')[:70]} {extra}")

    # 2. 排行
    ok = [r for r in results if r.get("status") == "OK"]
    print("\n" + "=" * 118)
    print("排行 (按正文生成速度 tok/s):")
    for i, r in enumerate(sorted(ok, key=lambda x: -(x.get("tok_s") or 0)), 1):
        print(f"  {i:>2}. {r['model']:<40} tok/s={r.get('tok_s'):>6} "
              f"ttft正文={r.get('ttft_content')}s 总={r.get('total_s')}s")
    print("\n排行 (按首正文 token 延迟 TTFT):")
    for i, r in enumerate(sorted(ok, key=lambda x: x.get("ttft_content") or 9e9), 1):
        print(f"  {i:>2}. {r['model']:<40} ttft正文={r.get('ttft_content')}s "
              f"tok/s={r.get('tok_s')} 总={r.get('total_s')}s")

    n_ok = len(ok)
    n_timeout = sum(1 for r in results if r.get("status") == "TIMEOUT")
    n_err = sum(1 for r in results if r.get("status") in ("ERROR", "EMPTY"))
    print(f"\n汇总: OK {n_ok} / TIMEOUT {n_timeout} / 失败 {n_err} / 共 {len(results)}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"base": BASE, "prompt": prompt, "results": results},
                      f, ensure_ascii=False, indent=2)
        print(f"报告已写入: {args.json}")


if __name__ == "__main__":
    main()
