#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

OUT_DIR = Path(__file__).resolve().parent
GRAPHS_DIR = OUT_DIR / "activity_graphs"


def safe_name(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|\s]+", "_", value.strip())
    value = value.strip("._")
    return value[:90] or "untitled"


def node_id(value: str) -> str:
    return "n" + re.sub(r"\D", "", value)


def write_activity_graph(activity: dict[str, Any]) -> dict[str, Any]:
    month = activity["month"]
    date = activity.get("date_range") or "no_date"
    title = activity["name"]
    file_name = f"{month}_{safe_name(date)}_{safe_name(title)}_{activity['page_id']}.md"
    path = GRAPHS_DIR / file_name

    lines = [
        f"# {title} 活动图谱",
        "",
        f"月份：{month}",
        f"活动时间：{activity.get('date_range') or '未识别'}",
        f"活动 Wiki：{activity['url']}",
        f"活动页面 ID：{activity['page_id']}",
        f"关联资料数：{len(activity.get('related_pages', []))}",
        "",
        "## 活动摘要",
        "",
    ]
    summary = activity.get("summary") or []
    if summary:
        lines.extend(f"- {item}" for item in summary)
    else:
        lines.append("- 无正文摘要，详见活动 Wiki。")

    lines.extend(["", "## 关联资料", ""])
    related_pages = activity.get("related_pages", [])
    if related_pages:
        for page in related_pages:
            lines.append(f"- [{page['title']}]({page['url']})")
            lines.append(f"  - 页面 ID：{page['page_id']}")
            lines.append(f"  - 本地 Markdown：`{page['markdown']}`")
    else:
        lines.append("- 无子资料页面。")

    lines.extend(["", "## Mermaid 图谱", "", "```mermaid", "graph TD"])
    month_node = f"m{month.replace('-', '')}"
    activity_node = node_id(activity["page_id"])
    lines.append(f"{month_node}[\"{month}\"] --> {activity_node}[\"{title.replace(chr(34), chr(39))}\"]")
    for page in related_pages:
        rid = node_id(page["page_id"])
        label = page["title"].replace('"', "'")
        lines.append(f"{activity_node} --> {rid}[\"{label}\"]")
    lines.extend(["```", "", "## 原始内容位置", "", f"- 活动主文档：`{activity['markdown']}`"])
    for page in related_pages:
        lines.append(f"- {page['title']}：`{page['markdown']}`")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "activity_title": activity["title"],
        "activity_name": activity["name"],
        "month": month,
        "page_id": activity["page_id"],
        "file_name": file_name,
        "path": str(path.relative_to(OUT_DIR)),
        "url": activity["url"],
        "related_count": len(related_pages),
    }


def main() -> None:
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads((OUT_DIR / "activities.json").read_text(encoding="utf-8"))
    generated = [write_activity_graph(activity) for activity in data["activities"]]
    manifest = {"count": len(generated), "files": generated}
    (OUT_DIR / "activity_graphs_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"count": len(generated), "dir": str(GRAPHS_DIR), "manifest": "activity_graphs_manifest.json"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
