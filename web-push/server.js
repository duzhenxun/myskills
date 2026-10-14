'use strict';

/**
 * 零依赖静态服务器 + 订阅收集接口
 * 默认端口 25259
 *
 * 启动: node server.js   (或 npm start)
 * 可用环境变量:
 *   PORT=25259        端口
 *   HTTPS=1           使用 certs/server.crt + certs/server.key 开启 https
 *                     (手机等非 localhost 访问必须 https；先生成自签证书: npm run cert)
 */

const http = require('node:http');
const https = require('node:https');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');

const PORT = Number(process.env.PORT || 25259);
const HOST = process.env.HOST || '0.0.0.0';
const ROOT = path.join(__dirname, 'public');
const STORE = path.join(__dirname, 'subscriptions.json');

/* ---- VAPID（私钥仅服务端持有，可用环境变量覆盖） ---- */
const VAPID_PUBLIC_KEY =
  process.env.VAPID_PUBLIC_KEY ||
  'BPnvp8p4QdnOh4vO6-oAhxFGouHJTqY68C_4-goxBh1sphBEb1blz2FgqyEVg5JoFMBdSJKu2tDR-VLkdUNIHrQ';
const VAPID_PRIVATE_KEY =
  process.env.VAPID_PRIVATE_KEY || 'UArGsIjinVV7Lk0g3zOdkMctvWIoTzUT8jV2vayiOyQ';
const VAPID_SUBJECT = process.env.VAPID_SUBJECT || 'mailto:admin@example.com';

let webpush = null;
let webpushError = null;
try {
  webpush = require('web-push');
  webpush.setVapidDetails(VAPID_SUBJECT, VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY);
} catch (e) {
  webpushError = e.message;
}

const deviceId = (endpoint) => crypto.createHash('sha1').update(endpoint).digest('hex').slice(0, 8);

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.ico': 'image/x-icon',
  '.webmanifest': 'application/manifest+json; charset=utf-8',
};

function readStore() {
  let list = [];
  try {
    const data = JSON.parse(fs.readFileSync(STORE, 'utf8'));
    if (Array.isArray(data)) list = data;
  } catch {
    list = [];
  }
  // 兼容早期没有 id/label 的记录
  return list.map((s) => ({
    ...s,
    id: s.id || deviceId(s.endpoint),
    label: s.label || guessLabel(s.userAgent || ''),
    savedAt: s.savedAt || null,
  }));
}

function guessLabel(ua) {
  const os = /iPhone|iPad|iPod/i.test(ua)
    ? 'iOS'
    : /Android/i.test(ua)
      ? 'Android'
      : /Mac OS X/i.test(ua)
        ? 'macOS'
        : /Windows/i.test(ua)
          ? 'Windows'
          : /Linux/i.test(ua)
            ? 'Linux'
            : '未知系统';
  const br = /Edg\//.test(ua)
    ? 'Edge'
    : /OPR\//.test(ua)
      ? 'Opera'
      : /Chrome\//.test(ua)
        ? 'Chrome'
        : /Safari\//.test(ua)
          ? 'Safari'
          : /Firefox\//.test(ua)
            ? 'Firefox'
            : '未知浏览器';
  return `${os} · ${br}`;
}

function writeStore(list) {
  fs.writeFileSync(STORE, JSON.stringify(list, null, 2));
}

function sendJson(res, status, body) {
  const buf = Buffer.from(JSON.stringify(body, null, 2));
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': buf.length,
    'Cache-Control': 'no-store',
  });
  res.end(buf);
}

function readBody(req, limit = 256 * 1024) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', (c) => {
      size += c.length;
      if (size > limit) {
        reject(new Error('body too large'));
        req.destroy();
        return;
      }
      chunks.push(c);
    });
    req.on('end', () => {
      const raw = Buffer.concat(chunks).toString('utf8');
      if (!raw) return resolve(null);
      try {
        resolve(JSON.parse(raw));
      } catch {
        reject(new Error('invalid json'));
      }
    });
    req.on('error', reject);
  });
}

function serveStatic(req, res, pathname) {
  const rel = pathname === '/' ? 'index.html' : decodeURIComponent(pathname).replace(/^\/+/, '');
  const file = path.resolve(ROOT, rel);
  if (!file.startsWith(ROOT)) {
    res.writeHead(403).end('Forbidden');
    return;
  }
  fs.stat(file, (err, stat) => {
    if (err || !stat.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('404 Not Found');
      return;
    }
    res.writeHead(200, {
      'Content-Type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream',
      'Content-Length': stat.size,
      // service worker / js 不缓存，方便调试
      'Cache-Control': 'no-cache',
      // 允许 SW 作用域覆盖整站
      'Service-Worker-Allowed': '/',
    });
    fs.createReadStream(file).pipe(res);
  });
}

async function handle(req, res) {
  const url = new URL(req.url, 'http://localhost');
  const { pathname } = url;

  // ---- API ----
  if (pathname === '/api/subscribe' && req.method === 'POST') {
    let body;
    try {
      body = await readBody(req);
    } catch (e) {
      return sendJson(res, 400, { ok: false, error: e.message });
    }
    if (!body || !body.endpoint) {
      return sendJson(res, 400, { ok: false, error: '缺少 subscription.endpoint' });
    }
    const list = readStore();
    const existing = list.find((x) => x.endpoint === body.endpoint);
    const entry = {
      id: deviceId(body.endpoint),
      label: (body.label || existing?.label || guessLabel(req.headers['user-agent'] || '')).slice(0, 60),
      endpoint: body.endpoint,
      keys: body.keys || existing?.keys || null,
      expirationTime: body.expirationTime ?? null,
      userAgent: req.headers['user-agent'] || '',
      savedAt: existing?.savedAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      lastPushAt: existing?.lastPushAt || null,
      lastResult: existing?.lastResult || null,
    };
    const idx = list.findIndex((x) => x.endpoint === entry.endpoint);
    if (idx >= 0) list[idx] = entry;
    else list.push(entry);
    writeStore(list);
    console.log(
      `[+] 已保存订阅 (${idx >= 0 ? '更新' : '新增'}) [${entry.id}] ${entry.label}，当前共 ${list.length} 台设备`
    );
    return sendJson(res, 200, { ok: true, count: list.length, id: entry.id, label: entry.label });
  }

  // 设备列表
  if (pathname === '/api/subscriptions' && req.method === 'GET') {
    const list = readStore();
    return sendJson(res, 200, { count: list.length, subscriptions: list });
  }

  // 删除设备: { id } 或 { endpoint } 或 { all: true }
  if (pathname === '/api/subscriptions' && req.method === 'DELETE') {
    let body = null;
    try {
      body = await readBody(req);
    } catch {
      /* ignore */
    }
    let list = readStore();
    if (body?.all) list = [];
    else if (body?.id) list = list.filter((x) => x.id !== body.id);
    else if (body?.endpoint) list = list.filter((x) => x.endpoint !== body.endpoint);
    writeStore(list);
    console.log(`[-] 设备记录变更，剩余 ${list.length} 台`);
    return sendJson(res, 200, { ok: true, count: list.length, subscriptions: list });
  }

  // 重命名设备: { id, label }
  if (pathname === '/api/subscriptions' && req.method === 'PATCH') {
    let body;
    try {
      body = await readBody(req);
    } catch (e) {
      return sendJson(res, 400, { ok: false, error: e.message });
    }
    const list = readStore();
    const target = list.find((x) => x.id === body?.id || x.endpoint === body?.endpoint);
    if (!target) return sendJson(res, 404, { ok: false, error: '设备不存在' });
    target.label = String(body.label || '').slice(0, 60) || target.label;
    writeStore(list);
    return sendJson(res, 200, { ok: true, device: target });
  }

  // 发送推送: { targets: 'all' | [id...], title, body, url, tag, ttl }
  if (pathname === '/api/push' && req.method === 'POST') {
    let body;
    try {
      body = await readBody(req);
    } catch (e) {
      return sendJson(res, 400, { ok: false, error: e.message });
    }
    if (!body?.title && !body?.body) {
      return sendJson(res, 400, { ok: false, error: '标题和内容不能同时为空' });
    }
    if (!webpush) {
      return sendJson(res, 500, {
        ok: false,
        error: '未安装 web-push 依赖，请执行 `npm install web-push` 后重启服务。(' + webpushError + ')',
      });
    }

    const all = readStore();
    const targets =
      body.targets === 'all' || !body.targets
        ? all
        : all.filter((x) => body.targets.includes(x.id) || body.targets.includes(x.endpoint));
    if (!targets.length) return sendJson(res, 400, { ok: false, error: '没有选中任何设备' });

    const payload = JSON.stringify({
      title: body.title || '通知',
      body: body.body || '',
      url: body.url || '/',
      tag: body.tag || 'demo-' + Date.now(),
      sentAt: new Date().toISOString(),
    });

    const options = { TTL: Number(body.ttl) > 0 ? Number(body.ttl) : 60 * 60 * 24 };
    const results = [];
    await Promise.all(
      targets.map(async (dev) => {
        const r = { id: dev.id, label: dev.label, endpoint: dev.endpoint, ok: false };
        try {
          const resp = await webpush.sendNotification(
            { endpoint: dev.endpoint, keys: dev.keys },
            payload,
            options
          );
          r.ok = true;
          r.statusCode = resp.statusCode;
        } catch (err) {
          r.statusCode = err.statusCode || 0;
          r.error = typeof err.body === 'string' ? err.body.slice(0, 300) : err.message;
          r.gone = [404, 410].includes(r.statusCode); // 订阅已失效
        }
        results.push(r);
      })
    );

    // 回写发送结果；失效订阅自动清理
    const goneIds = new Set(results.filter((r) => r.gone).map((r) => r.id));
    const kept = all
      .filter((x) => !goneIds.has(x.id))
      .map((x) => {
        const r = results.find((i) => i.id === x.id);
        return r
          ? { ...x, lastPushAt: new Date().toISOString(), lastResult: r.ok ? '成功' : `失败 ${r.statusCode}` }
          : x;
      });
    writeStore(kept);

    const okCount = results.filter((r) => r.ok).length;
    console.log(
      `[>] 推送「${body.title || '通知'}」→ 成功 ${okCount}/${results.length}` +
        (goneIds.size ? `，清理失效设备 ${goneIds.size} 台` : '')
    );
    return sendJson(res, 200, {
      ok: okCount > 0,
      sent: okCount,
      total: results.length,
      removed: goneIds.size,
      results,
    });
  }

  if (pathname === '/api/vapid-public-key' && req.method === 'GET') {
    return sendJson(res, 200, { publicKey: VAPID_PUBLIC_KEY });
  }

  if (pathname === '/api/health' && req.method === 'GET') {
    return sendJson(res, 200, {
      ok: true,
      port: PORT,
      https: useHttps,
      webpush: !!webpush,
      devices: readStore().length,
      uptime: Math.round(process.uptime()),
    });
  }

  // ---- 静态资源 ----
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    return sendJson(res, 405, { ok: false, error: 'method not allowed' });
  }
  serveStatic(req, res, pathname);
}

function localIPs() {
  return Object.values(os.networkInterfaces())
    .flat()
    .filter((i) => i && i.family === 'IPv4' && !i.internal)
    .map((i) => i.address);
}

const useHttps = process.env.HTTPS === '1' || fs.existsSync(path.join(__dirname, 'certs', 'server.crt'));
let server;

if (useHttps) {
  const crt = path.join(__dirname, 'certs', 'server.crt');
  const key = path.join(__dirname, 'certs', 'server.key');
  if (!fs.existsSync(crt) || !fs.existsSync(key)) {
    console.error('HTTPS 已开启但缺少证书: 请先执行 `npm run cert`');
    process.exit(1);
  }
  server = https.createServer({ cert: fs.readFileSync(crt), key: fs.readFileSync(key) }, (req, res) => {
    handle(req, res).catch((e) => sendJson(res, 500, { ok: false, error: String(e) }));
  });
} else {
  server = http.createServer((req, res) => {
    handle(req, res).catch((e) => sendJson(res, 500, { ok: false, error: String(e) }));
  });
}

server.listen(PORT, HOST, () => {
  const scheme = useHttps ? 'https' : 'http';
  console.log(`\n  Web Push 演示服务已启动 (${scheme})`);
  console.log(`  本机:   ${scheme}://localhost:${PORT}`);
  for (const ip of localIPs()) console.log(`  局域网: ${scheme}://${ip}:${PORT}`);
  console.log(`\n  订阅接口: POST ${scheme}://localhost:${PORT}/api/subscribe`);
  console.log(`  推送接口: POST ${scheme}://localhost:${PORT}/api/push`);
  console.log(`  web-push 依赖: ${webpush ? '可用 ✔' : '缺失 ✘（npm install web-push）'}`);
  console.log(`  订阅数据: ${STORE}（当前 ${readStore().length} 台设备）`);
  if (!useHttps) {
    console.log('\n  提示: 非 localhost 访问（手机/PWA）必须 HTTPS，可执行 `npm run cert` 后以 HTTPS=1 启动。');
  }
  console.log('');
});
