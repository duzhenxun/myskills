#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import sys
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

WIKI_SKILL_DIR = Path("/Users/dds/.agents/skills/wiki-skill")
sys.path.insert(0, str(WIKI_SKILL_DIR))

from confluence import ConfluenceClient, load_config  # noqa: E402

ROOT_ID = "452644191"
OUT_DIR = Path(__file__).resolve().parent
PAGES_DIR = OUT_DIR / "pages"


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"p", "br", "div", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data)

    def text(self) -> str:
        text = html.unescape("".join(self.parts))
        text = re.sub(r"[ \t\r\f\v]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        return text.strip() + "\n" if text.strip() else ""


def safe_name(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|\s]+", "_", value.strip())
    value = value.strip("._")
    return value[:80] or "untitled"


def storage_to_markdown(title: str, storage: str) -> str:
    parser = TextExtractor()
    parser.feed(storage or "")
    text = parser.text()
    return f"# {title}\n\n{text}"


def get_children(client: ConfluenceClient, content_id: str) -> list[dict[str, Any]]:
    children: list[dict[str, Any]] = []
    start = 0
    limit = 100
    while True:
        data = client.request(
            "GET",
            f"/content/{content_id}/child/page",
            query={"start": start, "limit": limit, "expand": "version,space"},
        )
        results = data.get("results", [])
        children.extend(results)
        size = int(data.get("size", len(results)))
        if size < limit:
            return children
        start += size


def fetch_page(client: ConfluenceClient, content_id: str) -> dict[str, Any]:
    return client.get_content(content_id, expand=["body.storage", "version", "space", "ancestors"])


def save_page(page: dict[str, Any], depth: int, parent_id: str | None) -> dict[str, Any]:
    page_id = str(page["id"])
    title = page.get("title", "untitled")
    storage = page.get("body", {}).get("storage", {}).get("value", "")
    base = f"{depth:02d}_{safe_name(title)}_{page_id}"
    page_dir = PAGES_DIR / base
    page_dir.mkdir(parents=True, exist_ok=True)

    raw_path = page_dir / "page.json"
    html_path = page_dir / "content.html"
    md_path = page_dir / "content.md"

    raw_path.write_text(json.dumps(page, ensure_ascii=False, indent=2), encoding="utf-8")
    html_path.write_text(storage, encoding="utf-8")
    md_path.write_text(storage_to_markdown(title, storage), encoding="utf-8")

    links = page.get("_links", {})
    web_url = urllib.parse.urljoin(links.get("base", ""), links.get("webui", ""))
    return {
        "id": page_id,
        "parent_id": parent_id,
        "depth": depth,
        "title": title,
        "version": page.get("version", {}).get("number"),
        "space": page.get("space", {}).get("key"),
        "url": web_url,
        "files": {
            "json": str(raw_path.relative_to(OUT_DIR)),
            "html": str(html_path.relative_to(OUT_DIR)),
            "markdown": str(md_path.relative_to(OUT_DIR)),
        },
        "children": [],
    }


def walk(client: ConfluenceClient, content_id: str, depth: int = 0, parent_id: str | None = None) -> dict[str, Any]:
    page = fetch_page(client, content_id)
    node = save_page(page, depth, parent_id)
    for child in get_children(client, content_id):
        node["children"].append(walk(client, str(child["id"]), depth + 1, str(content_id)))
    return node


def flatten(node: dict[str, Any]) -> list[dict[str, Any]]:
    current = {k: v for k, v in node.items() if k != "children"}
    rows = [current]
    for child in node.get("children", []):
        rows.extend(flatten(child))
    return rows


def main() -> None:
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    client = ConfluenceClient(load_config())
    tree = walk(client, ROOT_ID)
    pages = flatten(tree)
    (OUT_DIR / "wiki_tree.json").write_text(json.dumps(tree, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "pages_index.json").write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"root_id": ROOT_ID, "page_count": len(pages), "out_dir": str(OUT_DIR)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
