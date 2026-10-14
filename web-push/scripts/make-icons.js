'use strict';
/**
 * 生成 PWA 图标（纯 Node，无依赖）：192 / 512 / 180(apple-touch-icon)
 * 用法: node scripts/make-icons.js
 */
const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');

const OUT = path.join(__dirname, '..', 'public', 'icons');

function crc32(buf) {
  let c;
  const table = crc32.table || (crc32.table = (() => {
    const t = new Int32Array(256);
    for (let n = 0; n < 256; n++) {
      c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      t[n] = c;
    }
    return t;
  })());
  let crc = -1;
  for (let i = 0; i < buf.length; i++) crc = table[(crc ^ buf[i]) & 0xff] ^ (crc >>> 8);
  return (crc ^ -1) >>> 0;
}

function chunk(type, data) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length);
  const body = Buffer.concat([Buffer.from(type, 'ascii'), data]);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(body));
  return Buffer.concat([len, body, crc]);
}

function png(width, height, rgba) {
  const raw = Buffer.alloc((width * 4 + 1) * height);
  for (let y = 0; y < height; y++) {
    raw[y * (width * 4 + 1)] = 0; // filter none
    rgba.copy(raw, y * (width * 4 + 1) + 1, y * width * 4, (y + 1) * width * 4);
  }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8;   // bit depth
  ihdr[9] = 6;   // RGBA
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk('IHDR', ihdr),
    chunk('IDAT', zlib.deflateSync(raw, { level: 9 })),
    chunk('IEND', Buffer.alloc(0)),
  ]);
}

// 简易多边形/形状判定：绘制渐变底 + 白色铃铛
function draw(size) {
  const buf = Buffer.alloc(size * size * 4);
  const s = size;
  const cx = s / 2;
  const set = (x, y, r, g, b, a) => {
    const i = (y * s + x) * 4;
    const sa = a / 255;
    buf[i] = Math.round(buf[i] * (1 - sa) + r * sa);
    buf[i + 1] = Math.round(buf[i + 1] * (1 - sa) + g * sa);
    buf[i + 2] = Math.round(buf[i + 2] * (1 - sa) + b * sa);
    buf[i + 3] = 255;
  };
  for (let y = 0; y < s; y++) {
    for (let x = 0; x < s; x++) {
      const t = (x + y) / (2 * s);
      // 紫->蓝渐变
      let r = Math.round(0x6d + (0x25 - 0x6d) * t);
      let g = Math.round(0x5a + (0x6a - 0x5a) * t);
      let b = Math.round(0xf7 + (0xe8 - 0xf7) * t);
      // 圆角
      const rad = s * 0.22;
      const dx = Math.max(rad - x, 0, x - (s - 1 - rad));
      const dy = Math.max(rad - y, 0, y - (s - 1 - rad));
      const d = Math.hypot(dx, dy);
      const alpha = d <= rad ? 255 : d <= rad + 1 ? Math.round(255 * (rad + 1 - d)) : 0;
      if (alpha === 0) { buf[(y * s + x) * 4 + 3] = 0; continue; }
      set(x, y, r, g, b, alpha);
    }
  }
  // 铃铛主体
  const bellW = s * 0.44;
  const bellTop = s * 0.26;
  const bellBottom = s * 0.68;
  for (let y = 0; y < s; y++) {
    for (let x = 0; x < s; x++) {
      const ny = (y - bellTop) / (bellBottom - bellTop);
      if (ny < 0 || ny > 1) continue;
      const half = (bellW / 2) * Math.min(1, 0.42 + ny * 0.75);
      if (Math.abs(x - cx) <= half) set(x, y, 255, 255, 255, 255);
    }
  }
  // 铃铛下沿 + 铃舌
  for (let y = 0; y < s; y++) {
    for (let x = 0; x < s; x++) {
      const ny = (y - bellBottom) / (s * 0.035);
      if (ny < 0 || ny > 1) continue;
      const half = (bellW / 2) * 1.17;
      if (Math.abs(x - cx) <= half) set(x, y, 255, 255, 255, 255);
    }
  }
  for (let y = 0; y < s; y++) {
    for (let x = 0; x < s; x++) {
      if (Math.hypot(x - cx, y - (bellBottom + s * 0.075)) <= s * 0.055) set(x, y, 255, 255, 255, 255);
    }
  }
  // 顶部小柄
  for (let y = 0; y < s; y++) {
    for (let x = 0; x < s; x++) {
      if (Math.hypot(x - cx, y - (bellTop + s * 0.005)) <= s * 0.035) set(x, y, 255, 255, 255, 255);
    }
  }
  return png(s, s, buf);
}

fs.mkdirSync(OUT, { recursive: true });
for (const [name, size] of [['icon-192.png', 192], ['icon-512.png', 512], ['apple-touch-icon.png', 180], ['favicon-64.png', 64]]) {
  fs.writeFileSync(path.join(OUT, name), draw(size));
  console.log('生成', path.join('public/icons', name));
}
