#!/usr/bin/env node

const { execSync } = require('child_process')
const fs = require('fs')

function usage() {
  console.log(`Usage:
  node extract-comments.js <douyin-url> [output-file]

Examples:
  node extract-comments.js "https://www.douyin.com/jingxuan?modal_id=7632657462063140130"
  node extract-comments.js "https://www.douyin.com/jingxuan?modal_id=7632657462063140130" "/Users/name/Desktop/comments.txt"
`)
}

function run(command) {
  return execSync(command, {
    encoding: 'utf8',
    stdio: ['ignore', 'pipe', 'pipe'],
    maxBuffer: 20 * 1024 * 1024,
  }).trim()
}

function shellQuote(value) {
  return JSON.stringify(value)
}

function sleep(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms)
}

function parseModalId(url) {
  try {
    const u = new URL(url)
    return u.searchParams.get('modal_id') || 'unknown'
  } catch {
    return 'unknown'
  }
}

function buildOutputPath(url, customPath) {
  if (customPath) return customPath
  return `/Users/dds/Desktop/douyin_comments_${parseModalId(url)}.txt`
}

function pwEval(js) {
  return run(`playwright-cli --raw eval ${shellQuote(js)}`)
}

function safeJsonParse(raw, fallback) {
  try {
    return JSON.parse(raw)
  } catch {
    return fallback
  }
}

function ensurePage(url) {
  run(`playwright-cli open --persistent --headed ${shellQuote(url)}`)
  sleep(4000)
}

function activateComments() {
  const titlePrefix = pwEval(`(() => JSON.stringify(document.title.split(' - 抖音')[0].split('#')[0].trim()))()`)
  const titleText = safeJsonParse(titlePrefix, '')

  if (titleText) {
    run(`playwright-cli click ${shellQuote(`text=${titleText}`)}`)
    sleep(2500)
  }

  run(`playwright-cli click ${shellQuote("getByRole('tab', { name: '评论' })")}`)
  sleep(2500)

  const state = pwEval(`(() => (document.body.innerText || '').includes('全部评论(') ? 'READY' : 'MISS')()`)
  if (state !== 'READY') {
    throw new Error('Failed to activate comment panel: 全部评论(...) did not appear')
  }
}

function parseVisible() {
  const raw = pwEval(`(() => {
    const root = [...document.querySelectorAll('*')].find(el =>
      String(el.className || '').includes('comment-mainContent') &&
      el.clientHeight > 200
    )

    if (!root) return JSON.stringify({ items: [], state: { ok: false } })

    const text = root.innerText || ''
    const lines = text.split('\\n').map(s => s.trim()).filter(Boolean)
    const items = []
    const isMeta = s => /^(\\d+小时前|\\d+天前|\\d+分钟前|昨天|今天)/.test(s) || /·/.test(s)
    const skip = s =>
      ['大家都在搜：', 'deepseek v4'].includes(s) ||
      s.startsWith('全部评论(') ||
      s === '留下你的精彩评论吧' ||
      s === '分享' ||
      s === '回复' ||
      s === '展开更多' ||
      s === '收起' ||
      /^展开\\d+条回复$/.test(s) ||
      s === '...'

    for (let i = 0; i < lines.length; i++) {
      const name = lines[i]
      const dot = lines[i + 1]
      const content = lines[i + 2]
      const meta = lines[i + 3]
      if (!name || skip(name) || dot !== '...' || !content || skip(content) || !isMeta(meta || '')) continue

      let likes = ''
      for (let j = i + 4; j < i + 8 && j < lines.length; j++) {
        if (/^\\d+$/.test(lines[j])) {
          likes = lines[j]
          break
        }
      }
      items.push({ name, content, meta, likes })
    }

    return JSON.stringify({
      items,
      state: {
        ok: true,
        scrollTop: root.scrollTop,
        scrollHeight: root.scrollHeight,
        clientHeight: root.clientHeight,
        textLen: text.length,
      }
    })
  })()`)

  return safeJsonParse(raw, { items: [], state: { ok: false, raw } })
}

function scrollOnce() {
  const raw = pwEval(`(() => {
    const root = [...document.querySelectorAll('*')].find(el =>
      String(el.className || '').includes('comment-mainContent') &&
      el.clientHeight > 200
    )

    if (!root) return JSON.stringify({ ok: false })
    const before = root.scrollTop
    root.scrollTop = Math.min(root.scrollTop + root.clientHeight - 30, root.scrollHeight)
    return JSON.stringify({ ok: true, before, after: root.scrollTop, scrollHeight: root.scrollHeight, clientHeight: root.clientHeight })
  })()`)

  return safeJsonParse(raw, { ok: false, raw })
}

function writeOutput(filePath, url, comments) {
  let txt = `Douyin comments for modal_id=${parseModalId(url)}\n`
  txt += `Source: ${url}\n`
  txt += `Extracted comments: ${comments.length}\n\n`

  comments.forEach((c, idx) => {
    txt += `${idx + 1}. ${c.name}\n`
    txt += `评论: ${c.content}\n`
    txt += `时间/地区: ${c.meta}\n`
    txt += `点赞: ${c.likes || 'N/A'}\n\n`
  })

  fs.writeFileSync(filePath, txt, 'utf8')
}

function main() {
  const [, , url, outputArg] = process.argv
  if (!url || url === '--help' || url === '-h') {
    usage()
    process.exit(url ? 0 : 1)
  }

  const outputPath = buildOutputPath(url, outputArg)
  ensurePage(url)
  activateComments()

  const seen = new Map()
  let stableRounds = 0
  let lastCount = 0
  let lastScrollHeight = 0

  for (let round = 0; round < 120; round++) {
    const parsed = parseVisible()
    for (const item of parsed.items || []) {
      const key = `${item.name}\n${item.content}\n${item.meta}`
      if (!seen.has(key)) seen.set(key, item)
    }

    const count = seen.size
    const scrollHeight = parsed.state?.scrollHeight || 0
    if (count === lastCount && scrollHeight === lastScrollHeight) stableRounds += 1
    else stableRounds = 0

    if (stableRounds >= 6) break

    lastCount = count
    lastScrollHeight = scrollHeight

    const moved = scrollOnce()
    if (!moved.ok || moved.after === moved.before) break
    sleep(1200)
  }

  const comments = [...seen.values()]
  writeOutput(outputPath, url, comments)
  console.log(JSON.stringify({ count: comments.length, outputPath }, null, 2))
}

main()
