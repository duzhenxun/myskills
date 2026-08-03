#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

OUT_DIR = Path(__file__).resolve().parent
GRAPHS_DIR = OUT_DIR / "activity_graphs_optimized"

SECTION_PATTERNS = [
    ("活动概览", r"活动简介|活动说明|活动目标|需求背景|项目背景|背景|目的|目标"),
    ("活动时间", r"活动时间|统计时间|上线时间|下线时间|时间"),
    ("玩法规则", r"活动规则|玩法|规则|活动逻辑|逻辑|任务|榜单|排名|积分|抽奖|收集"),
    ("奖励与资源", r"奖励|资源|礼物|道具|权益|预算|奖品|发放|配置"),
    ("入口与链接", r"入口|链接|活动中心|直播间|插件|url|URL|页面"),
    ("上线配置", r"上线申请|上线|配置|白名单|测试|排期|需求"),
    ("数据与复盘", r"日报|数据|复盘|效果|消耗|人数|ARPPU|流水|目标|完成度"),
]


def safe_name(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|\s]+", "_", value.strip())
    value = value.strip("._")
    return value[:90] or "untitled"


def node_id(value: str) -> str:
    return "n" + re.sub(r"\D", "", value)


def read_page(markdown_path: str) -> str:
    path = OUT_DIR / markdown_path
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    return "\n".join(lines[1:]).strip() if lines and lines[0].startswith("# ") else text.strip()


def clean_line(line: str) -> str:
    line = re.sub(r"\s+", " ", line.strip())
    line = re.sub(r"^[-*•\d.、\s]+", "", line)
    return line.strip()


def meaningful_lines(text: str) -> list[str]:
    lines = []
    for raw in text.splitlines():
        line = clean_line(raw)
        if not line or len(line) < 4:
            continue
        if re.fullmatch(r"[-|:：\s]+", line):
            continue
        lines.append(line)
    return lines


def collect_by_category(docs: list[dict[str, str]]) -> dict[str, list[str]]:
    categories = {name: [] for name, _ in SECTION_PATTERNS}
    categories["其他关键信息"] = []
    seen: set[str] = set()
    for doc in docs:
        title = doc["title"]
        for line in meaningful_lines(doc["content"]):
            item = f"{line}（来源：{title}）"
            if item in seen:
                continue
            seen.add(item)
            placed = False
            for name, pattern in SECTION_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE) or re.search(pattern, title, re.IGNORECASE):
                    categories[name].append(item)
                    placed = True
                    break
            if not placed and len(categories["其他关键信息"]) < 40:
                categories["其他关键信息"].append(item)
    return categories


def limit_items(items: list[str], limit: int, max_len: int = 220) -> list[str]:
    result = []
    for item in items:
        if len(item) > max_len:
            item = item[: max_len - 1] + "..."
        result.append(item)
        if len(result) >= limit:
            break
    return result


def infer_tags(activity: dict[str, Any], categories: dict[str, list[str]]) -> list[str]:
    blob = "\n".join([activity["name"], activity["title"], *[x for items in categories.values() for x in items[:5]]])
    tags = []
    candidates = [
        ("星座", r"星座|摩羯|水瓶|双鱼|白羊|金牛|双子"),
        ("节日", r"春节|情人节|元宵|女神|五一|六一|端午|527"),
        ("榜单", r"榜单|排名|TOP|总榜"),
        ("礼物", r"礼物|送礼|收礼|小映|钻"),
        ("主播", r"主播|嘉宾|开播|活跃"),
        ("用户", r"用户|送礼人数|付费"),
        ("资源配置", r"资源|配置|上线申请|白名单"),
        ("数据复盘", r"日报|数据|复盘|完成度|消耗"),
    ]
    for tag, pattern in candidates:
        if re.search(pattern, blob, re.IGNORECASE):
            tags.append(tag)
    return tags or ["活动运营"]


def write_activity_graph(activity: dict[str, Any]) -> dict[str, Any]:
    month = activity["month"]
    date = activity.get("date_range") or "no_date"
    title = activity["name"]
    file_name = f"{month}_{safe_name(date)}_{safe_name(title)}_{activity['page_id']}_optimized.md"
    path = GRAPHS_DIR / file_name

    docs = [{"title": "活动主页面", "url": activity["url"], "content": read_page(activity["markdown"])}]
    for page in activity.get("related_pages", []):
        docs.append({"title": page["title"], "url": page["url"], "content": read_page(page["markdown"])})

    categories = collect_by_category(docs)
    tags = infer_tags(activity, categories)

    lines = [
        f"# {title} 活动知识图谱",
        "",
        "## 核心信息",
        "",
        f"- 月份：{month}",
        f"- 活动时间：{activity.get('date_range') or '未识别'}",
        f"- 活动 Wiki：{activity['url']}",
        f"- 活动页面 ID：{activity['page_id']}",
        f"- 关联资料数：{len(activity.get('related_pages', []))}",
        f"- 标签：{'、'.join(tags)}",
        "",
        "## 优化总结",
        "",
    ]

    for section, limit in [
        ("活动概览", 10),
        ("活动时间", 8),
        ("玩法规则", 18),
        ("奖励与资源", 18),
        ("入口与链接", 12),
        ("上线配置", 14),
        ("数据与复盘", 16),
        ("其他关键信息", 10),
    ]:
        items = limit_items(categories.get(section, []), limit)
        if not items:
            continue
        lines.extend([f"### {section}", ""])
        lines.extend(f"- {item}" for item in items)
        lines.append("")

    lines.extend(["## 资料关系图", "", "```mermaid", "graph TD"])
    month_node = f"m{month.replace('-', '')}"
    activity_node = node_id(activity["page_id"])
    lines.append(f"{month_node}[\"{month}\"] --> {activity_node}[\"{title.replace(chr(34), chr(39))}\"]")
    for tag in tags:
        tid = "tag" + safe_name(tag)
        lines.append(f"{activity_node} --> {tid}[\"标签：{tag}\"]")
    for page in activity.get("related_pages", []):
        rid = node_id(page["page_id"])
        label = page["title"].replace('"', "'")
        lines.append(f"{activity_node} --> {rid}[\"{label}\"]")
    lines.extend(["```", ""])

    lines.extend(["## 资料来源", "", f"- [活动主页面]({activity['url']})"])
    for page in activity.get("related_pages", []):
        lines.append(f"- [{page['title']}]({page['url']})")
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
        "related_count": len(activity.get("related_pages", [])),
    }


def main() -> None:
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads((OUT_DIR / "activities.json").read_text(encoding="utf-8"))
    generated = [write_activity_graph(activity) for activity in data["activities"]]
    manifest = {"count": len(generated), "files": generated}
    (OUT_DIR / "activity_graphs_optimized_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"count": len(generated), "dir": str(GRAPHS_DIR), "manifest": "activity_graphs_optimized_manifest.json"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
