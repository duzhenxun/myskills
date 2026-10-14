'use strict';
/**
 * 演示「不借助 web-push 库，直接手写 HTTP 请求」推到推送服务
 *
 *   node scripts/raw-request.js            # 只打印本次请求（headers + body 摘要）
 *   node scripts/raw-request.js --send     # 真的发出去（空 payload 模式，纯 curl 可复现）
 *
 * 说明：
 *  - 有 payload 时 body 必须用 RFC8291(aes128gcm) 加密，纯 curl 做不到（需要 ECDH+HKDF+AES-GCM）
 *  - 无 payload 时可以完全手写：只发 VAPID JWT 头 + TTL，body 为空
 */
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const https = require('node:https');

const PRIVATE_KEY = process.env.VAPID_PRIVATE_KEY || 'UArGsIjinVV7Lk0g3zOdkMctvWIoTzUT8jV2vayiOyQ';
const PUBLIC_KEY =
  process.env.VAPID_PUBLIC_KEY ||
  'BPnvp8p4QdnOh4vO6-oAhxFGouHJTqY68C_4-goxBh1sphBEb1blz2FgqyEVg5JoFMBdSJKu2tDR-VLkdUNIHrQ';
const SUBJECT = process.env.VAPID_SUBJECT || 'mailto:duzhenxun@126.com';

const b64u = (buf) => Buffer.from(buf).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

/** 把 URL-safe base64 的 VAPID 私钥/公钥转成 Node 的 EC KeyObject（走 JWK 导入，x/y 取自公钥的点） */
function decodeB64u(s) {
  return Buffer.from(s.replace(/-/g, '+').replace(/_/g, '/'), 'base64');
}

function privateKeyObject(privateB64u, publicB64u) {
  const point = decodeB64u(publicB64u); // 0x04 || X(32) || Y(32)
  if (point.length !== 65 || point[0] !== 4) throw new Error('VAPID 公钥不是合法的 P-256 uncompressed point');
  return crypto.createPrivateKey({
    key: {
      kty: 'EC',
      crv: 'P-256',
      d: privateB64u,
      x: b64u(point.subarray(1, 33)),
      y: b64u(point.subarray(33, 65)),
    },
    format: 'jwk',
  });
}

/** 生成 VAPID 的 ES256 JWT：payload = { aud: <推送服务 origin>, exp, sub } */
function vapidHeaders(endpoint, ttl) {
  const aud = new URL(endpoint).origin;
  const header = b64u(JSON.stringify({ typ: 'JWT', alg: 'ES256' }));
  const payload = b64u(
    JSON.stringify({ aud, exp: Math.floor(Date.now() / 1000) + 12 * 3600, sub: SUBJECT })
  );
  const signingInput = `${header}.${payload}`;
  const sig = crypto.sign('sha256', Buffer.from(signingInput), {
    key: privateKeyObject(PRIVATE_KEY, PUBLIC_KEY),
    dsaEncoding: 'ieee-p1363',
  });
  return {
    TTL: String(ttl || 60),
    'Content-Length': '0',
    Authorization: `vapid t=${signingInput}.${b64u(sig)}, k=${PUBLIC_KEY}`,
    Urgency: 'normal',
  };
}

(async () => {
  const { endpoint } = JSON.parse(process.argv[3] || '{}');
  let sub;
  if (endpoint) sub = { endpoint };
  else {
    const list = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'subscriptions.json'), 'utf8'));
    sub = list[0];
  }
  if (!sub?.endpoint) {
    console.error('没有可用 endpoint，先在页面上注册设备');
    process.exit(1);
  }
  const ep = sub.endpoint.trim();
  const headers = vapidHeaders(ep, 60);

  console.log('POST ' + ep);
  for (const [k, v] of Object.entries(headers)) console.log(k + ': ' + v.slice(0, 90) + (v.length > 90 ? '…' : ''));
  console.log('\n等价 curl：\n');
  console.log(
    `curl -i -X POST '${ep}' \\\n  -H 'TTL: 60' \\\n  -H 'Content-Length: 0' \\\n  -H 'Authorization: vapid t=${headers.Authorization.match(/t=([^,]+)/)[1]}, k=${PUBLIC_KEY}' \\\n  -H 'Urgency: normal'\n`
  );

  if (!process.argv.includes('--send')) {
    console.log('（加 --send 参数才会真正发出）');
    return;
  }

  https.request(
    ep,
    { method: 'POST', headers },
    (res) => {
      let body = '';
      res.on('data', (c) => (body += c));
      res.on('end', () => {
        console.log(`推送服务响应: HTTP ${res.statusCode} ${res.statusMessage}`);
        if (body) console.log(body);
      });
    }
  ).on('error', (e) => console.error('请求失败:', e.message))
   .end();
})();
