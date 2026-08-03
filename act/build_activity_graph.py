#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

OUT_DIR = Path(__file__).resolve().parent
INDEX_PATH = OUT_DIR / "pages_index.json"


def month_key(title: str) -> str | None:
    match = re.search(r"2026年\s*(\d{1,2})\s*月份活动", title)
    if not match:
        return None
    return f"2026-{int(match.group(1)):02d}"


def date_range(title: str) -> str:
    match = re.search(r"(\d{1,2}(?:\.\d{1,2})?\s*-\s*\d{1,2}(?:\.\d{1,2})?)", title)
    return match.group(1).replace(" ", "") if match else ""


def clean_activity_name(title: str) -> str:
    name = re.sub(r"^\s*\d{1,2}(?:\.\d{1,2})?\s*-\s*\d{1,2}(?:\.\d{1,2})?", "", title)
    name = re.sub(r"^[\s:：\-—]+", "", name)
    return name.strip() or title


def load_markdown(row: dict[str, Any]) -> str:
    path = OUT_DIR / row["files"]["markdown"]
    return path.read_text(encoding="utf-8") if path.exists() else ""


def first_lines(text: str, limit: int = 8) -> list[str]:
    lines = []
    for line in text.splitlines()[1:]:
        value = line.strip()
        if value:
            lines.append(value)
        if len(lines) >= limit:
            break
    return lines


def mermaid_id(value: str) -> str:
    return "n" + re.sub(r"\D", "", value)


def main() -> None:
    rows = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    by_id = {row["id"]: row for row in rows}
    children = defaultdict(list)
    for row in rows:
        if row.get("parent_id"):
            children[row["parent_id"]].append(row)

    months = []
    activities = []
    for row in rows:
        key = month_key(row["title"])
        if not key:
            continue
        month = {
            "month": key,
            "title": row["title"],
            "page_id": row["id"],
            "url": row["url"],
            "summary": first_lines(load_markdown(row), 10),
            "activities": [],
        }
        months.append(month)
        for activity_row in children[row["id"]]:
            descendants = []
            stack = list(children[activity_row["id"]])
            while stack:
                child = stack.pop(0)
                descendants.append({
                    "title": child["title"],
                    "page_id": child["id"],
                    "url": child["url"],
                    "depth": child["depth"],
                    "markdown": child["files"]["markdown"],
                })
                stack.extend(children[child["id"]])

            activity = {
                "month": key,
                "title": activity_row["title"],
                "name": clean_activity_name(activity_row["title"]),
                "date_range": date_range(activity_row["title"]),
                "page_id": activity_row["id"],
                "url": activity_row["url"],
                "markdown": activity_row["files"]["markdown"],
                "summary": first_lines(load_markdown(activity_row), 12),
                "related_pages": descendants,
            }
            activities.append(activity)
            month["activities"].append(activity)

    months.sort(key=lambda item: item["month"])
    activities.sort(key=lambda item: (item["month"], item["date_range"], item["title"]))

    (OUT_DIR / "activities.json").write_text(json.dumps({"months": months, "activities": activities}, ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# 2026营收运营活动图谱", "", f"来源 Wiki：{by_id['452644191']['url']}", f"页面总数：{len(rows)}", f"活动数：{len(activities)}", ""]
    md.extend(["## 月度活动总览", ""])
    for month in months:
        md.append(f"### {month['title']}")
        md.append("")
        if month["summary"]:
            md.append("月度判断：")
            for line in month["summary"]:
                md.append(f"- {line}")
            md.append("")
        for activity in month["activities"]:
            date = f"（{activity['date_range']}）" if activity["date_range"] else ""
            md.append(f"- [{activity['name']}{date}]({activity['url']})")
            if activity["related_pages"]:
                related = "、".join(f"[{p['title']}]({p['url']})" for p in activity["related_pages"][:8])
                suffix = " ..." if len(activity["related_pages"]) > 8 else ""
                md.append(f"  资料：{related}{suffix}")
        md.append("")

    md.extend(["## Mermaid 图谱", "", "```mermaid", "graph TD", "root[2026营收运营活动]"])
    for month in months:
        mid = mermaid_id(month["page_id"])
        md.append(f"root --> {mid}[{month['month']}]")
        for activity in month["activities"]:
            aid = mermaid_id(activity["page_id"])
            label = activity["name"].replace('"', "'")
            md.append(f"{mid} --> {aid}[\"{label}\"]")
            for related in activity["related_pages"][:6]:
                rid = mermaid_id(related["page_id"])
                rlabel = related["title"].replace('"', "'")
                md.append(f"{aid} --> {rid}[\"{rlabel}\"]")
    md.extend(["```", ""])
    (OUT_DIR / "activity_graph.md").write_text("\n".join(md), encoding="utf-8")

    cards = []
    for month in months:
        items = []
        for activity in month["activities"]:
            related = "".join(
                f'<li><a href="{html.escape(p["url"])}">{html.escape(p["title"])}</a></li>'
                for p in activity["related_pages"]
            )
            summary = "".join(f"<li>{html.escape(line)}</li>" for line in activity["summary"][:6])
            items.append(
                f'<article class="activity"><h3><a href="{html.escape(activity["url"])}">{html.escape(activity["name"])}</a></h3>'
                f'<p class="date">{html.escape(activity["date_range"] or "未识别日期")}</p><ul>{summary}</ul>'
                f'<details><summary>关联资料 {len(activity["related_pages"])} 个</summary><ul>{related}</ul></details></article>'
            )
        cards.append(f'<section class="month"><h2>{html.escape(month["title"])}</h2>{"".join(items)}</section>')

    html_doc = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>2026营收运营活动图谱</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:0;background:#111827;color:#e5e7eb;}}
header{{padding:32px;background:linear-gradient(135deg,#4f46e5,#06b6d4);}}
h1{{margin:0;font-size:32px;}}a{{color:#67e8f9;}}main{{padding:24px;display:grid;gap:20px;}}
.month{{background:#1f2937;border:1px solid #374151;border-radius:18px;padding:20px;}}
.activity{{background:#111827;border:1px solid #374151;border-radius:14px;padding:16px;margin:12px 0;}}
.date{{color:#fbbf24;font-weight:600;}}summary{{cursor:pointer;color:#a7f3d0;}}
ul{{line-height:1.7;}}
</style>
</head>
<body><header><h1>2026营收运营活动图谱</h1><p>页面总数：{len(rows)}，活动数：{len(activities)}，来源：<a href="{html.escape(by_id['452644191']['url'])}">Wiki 根页</a></p></header><main>{"".join(cards)}</main></body></html>"""
    (OUT_DIR / "activity_graph.html").write_text(html_doc, encoding="utf-8")
    print(json.dumps({"months": len(months), "activities": len(activities), "outputs": ["activities.json", "activity_graph.md", "activity_graph.html"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
