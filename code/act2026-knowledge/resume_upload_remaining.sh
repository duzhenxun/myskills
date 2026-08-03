#!/usr/bin/env bash
set -euo pipefail

node - <<'NODE'
const fs = require('fs');
const path = require('path');
const {spawnSync} = require('child_process');

const api = '/Users/dds/.agents/skills/ima-skill/ima_api.cjs';
const dir = '/Users/dds/data/ai/work/code/act2026-knowledge';
const kb = 'nB9Pe0Bep4mGREntD_R9YiuUxKih4ESsOXcXabB3du4=';
const summaryPath = path.join(dir, 'ima-note-add-summary.json');

function wait(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

function run(cmd, args) {
  const r = spawnSync(cmd, args, {encoding: 'utf8', maxBuffer: 50 * 1024 * 1024});
  if (r.status !== 0) throw new Error((r.stderr || r.stdout || 'command failed').trim());
  return r.stdout.trim();
}

function apiCall(route, body) {
  const out = run('node', [api, route, JSON.stringify(body)]);
  const res = JSON.parse(out);
  if (res.code !== 0) throw new Error(`${route}: ${res.msg || out}`);
  return res.data;
}

let summary = JSON.parse(fs.readFileSync(summaryPath, 'utf8'));
let pending = summary.note_failed_files.map(x => x.file);
const newlyOk = [];
const stillFailed = [];

for (const fileName of pending) {
  const file = path.join(dir, fileName);
  const title = fileName.replace(/\.md$/, '');
  const content = fs.readFileSync(file, 'utf8');
  let done = false;
  for (let attempt = 1; attempt <= 3 && !done; attempt++) {
    try {
      const search = apiCall('openapi/wiki/v1/search_knowledge', {query: title, knowledge_base_id: kb, cursor: ''});
      const exists = (search.info_list || []).some(x => x.title === title || x.title === fileName);
      if (exists) {
        console.log(`SKIP existing ${fileName}`);
        newlyOk.push(fileName);
        done = true;
        break;
      }
      const imported = apiCall('openapi/note/v1/import_doc', {title, content_format: 1, content});
      const noteId = imported.note_id || imported.content_id || imported.id;
      if (!noteId) throw new Error('import_doc succeeded without note_id');
      apiCall('openapi/wiki/v1/add_knowledge', {media_type: 11, note_info: {content_id: noteId}, title, knowledge_base_id: kb});
      console.log(`OK ${fileName}`);
      newlyOk.push(fileName);
      done = true;
    } catch (e) {
      const msg = e.message || String(e);
      if (attempt < 3 && /频率|限频|超限|Too Many|timeout|ECONNRESET|ETIMEDOUT/i.test(msg)) {
        console.error(`retry ${attempt} ${fileName}: ${msg}`);
        wait(30000 * attempt);
      } else {
        console.error(`FAIL ${fileName}: ${msg}`);
        stillFailed.push({file: fileName, error: msg});
        done = true;
      }
    }
  }
}

summary.note_ok_files = Array.from(new Set([...(summary.note_ok_files || []), ...newlyOk]));
summary.note_failed_files = stillFailed;
summary.note_add_ok = summary.note_ok_files.length;
summary.note_add_fail = stillFailed.length;
fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));

console.log(JSON.stringify({newly_ok: newlyOk.length, remaining_failed: stillFailed.length}, null, 2));
if (stillFailed.length) process.exit(2);
NODE
