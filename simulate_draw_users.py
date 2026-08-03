#!/usr/bin/env python3
"""
Simulate online draw traffic for uid 10001-10100.

Default mode is dry-run: it writes the randomized draw plan but does not call
the API. Add --execute to send requests.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any


API_URL = "https://testqaactapi.busi.inke.cn/api/internal/act200001/act_draw/iSimulationDraw"
DEFAULT_TICKET = "STXnnvFgCNxeXjuVNvodOVxcJLoimpRxLew"
DEFAULT_MODULE = "act202601_game_yichuidingjin"
DEFAULT_POOL_TYPE = "A1"


@dataclass(frozen=True)
class DrawPlan:
    uid: int
    count: int
    group: str


def build_plan(seed: int | None) -> list[DrawPlan]:
    rng = random.Random(seed)
    uids = list(range(10001, 10101))
    heavy_uids = set(rng.sample(uids, 20))

    plan: list[DrawPlan] = []
    for uid in uids:
        if uid in heavy_uids:
            plan.append(DrawPlan(uid=uid, count=rng.randint(200, 500), group="200-500"))
        else:
            plan.append(DrawPlan(uid=uid, count=rng.randint(1, 99), group="1-99"))
    return plan


def write_plan_csv(path: Path, plan: list[DrawPlan]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["uid", "count", "group"])
        writer.writeheader()
        for item in plan:
            writer.writerow({"uid": item.uid, "count": item.count, "group": item.group})


def request_once(
    item: DrawPlan,
    *,
    ticket: str,
    module_name: str,
    pool_type: str,
    worker_count: int,
    timeout: float,
) -> dict[str, Any]:
    params = {
        "module_name": "",
        "pool_type": pool_type,
        "uid_input": str(item.uid),
        "count": str(item.count),
        "worker_count": str(worker_count),
        "module_name_select": module_name,
        "pool_type_select": "",
        "uid": "",
        "is_all_uid": "",
        "is_empty": "2",
        "ticket": ticket,
    }
    url = API_URL + "?" + urllib.parse.urlencode(params)
    started = time.time()
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        body = resp.read()
        status = resp.status
    elapsed_ms = round((time.time() - started) * 1000, 2)
    try:
        payload: Any = json.loads(body.decode("utf-8"))
    except Exception:
        payload = body.decode("utf-8", errors="replace")
    return {
        "uid": item.uid,
        "count": item.count,
        "group": item.group,
        "ok": True,
        "status": status,
        "elapsed_ms": elapsed_ms,
        "response": payload,
    }


def execute_item(
    item: DrawPlan,
    *,
    ticket: str,
    module_name: str,
    pool_type: str,
    worker_count: int,
    timeout: float,
    retries: int,
) -> dict[str, Any]:
    last_error = ""
    for attempt in range(1, retries + 2):
        try:
            return request_once(
                item,
                ticket=ticket,
                module_name=module_name,
                pool_type=pool_type,
                worker_count=worker_count,
                timeout=timeout,
            )
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = repr(exc)
            if attempt <= retries:
                time.sleep(min(2.0, 0.4 * attempt))
    return {
        "uid": item.uid,
        "count": item.count,
        "group": item.group,
        "ok": False,
        "error": last_error,
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def summarize(plan: list[DrawPlan]) -> dict[str, Any]:
    heavy = [p for p in plan if p.group == "200-500"]
    light = [p for p in plan if p.group == "1-99"]
    return {
        "users": len(plan),
        "heavy_users": len(heavy),
        "light_users": len(light),
        "total_draw_count": sum(p.count for p in plan),
        "heavy_draw_count": sum(p.count for p in heavy),
        "light_draw_count": sum(p.count for p in light),
        "max_count": max(p.count for p in plan),
        "min_count": min(p.count for p in plan),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulate draw requests for uid 10001-10100.")
    parser.add_argument("--execute", action="store_true", help="Actually call the simulation API.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed. Omit for fresh randomness.")
    parser.add_argument("--out-dir", default="simulation_draw_output", help="Output directory.")
    parser.add_argument("--ticket", default=DEFAULT_TICKET, help="API ticket.")
    parser.add_argument("--module", default=DEFAULT_MODULE, help="module_name_select value.")
    parser.add_argument("--pool-type", default=DEFAULT_POOL_TYPE, help="pool_type value.")
    parser.add_argument("--worker-count", type=int, default=1, help="worker_count API value.")
    parser.add_argument("--concurrency", type=int, default=4, help="Concurrent user requests.")
    parser.add_argument("--timeout", type=float, default=60.0, help="HTTP timeout seconds.")
    parser.add_argument("--retries", type=int, default=2, help="Retries per uid after first failure.")
    args = parser.parse_args()

    if args.concurrency < 1:
        raise SystemExit("--concurrency must be >= 1")

    out_dir = Path(args.out_dir).expanduser().resolve()
    plan = build_plan(args.seed)
    plan_csv = out_dir / "simulation_draw_plan.csv"
    write_plan_csv(plan_csv, plan)

    summary = summarize(plan)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"plan_csv={plan_csv}")

    if not args.execute:
        print("dry_run=true; add --execute to call the API.")
        return 0

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = {
            executor.submit(
                execute_item,
                item,
                ticket=args.ticket,
                module_name=args.module,
                pool_type=args.pool_type,
                worker_count=args.worker_count,
                timeout=args.timeout,
                retries=args.retries,
            ): item
            for item in plan
        }
        for done_count, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            status = "OK" if result.get("ok") else "ERR"
            print(f"[{done_count}/{len(plan)}] {status} uid={result['uid']} count={result['count']}")

    results.sort(key=lambda r: int(r["uid"]))
    result_path = out_dir / "simulation_draw_results.jsonl"
    write_jsonl(result_path, results)

    ok_count = sum(1 for r in results if r.get("ok"))
    print(f"result_jsonl={result_path}")
    print(f"ok={ok_count} failed={len(results) - ok_count}")
    return 0 if ok_count == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
