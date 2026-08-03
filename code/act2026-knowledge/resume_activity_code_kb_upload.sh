#!/usr/bin/env bash
set -euo pipefail

node - <<'NODE'
const fs = require('fs');
const path = require('path');
const {spawnSync} = require('child_process');

const api = '/Users/dds/.agents/skills/ima-skill/ima_api.cjs';
const dir = '/Users/dds/data/ai/work/code/act2026-knowledge';
const kb = 'YBb5exANmQqWXwnmzUkfTqwaEbOP5HK3o940o_5sdzo=';
const outPath = path.join(dir, 'activity-code-kb-upload-summary.json');

function wait(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

function run(cmd, args) {
  const r = spawnSync(cmd, args, {encoding: 'utf8', maxBuffer: 80 * 1024 * 1024});
  if (r.status !== 0) throw new Error((r.stderr || r.stdout || 'command failed').trim());
  return r.stdout.trim();
}

function apiCall(route, body) {
  const out = run('node', [api, route, JSON.stringify(body)]);
  const res = JSON.parse(out);
  if (res.code !== 0) throw new Error(`${route}: ${res.msg || out}`);
  return res.data;
}

let summary = JSON.parse(fs.readFileSync(outPath, 'utf8'));
let ok = summary.ok_files || [];
let pending = (summary.failed_files || []).map(x => x.file).filter(x => !ok.includes(x));
let fail = [];
let noteCreatedButNotAdded = summary.note_created_but_not_added || [];

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
        ok.push(fileName);
        console.log(`OK ${ok.length} ${fileName} existing`);
        done = true;
        break;
      }
      const imported = apiCall('openapi/note/v1/import_doc', {title, content_format: 1, content});
      const noteId = imported.note_id || imported.content_id || imported.id;
      if (!noteId) throw new Error('import_doc succeeded without note_id');
      try {
        apiCall('openapi/wiki/v1/add_knowledge', {media_type: 11, note_info: {content_id: noteId}, title, knowledge_base_id: kb});
      } catch (addErr) {
        noteCreatedButNotAdded.push({file: fileName, title, note_id: noteId, error: addErr.message});
        throw addErr;
      }
      ok.push(fileName);
      console.log(`OK ${ok.length} ${fileName} note`);
      done = true;
    } catch (e) {
      const msg = e.message || String(e);
      if (attempt < 3 && /频率|限频|超限|Too Many|timeout|ECONNRESET|ETIMEDOUT/i.test(msg) && !/请求超量，请明日再试/.test(msg)) {
        console.error(`retry ${attempt} ${fileName}: ${msg}`);
        wait(30000 * attempt);
      } else {
        fail.push({file: fileName, error: msg});
        console.error(`FAIL ${fileName}: ${msg}`);
        done = true;
      }
    }
  }
  fs.writeFileSync(outPath, JSON.stringify({ok: ok.length, fail: fail.length, ok_files: ok, failed_files: fail, note_created_but_not_added: noteCreatedButNotAdded}, null, 2));
  if (fail.length && /请求超量，请明日再试/.test(fail[fail.length - 1].error)) {
    break;
  }
}

const remaining = pending.filter(f => !ok.includes(f) && !fail.some(x => x.file === f));
const finalSummary = {
  ok: ok.length,
  fail: fail.length + remaining.length,
  ok_files: ok,
  failed_files: [...fail, ...remaining.map(file => ({file, error: 'not attempted after quota limit'}))],
  note_created_but_not_added: noteCreatedButNotAdded,
};
fs.writeFileSync(outPath, JSON.stringify(finalSummary, null, 2));
console.log(JSON.stringify({ok: finalSummary.ok, remaining: finalSummary.fail}, null, 2));
if (finalSummary.fail) process.exit(2);
NODE
