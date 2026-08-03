#!/usr/bin/env python3
from __future__ import annotations

import json
import mimetypes
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

OUT_DIR = Path(__file__).resolve().parent
IMA_SKILL_DIR = Path("/Users/dds/.agents/skills/ima-skill")
IMA_API = IMA_SKILL_DIR / "ima_api.cjs"
COS_UPLOAD = IMA_SKILL_DIR / "knowledge-base/scripts/cos-upload.cjs"
PREFLIGHT = IMA_SKILL_DIR / "knowledge-base/scripts/preflight-check.cjs"
KNOWLEDGE_BASE_ID = "1qse3qqKNV3SUn3y7YKsm4BovNX76dNx7g8ayZjjCto="


def run(args: list[str], *, input_text: str | None = None) -> str:
    result = subprocess.run(args, input=input_text, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"Command failed: {args}")
    return result.stdout.strip()


def ima(api_path: str, body: dict[str, Any]) -> dict[str, Any]:
    output = run(["node", str(IMA_API), api_path, json.dumps(body, ensure_ascii=False)])
    data = json.loads(output)
    if data.get("code") != 0:
        raise RuntimeError(data.get("msg") or output)
    return data


def preflight(file_path: Path) -> dict[str, Any]:
    output = run(["node", str(PREFLIGHT), "--file", str(file_path)])
    data = json.loads(output)
    if not data.get("pass"):
        raise RuntimeError(f"{file_path.name}: {data.get('reason')}")
    return data


def check_duplicates(files: list[dict[str, Any]]) -> list[str]:
    params = [{"name": item["file_name"], "media_type": item["media_type"]} for item in files]
    data = ima("openapi/wiki/v1/check_repeated_names", {"params": params, "knowledge_base_id": KNOWLEDGE_BASE_ID})
    return [item["name"] for item in data["data"].get("results", []) if item.get("is_repeated")]


def upload_one(item: dict[str, Any]) -> dict[str, Any]:
    file_path = OUT_DIR / item["path"]
    create = ima(
        "openapi/wiki/v1/create_media",
        {
            "file_name": item["file_name"],
            "file_size": item["file_size"],
            "content_type": item["content_type"],
            "knowledge_base_id": KNOWLEDGE_BASE_ID,
            "file_ext": item["file_ext"],
        },
    )["data"]
    cos = create["cos_credential"]
    run(
        [
            "node",
            str(COS_UPLOAD),
            "--file",
            str(file_path),
            "--secret-id",
            cos["secret_id"],
            "--secret-key",
            cos["secret_key"],
            "--token",
            cos["token"],
            "--bucket",
            cos["bucket_name"],
            "--region",
            cos["region"],
            "--cos-key",
            cos["cos_key"],
            "--content-type",
            item["content_type"],
            "--start-time",
            cos["start_time"],
            "--expired-time",
            cos["expired_time"],
            "--timeout",
            "300000",
        ]
    )
    ima(
        "openapi/wiki/v1/add_knowledge",
        {
            "media_type": item["media_type"],
            "media_id": create["media_id"],
            "title": item["file_name"],
            "knowledge_base_id": KNOWLEDGE_BASE_ID,
            "file_info": {"cos_key": cos["cos_key"], "file_size": item["file_size"], "file_name": item["file_name"]},
        },
    )
    return {**item, "media_id": create["media_id"], "uploaded": True}


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    manifest_name = "activity_graphs_manifest.json"
    result_name = "ima_upload_results.json"
    if "--manifest" in sys.argv:
        manifest_name = sys.argv[sys.argv.index("--manifest") + 1]
    if "--result" in sys.argv:
        result_name = sys.argv[sys.argv.index("--result") + 1]
    sleep_seconds = 0.0
    if "--sleep" in sys.argv:
        sleep_seconds = float(sys.argv[sys.argv.index("--sleep") + 1])
    manifest = json.loads((OUT_DIR / manifest_name).read_text(encoding="utf-8"))
    files = []
    for item in manifest["files"]:
        file_path = OUT_DIR / item["path"]
        info = preflight(file_path)
        files.append(
            {
                **item,
                "file_size": os.path.getsize(file_path),
                "file_ext": info.get("file_ext") or file_path.suffix.lstrip("."),
                "media_type": info["media_type"],
                "content_type": info.get("content_type") or mimetypes.guess_type(file_path.name)[0] or "text/markdown",
            }
        )

    result_path = OUT_DIR / result_name
    uploaded = []
    uploaded_names: set[str] = set()
    if result_path.exists() and "--resume" in sys.argv:
        previous = json.loads(result_path.read_text(encoding="utf-8"))
        uploaded = previous.get("uploaded", [])
        uploaded_names = {item["file_name"] for item in uploaded if item.get("uploaded")}

    files_to_check = [item for item in files if item["file_name"] not in uploaded_names]
    duplicates = check_duplicates(files_to_check) if files_to_check else []
    if duplicates:
        (OUT_DIR / "ima_duplicate_files.json").write_text(json.dumps(duplicates, ensure_ascii=False, indent=2), encoding="utf-8")
        raise RuntimeError(f"IMA already has {len(duplicates)} duplicate file names. See act/ima_duplicate_files.json")
    if dry_run:
        print(json.dumps({"checked": len(files), "duplicates": 0}, ensure_ascii=False))
        return

    failed = []
    for index, item in enumerate(files_to_check, start=1):
        try:
            uploaded.append(upload_one(item))
            print(json.dumps({"uploaded": len(uploaded), "remaining_batch_index": index, "total": len(files), "file_name": item["file_name"]}, ensure_ascii=False), flush=True)
            if sleep_seconds:
                time.sleep(sleep_seconds)
        except Exception as exc:
            failed.append({"file_name": item["file_name"], "error": str(exc)})
            break

    result = {"uploaded_count": len(uploaded), "failed": failed, "uploaded": uploaded}
    (OUT_DIR / result_name).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if failed:
        raise RuntimeError(f"Upload stopped after {len(uploaded)} files: {failed[0]['file_name']} - {failed[0]['error']}")
    print(json.dumps({"uploaded_count": len(uploaded), "result": result_name}, ensure_ascii=False))


if __name__ == "__main__":
    main()
