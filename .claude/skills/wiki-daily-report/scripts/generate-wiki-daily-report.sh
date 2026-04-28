#!/usr/bin/env bash

set -euo pipefail

WIKI_URL_DEFAULT="https://wiki.inkept.cn/pages/viewpage.action?pageId=448290889"
TARGET_DATE="${1:-$(date +%F)}"
WIKI_URL="${2:-$WIKI_URL_DEFAULT}"

if ! command -v playwright-cli >/dev/null 2>&1; then
  printf 'playwright-cli not found\n' >&2
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  printf 'node not found\n' >&2
  exit 1
fi

TMP_JSON="/tmp/wiki-daily-report-${TARGET_DATE}.json"

playwright-cli list >/dev/null 2>&1 || true

if ! playwright-cli goto "$WIKI_URL" >/dev/null 2>&1; then
  playwright-cli open --persistent --headed "$WIKI_URL" >/dev/null
else
  playwright-cli goto "$WIKI_URL" >/dev/null
fi

playwright-cli --raw eval "(() => {
  const target = '$TARGET_DATE'
  const date = new Date(target)
  if (Number.isNaN(date.getTime())) {
    return JSON.stringify({ error: 'Invalid target date', target })
  }

  const title = document.title || ''
  const monthMatch = title.match(/(\d{4})年(\d{2})月/)
  if (!monthMatch) {
    return JSON.stringify({ error: 'Cannot parse page month from title', title })
  }

  const pageYear = Number(monthMatch[1])
  const pageMonth = Number(monthMatch[2])
  const targetYear = date.getFullYear()
  const targetMonth = date.getMonth() + 1
  const targetDay = String(date.getDate())

  if (pageYear !== targetYear || pageMonth !== targetMonth) {
    return JSON.stringify({
      error: 'Target date is not in current page month',
      title,
      target,
      pageYear,
      pageMonth,
      targetYear,
      targetMonth
    })
  }

  const tables = [...document.querySelectorAll('table')]
  const scheduleTable = tables.find(table => {
    const text = (table.innerText || '').replace(/\s+/g, ' ')
    return text.includes('日期') && text.includes('27') && text.includes('杜振训')
  })
  if (!scheduleTable) {
    return JSON.stringify({ error: 'Cannot find work schedule table', title })
  }

  const rows = [...scheduleTable.querySelectorAll('tr')]
  const headerRow = rows.find(row => {
    const text = (row.textContent || '').replace(/\s+/g, ' ')
    return text.includes('日期') && text.includes('27')
  })
  if (!headerRow) {
    return JSON.stringify({ error: 'Cannot find date header row', title })
  }

  const headerCells = [...headerRow.children].map(cell => (cell.textContent || '').trim())
  const targetIndex = headerCells.findIndex(text => text === targetDay)
  if (targetIndex === -1) {
    return JSON.stringify({ error: 'Cannot find target day column', title, targetDay, headerCells })
  }

  const dataRows = rows.filter(row => row.querySelector('th') || row.querySelector('td'))
  const items = []
  for (const row of dataRows) {
    const rowHeader = row.querySelector('th')
    if (!rowHeader) continue
    const owner = (rowHeader.textContent || '').trim()
    if (!owner || owner === '日期' || owner === '周几') continue
    const cells = [...row.children]
    const cell = cells[targetIndex]
    if (!cell) continue
    const text = (cell.innerText || cell.textContent || '').trim().replace(/\s+/g, ' ')
    if (!text) continue
    items.push({ owner, text })
  }

  return JSON.stringify({
    title,
    target,
    pageYear,
    pageMonth,
    targetDay,
    items
  })
})()" > "$TMP_JSON"

node - "$TMP_JSON" <<'NODE'
const fs = require('fs')

const inputPath = process.argv[2]
let data = JSON.parse(fs.readFileSync(inputPath, 'utf8'))
if (typeof data === 'string') data = JSON.parse(data)

if (data.error) {
  console.error(data.error)
  if (data.title) console.error(`title: ${data.title}`)
  if (data.target) console.error(`target: ${data.target}`)
  process.exit(1)
}

function normalizeSuffix(task) {
  let out = task.replace(/[—–]/g, '-').replace(/\s+/g, ' ').trim()
  out = out.replace(/-{3,}/g, '--')
  out = out.replace(/跟测/g, '--测试')
  out = out.replace(/联调/g, '--开发')
  out = out.replace(/\s*--\s*上线/g, '--上线')
  out = out.replace(/\s*--\s*测试/g, '--测试')
  out = out.replace(/\s*--\s*开发/g, '--开发')
  out = out.replace(/(?<!\d)-上线/g, '--上线')
  out = out.replace(/(?<!\d)-测试/g, '--测试')
  out = out.replace(/(?<!\d)-开发/g, '--开发')
  out = out.replace(/(?<!\d)研发(?![\u4e00-\u9fa5])/g, '--开发')
  out = out.replace(/--开发--开发/g, '--开发')
  out = out.replace(/--测试--测试/g, '--测试')
  out = out.replace(/--上线--上线/g, '--上线')
  out = out.replace(/--开发--上线/g, '--上线')
  out = out.replace(/--开发--测试/g, '--测试')
  out = out.replace(/---上线/g, '--上线')
  out = out.replace(/---测试/g, '--测试')
  out = out.replace(/---开发/g, '--开发')
  if (!/--(上线|测试|开发)$/.test(out)) out += '--开发'
  return out
}

function splitTasks(text) {
  return text
    .split(/(?=\d{1,2}\.\d{1,2}-\d{1,2}\.\d{1,2}|KA\d{1,2}|v\d|PK专属|2026[-年]|长期-|复用-[^\s]|封神令|江湖策|传奇寻珍|迷幻森林奇遇记|派对榜|阿拉丁神灯|五一)/)
    .map(s => s.trim())
    .filter(Boolean)
}

function classify(task) {
  const backendKeywords = ['企微', '公会', 'CRM', 'GOS', 'FSS', '账后调账', '通知消息', '查询', '后台工具', '脚本']
  return backendKeywords.some(k => task.includes(k)) ? '后台' : '活动'
}

const rawItems = []
for (const item of data.items) {
  const tasks = splitTasks(item.text).map(normalizeSuffix)
  rawItems.push({ owner: item.owner, tasks })
}

const merged = { 活动: [], 后台: [] }
const seen = new Set()

for (const item of rawItems) {
  for (const task of item.tasks) {
    const key = task
    if (seen.has(key)) continue
    seen.add(key)
    merged[classify(task)].push(task)
  }
}

const suffixOrder = { '--上线': 0, '--测试': 1, '--开发': 2 }
for (const key of Object.keys(merged)) {
  merged[key].sort((a, b) => {
    const sa = Object.keys(suffixOrder).find(k => a.endsWith(k)) || '--开发'
    const sb = Object.keys(suffixOrder).find(k => b.endsWith(k)) || '--开发'
    return suffixOrder[sa] - suffixOrder[sb]
  })
}

const d = new Date(data.target)
const week = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'][d.getDay()]

console.log(`${d.getMonth() + 1} 月 ${d.getDate()} 日 的工作排期如下：`)
for (const item of rawItems) {
  console.log(`- ${item.owner}：${item.tasks.join('；')}`)
}
console.log('')
console.log(`## ${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日（${week}）工作安排：`)
console.log('活动')
for (const task of merged['活动']) console.log(task)
console.log('')
console.log('后台')
for (const task of merged['后台']) console.log(task)
NODE
