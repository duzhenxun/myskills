async page => {
  await page.goto("https://www.douyin.com/jingxuan?modal_id=7632657462063140130", { waitUntil: 'domcontentloaded' })
  await page.waitForTimeout(4000)
  const commentTab = page.locator('text=评论').first()
  if (await commentTab.count()) {
    await commentTab.click()
    await page.waitForTimeout(2500)
  }
  const seen = new Map()
  const parsed = await page.evaluate(() => {
    const root = [...document.querySelectorAll('*')].find(el => String(el.className || '').includes('comment-mainContent') && el.clientHeight > 200)
    if (!root) return { items: [], state: { ok: false } }
    const text = root.innerText || ''
    return { items: [{ sample: text.slice(0, 500) }], state: { ok: true, len: text.length } }
  })
  console.log(JSON.stringify(parsed, null, 2))
}