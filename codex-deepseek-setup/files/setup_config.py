#!/usr/bin/env python3
"""Rewrite codex config.toml + the model catalog for the DeepSeek adapter.

Deliberately does a surgical *text* edit instead of a TOML round-trip: a real
config.toml is full of user comments and ordering that a parse/dump cycle would
destroy. Every change is idempotent, so re-running install.sh is safe.

Changes:
  1. a managed block at the top with the active model settings
     (conflicting pre-existing top-level keys are tagged, not deleted)
  2. [model_providers.<provider>] pointing at the local adapter
  3. optionally repoint a legacy provider (default name: OpenAI) at the adapter
  4. the model catalog, with slugs patched to the requested models
"""

import argparse
import json
import os
import re
import shutil
import sys
import time

BEGIN = "# >>> codex-deepseek: managed block (rewritten by install.sh) >>>"
END = "# <<< codex-deepseek: end managed block <<<"
TAG = "#[codex-deepseek:disabled] "
TOP_KEYS = ("model_provider", "model", "review_model", "model_catalog_json",
            "web_search", "disable_response_storage")
MANAGED_PROVIDER_KEYS = ("name", "base_url", "wire_api", "experimental_bearer_token")


def warn(msg):
    print("  ! " + msg, file=sys.stderr)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write(path, text):
    tmp = path + ".codex-deepseek.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)


def backup(path):
    if not os.path.exists(path):
        return None
    dest = "%s.bak-%s" % (path, time.strftime("%Y%m%d%H%M%S"))
    shutil.copy2(path, dest)
    return dest


def first_table_index(lines):
    for i, line in enumerate(lines):
        if re.match(r"^\s*\[", line):
            return i
    return len(lines)


def strip_managed_block(lines):
    out = []
    inside = False
    for line in lines:
        s = line.strip()
        if s == BEGIN:
            inside = True
            continue
        if inside:
            if s == END:
                inside = False
            continue
        out.append(line)
    return out


def managed_block(catalog_path, model, model_alt):
    block = [
        BEGIN,
        'model_provider = "deepseek"',
        'model = "%s"' % model,
        'review_model = "%s"' % (model_alt or model),
        'model_catalog_json = "%s"' % catalog_path,
        'web_search = "disabled"',
        "# The catalog above only lists the open models, so when switching back to a",
        "# gpt-* model comment out model_catalog_json + web_search as well, then restore",
        "# the tagged lines below.",
        END,
    ]
    return block


def apply_top_block(lines, block):
    """Put `block` at the top and tag any conflicting top-level assignment."""
    lines = strip_managed_block(lines)
    split = first_table_index(lines)
    top, rest = lines[:split], lines[split:]

    tagged = []
    for line in top:
        s = line.strip()
        if s.startswith(TAG.strip()):
            tagged.append(line)
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=", line)
        if m and m.group(1) in TOP_KEYS:
            tagged.append(TAG + line.lstrip())
        else:
            tagged.append(line)

    while tagged and not tagged[-1].strip():
        tagged.pop()
    while tagged and not tagged[0].strip():
        tagged.pop(0)

    out = list(block) + [""]
    if tagged:
        out += ["# --- previous settings, tagged by install.sh (uncomment to revert) ---"]
        out += tagged + [""]
    out += rest
    return out


def provider_extent(lines, header):
    start = None
    for i, line in enumerate(lines):
        if line.strip() == header:
            start = i
            break
    if start is None:
        return None, None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^\s*\[", lines[j]):
            end = j
            break
    return start, end


def set_provider(lines, name, values, create_only=None):
    """Create or update [model_providers.<name>] with the given key/value pairs.

    `create_only` holds extra keys (e.g. the required `name`) that must be
    present when the table is created but must not be touched when it already
    exists because the user may have customised them.
    """
    create_only = create_only or {}
    header = "[model_providers.%s]" % name
    start, end = provider_extent(lines, header)
    if start is None:
        block = [header]
        merged = dict(create_only)
        merged.update(values)
        block += ['%s = %s' % (k, json.dumps(v)) for k, v in merged.items()]
        if lines and lines[-1].strip():
            lines.append("")
        lines += block + [""]
        return lines, "added"

    body = lines[start + 1:end]
    seen = set()
    new_body = []
    for line in body:
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=", line)
        if m and m.group(1) in values:
            key = m.group(1)
            new_body.append("%s = %s" % (key, json.dumps(values[key])))
            seen.add(key)
        else:
            new_body.append(line)
    missing = [k for k in values if k not in seen]
    if missing:
        # insert right after the header, before any blank line
        insert_at = 0
        while insert_at < len(new_body) and not new_body[insert_at].strip():
            insert_at += 1
        new_body[insert_at:insert_at] = ['%s = %s' % (k, json.dumps(values[k])) for k in missing]
    return lines[:start + 1] + new_body + lines[end:], "updated"


def patch_catalog(src, dest, model, model_alt):
    with open(src, encoding="utf-8") as fh:
        catalog = json.load(fh)
    models = catalog["models"]
    models[0]["slug"] = model
    models[0]["display_name"] = model
    if model_alt:
        models[1]["slug"] = model_alt
        models[1]["display_name"] = model_alt
    else:
        del models[1:]
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(catalog, fh, ensure_ascii=False)
    return [m["slug"] for m in models]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--codex-home", required=True)
    ap.add_argument("--key", required=True, help="bearer token stored in the provider block")
    ap.add_argument("--adapter-url", required=True, help="e.g. http://127.0.0.1:8899")
    ap.add_argument("--model", required=True)
    ap.add_argument("--model-alt", default="")
    ap.add_argument("--catalog-src", default="")
    ap.add_argument("--repoint-provider", default="",
                    help="extra provider id to point at the adapter, e.g. OpenAI")
    args = ap.parse_args()

    home = os.path.expanduser(args.codex_home)
    config_path = os.path.join(home, "config.toml")
    catalog_path = os.path.join(home, "models.json")

    # ---- config.toml ----
    text = read(config_path) if os.path.exists(config_path) else ""
    lines = text.split("\n")

    lines = apply_top_block(lines, managed_block(catalog_path, args.model, args.model_alt))
    lines, how = set_provider(lines, "deepseek", {
        "name": "deepseek",
        "base_url": args.adapter_url,
        "wire_api": "responses",
        "experimental_bearer_token": args.key,
    })
    print("  provider deepseek: %s" % how)

    if args.repoint_provider:
        # Legacy threads recorded this provider id; the adapter routes model -> key,
        # so pointing it here keeps old threads working without touching history.
        lines, how = set_provider(
            lines, args.repoint_provider,
            {"base_url": args.adapter_url, "wire_api": "responses"},
            create_only={"name": args.repoint_provider},
        )
        print("  provider %s: %s -> adapter" % (args.repoint_provider, how))

    bkp = backup(config_path)
    write(config_path, "\n".join(lines).rstrip("\n") + "\n")
    print("  config.toml written%s" % (" (backup: %s)" % os.path.basename(bkp) if bkp else ""))

    # ---- catalog ----
    if args.catalog_src:
        slugs = patch_catalog(args.catalog_src, catalog_path, args.model, args.model_alt)
        print("  models.json: %s" % ", ".join(slugs))


if __name__ == "__main__":
    main()
