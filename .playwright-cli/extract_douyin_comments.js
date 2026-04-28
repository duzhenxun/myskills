async page => {
  await page.goto('https://www.douyin.com/jingxuan?modal_id=7632657462063140130', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(4000);
  const tab = page.locator('text=评论').first();
  if (await tab.count()) await tab.click();
  await page.waitForTimeout(2500);
  const seen = new Map();
  const parseVisible = async () => await page.evaluate(() => {
    const root = [...document.querySelectorAll('*')].find(el => String(el.className||'').includes('comment-mainContent') && el.clientHeight > 200);
    if (!root) return { items: [], state: null };
    const text = root.innerText || '';
    const lines = text.split('\n').map(s => s.trim()).filter(Boolean);
    const items = [];
    const isMeta = s => /^(\d+小时前|\d+天前|\d+分钟前|昨天|今天)/.test(s) || /·/.test(s);
    const skip = s => ['大家都在搜：','deepseek v4'].includes(s) || s.startsWith('全部评论(') || s === '留下你的精彩评论吧' || s === '分享' || s === '回复' || s === '展开更多' || s === '收起' || /^展开\d+条回复$/.test(s) || s === '...';
    for (let i = 0; i < lines.length; i++) {
      const name = lines[i], dot = lines[i+1], content = lines[i+2], meta = lines[i+3];
      if (!name || skip(name) || dot !== '...' || !content || skip(content) || !isMeta(meta || '')) continue;
      let likes = '';
      for (let j = i + 4; j < i + 8 && j < lines.length; j++) if (/^\d+$/.test(lines[j])) { likes = lines[j]; break; }
      items.push({ name, content, meta, likes });
    }
    return { items, state: { scrollTop: root.scrollTop, scrollHeight: root.scrollHeight, clientHeight: root.clientHeight, textLen: text.length } };
  });
  for (let round = 0; round < 80; round++) {
    const parsed = await parseVisible();
    for (const item of parsed.items) {
      const key = item.name + '\n' + item.content + '\n' + item.meta;
      if (!seen.has(key)) seen.set(key, item);
    }
    const moved = await page.evaluate(() => {
      const root = [...document.querySelectorAll('*')].find(el => String(el.className||'').includes('comment-mainContent') && el.clientHeight > 200);
      if (!root) return { ok: false };
      const before = root.scrollTop;
      root.scrollTop = Math.min(root.scrollTop + root.clientHeight - 30, root.scrollHeight);
      return { ok: true, before, after: root.scrollTop, scrollHeight: root.scrollHeight, clientHeight: root.clientHeight };
    });
    if (!moved.ok) break;
    await page.waitForTimeout(1200);
    if (moved.after === moved.before) break;
  }
  const result = [...seen.values()];
  console.log(JSON.stringify(result, null, 2));
}