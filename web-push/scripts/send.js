'use strict';
/**
 * 可选：向 subscriptions.json 里的订阅发送一条测试推送（验证端到端链路）
 * 依赖 web-push 包：npm i web-push
 * 用法: node scripts/send.js "标题" "内容"
 *      VAPID_PRIVATE_KEY / VAPID_PUBLIC_KEY / VAPID_SUBJECT 可用环境变量覆盖
 */
const fs = require('node:fs');
const path = require('node:path');

const PRIVATE_KEY = process.env.VAPID_PRIVATE_KEY || 'UArGsIjinVV7Lk0g3zOdkMctvWIoTzUT8jV2vayiOyQ';
const PUBLIC_KEY =
  process.env.VAPID_PUBLIC_KEY ||
  'BPnvp8p4QdnOh4vO6-oAhxFGouHJTqY68C_4-goxBh1sphBEb1blz2FgqyEVg5JoFMBdSJKu2tDR-VLkdUNIHrQ';
const SUBJECT = process.env.VAPID_SUBJECT || 'mailto:admin@example.com';

let webpush;
try {
  webpush = require('web-push');
} catch {
  console.error('缺少依赖，请先执行:  npm i web-push');
  process.exit(1);
}

const store = path.join(__dirname, '..', 'subscriptions.json');
if (!fs.existsSync(store)) {
  console.error('找不到 subscriptions.json，请先在网页上点击「注册推送」。');
  process.exit(1);
}
const subs = JSON.parse(fs.readFileSync(store, 'utf8'));
if (!subs.length) {
  console.error('subscriptions.json 里没有订阅记录。');
  process.exit(1);
}

webpush.setVapidDetails(SUBJECT, PUBLIC_KEY, PRIVATE_KEY);

const title = process.argv[2] || '测试推送';
const body = process.argv[3] || `来自 web-push-demo 的测试推送 ${new Date().toLocaleString()}`;
const payload = JSON.stringify({ title, body, url: '/' });

(async () => {
  let ok = 0;
  const keep = [];
  for (const sub of subs) {
    try {
      await webpush.sendNotification({ endpoint: sub.endpoint, keys: sub.keys }, payload);
      console.log('✓ 发送成功:', sub.endpoint.slice(0, 70) + '…');
      ok++;
      keep.push(sub);
    } catch (err) {
      console.error('✗ 发送失败', err.statusCode || '', err.body || err.message);
      if (![404, 410].includes(err.statusCode)) keep.push(sub); // 失效订阅丢弃
    }
  }
  if (keep.length !== subs.length) {
    fs.writeFileSync(store, JSON.stringify(keep, null, 2));
    console.log(`已清理 ${subs.length - keep.length} 条失效订阅`);
  }
  console.log(`完成：成功 ${ok}/${subs.length}`);
})();
