'use strict';

/* ============ 配置 ============ */

// 默认 VAPID 公钥（web-push generate-vapid-keys 生成，可用输入框覆盖）
const DEFAULT_VAPID_PUBLIC_KEY =
  'BPnvp8p4QdnOh4vO6-oAhxFGouHJTqY68C_4-goxBh1sphBEb1blz2FgqyEVg5JoFMBdSJKu2tDR-VLkdUNIHrQ';

const STORAGE_KEY = 'webpush.vapidPublicKey';

/* ============ 工具 ============ */

const $ = (id) => document.getElementById(id);

/** 本机设备标签，用于在设备列表里区分 */
function deviceLabel() {
  const ua = navigator.userAgent;
  const os = /iPhone|iPad|iPod/.test(ua)
    ? 'iOS'
    : /Android/.test(ua)
      ? 'Android'
      : /Mac OS X/.test(ua)
        ? 'macOS'
        : /Windows/.test(ua)
          ? 'Windows'
          : /Linux/.test(ua)
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
            : '浏览器';
  const pwa =
    (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) ||
    navigator.standalone
      ? ' PWA'
      : '';
  const width = window.screen?.width ? ` ${Math.min(window.screen.width, window.screen.height)}px` : '';
  return `${os} · ${br}${pwa}${width}`;
}

/** base64url -> Uint8Array （applicationServerKey 必须是 Uint8Array） */
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const raw = atob(base64);
  const output = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) output[i] = raw.charCodeAt(i);
  return output;
}

function shortEndpoint(endpoint) {
  if (!endpoint) return '';
  try {
    const u = new URL(endpoint);
    return u.host + (u.pathname.length > 24 ? u.pathname.slice(0, 24) + '…' : u.pathname);
  } catch {
    return endpoint;
  }
}

let toastTimer;
function toast(msg, kind = 'ok') {
  const el = $('toast');
  el.textContent = msg;
  el.className = 'toast show ' + kind;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (el.className = 'toast'), 2600);
}

async function copyText(text, okMsg = '已复制到剪贴板') {
  if (!text) return toast('没有可复制的内容', 'warn');
  try {
    await navigator.clipboard.writeText(text);
    toast(okMsg);
  } catch {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand('copy');
    ta.remove();
    toast(ok ? okMsg : '复制失败，请手动选择文本复制', ok ? 'ok' : 'warn');
  }
}

/* ============ Tab 切换 ============ */

const TABS = ['register', 'push', 'help'];
const TAB_KEY = 'webpush.tab';

function activateTab(name, opts = {}) {
  if (!TABS.includes(name)) name = opts.fallback || 'register';
  for (const btn of document.querySelectorAll('.tab')) {
    btn.setAttribute('aria-selected', String(btn.dataset.tab === name));
  }
  for (const t of TABS) {
    const panel = $('panel-' + t);
    if (panel) panel.hidden = t !== name;
  }
  try {
    localStorage.setItem(TAB_KEY, name);
  } catch {
    /* 忽略隐私模式下的写入失败 */
  }
  if (!opts.silent) window.scrollTo({ top: 0, behavior: 'smooth' });
  if (name === 'push') loadDevices(true); // 切到推送页时刷新设备列表
}

function initTabs() {
  const btns = [...document.querySelectorAll('.tab')];
  btns.forEach((btn) => btn.addEventListener('click', () => activateTab(btn.dataset.tab)));

  // 键盘左右/Home/End 切换
  document.querySelector('.tabs')?.addEventListener('keydown', (e) => {
    const keys = ['ArrowLeft', 'ArrowRight', 'Home', 'End'];
    if (!keys.includes(e.key)) return;
    e.preventDefault();
    const cur = btns.findIndex((b) => b.getAttribute('aria-selected') === 'true');
    const next =
      e.key === 'Home'
        ? 0
        : e.key === 'End'
          ? btns.length - 1
          : (cur + (e.key === 'ArrowRight' ? 1 : -1) + btns.length) % btns.length;
    btns[next].focus();
    activateTab(btns[next].dataset.tab);
  });

  // 支持 #push / #help 直达，并记住上次所在页
  let initial = location.hash.replace('#', '');
  if (!TABS.includes(initial)) {
    try {
      initial = localStorage.getItem(TAB_KEY) || 'register';
    } catch {
      initial = 'register';
    }
  }
  activateTab(initial, { silent: true });
  window.addEventListener('hashchange', () =>
    activateTab(location.hash.replace('#', ''), { silent: true })
  );
}

/* ============ 状态渲染 ============ */

const state = {
  registration: null,
  subscription: null,
};

function badge(el, text, kind) {
  el.textContent = text;
  el.className = 'badge ' + kind;
}

function render() {
  const sub = state.subscription;

  // 浏览器能力
  const supported =
    'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
  badge($('sSupport'), supported ? '支持' : '不支持', supported ? 'ok' : 'bad');

  // 权限
  const perm = 'Notification' in window ? Notification.permission : 'unsupported';
  const permMap = {
    granted: ['已允许', 'ok'],
    denied: ['已拒绝', 'bad'],
    default: ['未询问', 'idle'],
    unsupported: ['不可用', 'bad'],
  };
  badge($('sPermission'), ...(permMap[perm] || ['未知', 'idle']));

  // SW
  badge($('sSw'), state.registration ? '已激活' : '未注册', state.registration ? 'ok' : 'idle');

  // 订阅
  badge($('sSub'), sub ? '已订阅' : '未订阅', sub ? 'ok' : 'idle');

  // 安全上下文提示
  const secure = window.isSecureContext;
  $('insecureWarn').style.display = secure ? 'none' : 'flex';

  // 输出
  const json = sub ? JSON.stringify(sub.toJSON ? sub.toJSON() : sub, null, 2) : '';
  $('out').textContent = json || '// 还没有 subscription，点击「注册推送」后这里会显示订阅对象';
  $('btnCopy').disabled = !sub;
  $('btnUnsub').disabled = !sub;
  $('btnServer').disabled = !sub;

  $('endpointText').textContent = sub ? sub.endpoint : '—';
  $('endpointText').title = sub ? sub.endpoint : '';
  $('p256dhText').textContent = sub?.getKey ? b64url(sub.getKey('p256dh')) : '—';
  $('authText').textContent = sub?.getKey ? b64url(sub.getKey('auth')) : '—';

  $('btnSub').textContent = sub ? '重新注册 / 刷新订阅' : '注册推送';
}

function b64url(buf) {
  if (!buf) return '';
  return btoa(String.fromCharCode(...new Uint8Array(buf)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

/* ============ 核心操作 ============ */

async function registerServiceWorker() {
  if (!('serviceWorker' in navigator)) throw new Error('当前浏览器不支持 Service Worker');
  const reg = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
  await navigator.serviceWorker.ready;
  state.registration = reg;
  return reg;
}

async function ensurePermission() {
  if (!('Notification' in window)) throw new Error('当前浏览器不支持 Notification');
  if (Notification.permission === 'granted') return 'granted';
  if (Notification.permission === 'denied') {
    throw new Error('通知权限已被拒绝，请在浏览器地址栏站点设置里重新允许通知后刷新页面');
  }
  const res = await Notification.requestPermission();
  if (res !== 'granted') throw new Error('你拒绝了通知权限（permission=' + res + '）');
  return res;
}

function getVapidPublicKey() {
  return ($('vapidInput').value || localStorage.getItem(STORAGE_KEY) || DEFAULT_VAPID_PUBLIC_KEY).trim();
}

async function subscribe() {
  const btn = $('btnSub');
  btn.disabled = true;
  btn.textContent = '注册中…';
  try {
    if (!window.isSecureContext) {
      throw new Error('当前不是安全上下文（需要 https 或 localhost），浏览器不会允许订阅推送');
    }
    const publicKey = getVapidPublicKey();
    if (publicKey.length < 80) throw new Error('VAPID 公钥看起来不合法（长度不足）');
    localStorage.setItem(STORAGE_KEY, publicKey);

    const reg = await registerServiceWorker();
    await ensurePermission();

    // 已有订阅时先取消，保证「重新注册」拿到新的 subscription
    const existing = await reg.pushManager.getSubscription();
    if (existing) {
      await existing.unsubscribe().catch(() => {});
    }

    const sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,                                   // 浏览器强制要求
      applicationServerKey: urlBase64ToUint8Array(publicKey),  // VAPID 公钥
    });

    state.subscription = sub;
    render();

    const payload = { ...(sub.toJSON ? sub.toJSON() : { endpoint: sub.endpoint }), label: deviceLabel() };
    console.log('[web-push] subscription =', payload);
    console.log('[web-push] JSON.stringify(subscription) =', JSON.stringify(sub));

    // 同步到本地服务端，成功后刷新设备列表
    try {
      const r = await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const d = await r.json();
      console.log('[web-push] 服务端已保存:', d);
    } catch (e) {
      console.warn('[web-push] 服务端保存失败:', e);
    }
    window.dispatchEvent(new Event('webpush:changed'));

    toast('注册成功，subscription 已复制；可切到「② 推送测试」发推送');
    copyText(JSON.stringify(payload));
  } catch (err) {
    console.error(err);
    toast(err.message || String(err), 'bad');
    $('out').textContent = '// 注册失败：' + (err.message || err);
  } finally {
    btn.disabled = false;
    render();
  }
}

async function unsubscribe() {
  try {
    if (state.registration) {
      const sub = await state.registration.pushManager.getSubscription();
      if (sub) {
        const endpoint = sub.endpoint;
        await sub.unsubscribe();
        // 删除服务端记录（按 endpoint）
        fetch('/api/subscriptions', {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ endpoint }),
        }).catch(() => {});
      }
    }
    state.subscription = null;
    render();
    window.dispatchEvent(new Event('webpush:changed'));
    toast('已取消订阅');
  } catch (err) {
    toast('取消订阅失败: ' + err.message, 'bad');
  }
}

async function testNotification() {
  try {
    await ensurePermission();
    const reg = state.registration || (await registerServiceWorker());
    await reg.showNotification('本地通知测试', {
      body: '这条通知由 showNotification 直接触发，说明通知通道可用。真正的推送需要服务端发 push。',
      icon: '/icons/icon-192.png',
      tag: 'local-test',
    });
  } catch (err) {
    toast(err.message, 'bad');
  }
}

/* ============ 推送面板 ============ */

// 预置内容模板，可在页面上选择后继续编辑
const PRESETS = [
  {
    name: '系统通知｜版本升级',
    title: '系统升级通知',
    body: '服务将于今晚 23:00 - 23:30 进行升级维护，期间可能短暂不可用，请提前保存工作内容。',
    url: '/',
    ttl: 86400,
  },
  {
    name: '订单提醒｜已发货',
    title: '你的订单已发货 📦',
    body: '订单 #20260514 已出库，预计明天 12:00 前送达，点击查看物流详情。',
    url: '/',
    ttl: 43200,
  },
  {
    name: '互动消息｜新消息',
    title: '你有 1 条新消息',
    body: '张三：需求文档我看过了，有两点想和你确认，方便的时候回一下～',
    url: '/',
    ttl: 3600,
  },
  {
    name: '活动营销｜限时优惠',
    title: '限时 5 折，今天最后一天',
    body: '全场会员充值立减 50%，点击立即领取专属优惠券，活动截止 24:00。',
    url: '/',
    ttl: 604800,
  },
  {
    name: '安全提醒｜新设备登录',
    title: '新设备登录提醒',
    body: '你的账号刚刚在一台新设备上登录，若非本人操作，请立即修改密码。',
    url: '/',
    ttl: 86400,
  },
  {
    name: '测试消息｜Hello Push',
    title: 'Hello Web Push 👋',
    body: '这是一条测试推送，收到说明端到端链路正常。',
    url: '/',
    ttl: 300,
  },
  { name: '自定义…', title: '', body: '', url: '/', ttl: 86400 },
];

const pushState = {
  devices: [],
  selected: new Set(),
  sending: false,
};

function applyPreset(index) {
  const p = PRESETS[index];
  if (!p) return;
  if (index === PRESETS.length - 1) return; // 自定义：保留用户输入
  $('pushTitle').value = p.title;
  $('pushBody').value = p.body;
  $('pushUrl').value = p.url || '/';
  $('pushTtl').value = String(p.ttl || 86400);
}

function timeAgo(iso) {
  if (!iso) return '—';
  const diff = Date.now() - new Date(iso).getTime();
  if (!Number.isFinite(diff)) return '—';
  const m = Math.floor(diff / 60000);
  if (m < 1) return '刚刚';
  if (m < 60) return `${m} 分钟前`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h} 小时前`;
  return `${Math.floor(h / 24)} 天前`;
}

function renderDevices() {
  const box = $('deviceList');
  const list = pushState.devices;
  $('devCount').textContent = list.length;
  $('tabDevCount').textContent = list.length;
  $('serverCount').textContent = list.length ? `服务端已保存 ${list.length} 台设备` : '';
  $('pushHint').textContent = list.length ? `已选 ${pushState.selected.size}/${list.length}` : '';

  if (!list.length) {
    box.innerHTML = '<p class="empty">暂无已注册设备，先点击上面的「注册推送」。</p>';
    return;
  }

  box.innerHTML = '';
  for (const d of list) {
    const on = pushState.selected.has(d.id);
    const row = document.createElement('div');
    row.className = 'dev' + (on ? ' on' : '');

    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.checked = on;
    cb.title = '选择这台设备';
    cb.addEventListener('change', () => {
      if (cb.checked) pushState.selected.add(d.id);
      else pushState.selected.delete(d.id);
      renderDevices();
    });

    const meta = document.createElement('div');
    meta.className = 'meta';
    const name = document.createElement('div');
    name.className = 'name';
    name.textContent = d.label || d.id;
    const sub = document.createElement('div');
    sub.className = 'sub';
    const ep = d.endpoint || '';
    sub.textContent = `${d.id} · ${shortEndpoint(ep)} · 注册 ${timeAgo(d.savedAt)}` +
      (d.lastPushAt ? ` · 上次推送 ${timeAgo(d.lastPushAt)}${d.lastResult ? ' (' + d.lastResult + ')' : ''}` : '');
    meta.append(name, sub);

    const acts = document.createElement('div');
    acts.className = 'acts';
    const rename = document.createElement('button');
    rename.className = 'ghost tiny';
    rename.textContent = '重命名';
    rename.addEventListener('click', async () => {
      const next = prompt('设备名称', d.label || '');
      if (next === null || !next.trim()) return;
      await fetch('/api/subscriptions', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: d.id, label: next.trim() }),
      });
      toast('已重命名');
      loadDevices();
    });
    const only = document.createElement('button');
    only.className = 'ghost tiny';
    only.textContent = '仅推它';
    only.addEventListener('click', () => {
      pushState.selected = new Set([d.id]);
      renderDevices();
    });
    const del = document.createElement('button');
    del.className = 'ghost tiny danger';
    del.textContent = '删除';
    del.addEventListener('click', async () => {
      if (!confirm(`从服务端删除「${d.label || d.id}」的订阅记录？`)) return;
      await fetch('/api/subscriptions', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: d.id }),
      });
      pushState.selected.delete(d.id);
      toast('已删除设备记录');
      loadDevices();
    });
    acts.append(rename, only, del);

    row.append(cb, meta, acts);
    row.addEventListener('click', (e) => {
      if (e.target.tagName === 'BUTTON' || e.target.tagName === 'INPUT') return;
      cb.checked = !cb.checked;
      cb.dispatchEvent(new Event('change'));
    });
    box.appendChild(row);
  }
}

async function loadDevices(silent = false) {
  try {
    const res = await fetch('/api/subscriptions', { cache: 'no-store' });
    const data = await res.json();
    pushState.devices = data.subscriptions || [];
    // 丢弃已被删除设备的选中状态；首次加载默认全选
    const ids = new Set(pushState.devices.map((d) => d.id));
    if (!pushState.touched) {
      pushState.selected = new Set(ids);
      pushState.touched = true;
    } else {
      for (const id of [...pushState.selected]) if (!ids.has(id)) pushState.selected.delete(id);
    }
    renderDevices();
    if (!silent) toast(`设备列表已刷新：${pushState.devices.length} 台`);
  } catch (e) {
    if (!silent) toast('读取设备列表失败: ' + e.message, 'bad');
  }
}

async function sendPush(targets) {
  if (pushState.sending) return;
  const title = $('pushTitle').value.trim();
  const body = $('pushBody').value.trim();
  if (!title && !body) return toast('标题和内容不能同时为空', 'warn');

  const payload = {
    targets,
    title,
    body,
    url: $('pushUrl').value.trim() || '/',
    ttl: Number($('pushTtl').value) || 86400,
  };
  if (targets !== 'all' && !targets.length) return toast('请先勾选要推送的设备', 'warn');

  pushState.sending = true;
  const btns = [$('btnSend'), $('btnSendAll')];
  btns.forEach((b) => (b.disabled = true));
  $('pushResult').textContent = '// 发送中…';

  try {
    const res = await fetch('/api/push', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || '发送失败');

    const lines = data.results.map((r) =>
      `${r.ok ? '✓' : '✗'} [${r.id}] ${r.label}  ${r.ok ? 'HTTP ' + r.statusCode : r.error || '失败'}`
    );
    $('pushResult').textContent =
      `// 发送时间 ${new Date().toLocaleTimeString()}\n` +
      `// 成功 ${data.sent}/${data.total}` +
      (data.removed ? `，自动清理失效设备 ${data.removed} 台` : '') +
      '\n\n' +
      lines.join('\n');

    toast(data.sent ? `推送完成：成功 ${data.sent}/${data.total}` : '推送失败，见下方结果', data.sent ? 'ok' : 'bad');
    if (data.removed) await loadDevices(true);
  } catch (e) {
    $('pushResult').textContent = '// ' + e.message;
    toast(e.message, 'bad');
  } finally {
    pushState.sending = false;
    btns.forEach((b) => (b.disabled = false));
  }
}

/* ============ 初始化 ============ */

(async function init() {
  $('vapidInput').value = localStorage.getItem(STORAGE_KEY) || DEFAULT_VAPID_PUBLIC_KEY;
  $('urlHint').textContent = location.origin;

  // 没手动改过就跟随服务端当前公钥，避免前后端 VAPID 不一致
  fetch('/api/vapid-public-key')
    .then((r) => r.json())
    .then((d) => {
      if (d?.publicKey && !localStorage.getItem(STORAGE_KEY)) $('vapidInput').value = d.publicKey;
    })
    .catch(() => {});

  $('btnSub').addEventListener('click', subscribe);  $('btnUnsub').addEventListener('click', unsubscribe);
  $('btnCopy').addEventListener('click', () => {
    const sub = state.subscription;
    if (!sub) return;
    copyText(JSON.stringify(sub.toJSON ? sub.toJSON() : sub), 'subscription JSON 已复制');
  });
  $('btnCopyRaw').addEventListener('click', () => {
    const sub = state.subscription;
    if (!sub) return;
    copyText(JSON.stringify(sub), '已复制 JSON.stringify(subscription)');
  });
  $('btnServer').addEventListener('click', () => loadDevices());
  $('btnTest').addEventListener('click', testNotification);

  // 推送面板
  const presetSel = $('preset');
  PRESETS.forEach((p, i) => {
    const opt = document.createElement('option');
    opt.value = String(i);
    opt.textContent = p.name;
    presetSel.appendChild(opt);
  });
  presetSel.value = '1';
  applyPreset(1); // 默认用「订单提醒」示例
  presetSel.addEventListener('change', () => {
    const i = Number(presetSel.value);
    if (i === PRESETS.length - 1) {
      $('pushTitle').value = '';
      $('pushBody').value = '';
      $('pushUrl').value = '/';
      $('pushTtl').value = '86400';
      return;
    }
    applyPreset(i);
  });
  $('btnAll').addEventListener('click', () => {
    pushState.selected = new Set(pushState.devices.map((d) => d.id));
    pushState.touched = true;
    renderDevices();
  });
  $('btnNone').addEventListener('click', () => {
    pushState.selected = new Set();
    pushState.touched = true;
    renderDevices();
  });
  $('btnReload').addEventListener('click', () => loadDevices());
  $('btnClearDev').addEventListener('click', async () => {
    if (!pushState.devices.length) return toast('当前没有设备记录', 'warn');
    if (!confirm(`清空服务端全部 ${pushState.devices.length} 条订阅记录？（浏览器侧订阅不受影响）`)) return;
    await fetch('/api/subscriptions', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ all: true }),
    });
    pushState.selected = new Set();
    toast('已清空设备记录');
    loadDevices(true);
  });
  $('btnSend').addEventListener('click', () => sendPush([...pushState.selected]));
  $('btnSendAll').addEventListener('click', () => sendPush('all'));

  loadDevices(true);
  // 注册/取消订阅后自动刷新设备列表
  window.addEventListener('webpush:changed', () => loadDevices(true), { once: false });

  initTabs();
  $('btnResetKey').addEventListener('click', () => {
    localStorage.removeItem(STORAGE_KEY);
    $('vapidInput').value = DEFAULT_VAPID_PUBLIC_KEY;
    toast('已恢复默认 VAPID 公钥');
  });
  $('btnClear').addEventListener('click', () => {
    state.subscription = null;
    render();
  });

  try {
    if ('serviceWorker' in navigator) {
      state.registration = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
      await navigator.serviceWorker.ready;
      state.subscription = await state.registration.pushManager.getSubscription();
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data?.type === 'push-received') {
          $('lastPush').textContent = JSON.stringify(event.data.payload, null, 2);
          toast('收到一条推送（切到「② 推送测试」查看 payload）');
        }
        // 浏览器轮换了订阅（iOS 常见），自动重新注册并上报
        if (event.data?.type === 'subscription-change') {
          toast('检测到订阅被浏览器更新，正在重新注册…', 'warn');
          subscribe();
        }
      });
    }
  } catch (err) {
    console.warn('SW 初始化失败', err);
  }
  render();
})();
