#!/usr/bin/env python3
"""Browse the exchanges the adapter captured (Codex request <-> DeepSeek reply).

Usage:
  ./captures.py                 last 20 exchanges, newest first
  ./captures.py -n 50           more rows
  ./captures.py --errors        only failed / non-200 exchanges
  ./captures.py --show 1        print the full .txt of the newest exchange
  ./captures.py --grep chmod    search all captured text

Env: CODEX_ADAPTER_CAPTURE_DIR overrides the default directory.
"""

import argparse
import json
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.environ.get("CODEX_ADAPTER_SETTINGS", os.path.join(BASE_DIR, "settings.json"))


def _capture_dir():
    """Env var, else settings.json written by install.sh, else the default."""
    if os.environ.get("CODEX_ADAPTER_CAPTURE_DIR"):
        return os.environ["CODEX_ADAPTER_CAPTURE_DIR"]
    try:
        with open(SETTINGS_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and data.get("capture_dir"):
            return data["capture_dir"]
    except Exception:
        pass
    return os.path.join(BASE_DIR, "logs", "exchanges")


CAPTURE_DIR = _capture_dir()


def files():
    """All captured .json files, newest first."""
    found = []
    for root, _dirs, names in os.walk(CAPTURE_DIR):
        for name in names:
            if name.endswith(".json"):
                found.append(os.path.join(root, name))
    found.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return found


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def preview(text, limit=58):
    text = (text or "").replace("\n", " ").strip()
    return text[:limit] + ("…" if len(text) > limit else "")


def cmd_list(rows, errors_only, as_json):
    picked = []
    for path in files():
        record = load(path)
        if record is None:
            continue
        if errors_only and not (record.get("error") or record.get("status") != 200
                                or (record.get("response") or {}).get("errors")):
            continue
        picked.append((path, record))
        if len(picked) >= rows:
            break
    if as_json:
        print(json.dumps([dict({k: r.get(k) for k in ("started_at", "status", "model", "adapter_note",
                                                      "duration_ms", "request_bytes", "response_bytes",
                                                      "error")},
                               file=os.path.relpath(p, CAPTURE_DIR)) for p, r in picked],
                         ensure_ascii=False, indent=2))
        return 0
    if not picked:
        print("no captures in %s" % CAPTURE_DIR)
        return 1
    print("%-19s %-5s %-22s %8s %9s %9s  %s" % (
        "started", "http", "model", "ms", "req B", "resp B", "reply"))
    for path, record in picked:
        note = record.get("adapter_note") or ""
        if "passthrough" in note:
            note = "passthrough"
        else:
            note = note.split("effort=")[-1].split()[0] if "effort=" in note else "-"
        print("%-19s %-5s %-22s %8s %9s %9s  %s" % (
            record.get("started_at"), record.get("status"), (record.get("model") or "-")[:22],
            record.get("duration_ms"), record.get("request_bytes"), record.get("response_bytes"),
            preview((record.get("response") or {}).get("text")) or "-"))
        if record.get("error"):
            print("%-19s   ^ error: %s" % ("", record["error"]))
    print("\n%d shown · dir %s · ./captures.py --show 1 for the full text" % (len(picked), CAPTURE_DIR))
    return 0


def cmd_show(index):
    path = files()[index - 1]
    text_path = path[:-5] + ".txt"
    if not os.path.exists(text_path):
        print("no readable rendering next to %s" % path, file=sys.stderr)
        return 1
    with open(text_path, encoding="utf-8") as fh:
        sys.stdout.write(fh.read())
    return 0


def cmd_grep(pattern):
    needle = pattern.lower()
    hits = 0
    for path in files():
        text_path = path[:-5] + ".txt"
        if not os.path.exists(text_path):
            continue
        with open(text_path, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
        matched = [(i, line) for i, line in enumerate(lines) if needle in line.lower()]
        if not matched:
            continue
        hits += 1
        print("=== %s (%d hits)" % (os.path.relpath(text_path, CAPTURE_DIR), len(matched)))
        for i, line in matched[:6]:
            print("  %4d: %s" % (i + 1, line[:160]))
    if not hits:
        print("no match for %r in %s" % (pattern, CAPTURE_DIR))
        return 1
    return 0


def main():
    ap = argparse.ArgumentParser(description="Browse captured Codex <-> DeepSeek exchanges")
    ap.add_argument("-n", "--rows", type=int, default=20, help="how many rows (default 20)")
    ap.add_argument("--errors", action="store_true", help="only failed / non-200 exchanges")
    ap.add_argument("--show", type=int, metavar="N", help="print the .txt of the Nth newest")
    ap.add_argument("--grep", metavar="PATTERN", help="search captured text")
    ap.add_argument("--json", action="store_true", help="machine-readable listing")
    args = ap.parse_args()

    if not os.path.isdir(CAPTURE_DIR):
        print("no capture directory yet: %s" % CAPTURE_DIR, file=sys.stderr)
        return 1
    if args.grep:
        return cmd_grep(args.grep)
    if args.show:
        return cmd_show(args.show)
    return cmd_list(args.rows, args.errors, args.json)


if __name__ == "__main__":
    sys.exit(main())
