#!/usr/bin/env node
/**
 * codex-ws-client.mjs — 与 `codex app-server --listen ws://127.0.0.1:25258` 通信的客户端
 *
 * 依赖：Node.js >= 22（内置 WebSocket，无需 npm install）
 *
 * 用法：
 *   node codex-ws-client.mjs                          # 交互模式，逐行输入消息（Ctrl-D 退出）
 *   node codex-ws-client.mjs "帮我看看这个目录有什么"    # 单次提问后退出
 *   echo "写个 hello world" | node codex-ws-client.mjs  # 从管道读
 *   node codex-ws-client.mjs -t 0199c... "继续刚才的任务" # 续用已有会话
 *
 * 连接参数（按优先级：--url > --host/--port > 环境变量 > 默认值）：
 *   --url <ws://host:port>     完整地址，也可只写 host:port
 *   --addr <host:port>         地址 + 端口（等价于 --host + --port）
 *   --host <host>              主机，默认 127.0.0.1
 *   -p, --port <n>             端口，默认 25258
 *   环境变量：CODEX_WS_URL / CODEX_WS_HOST / CODEX_WS_PORT
 *
 * 其他参数：
 *   --cwd <dir>                工作目录（默认当前目录）
 *   -t, --thread <id>          复用/恢复已有 thread
 *   --model <name>             指定模型
 *   --sandbox <read-only|workspace-write|danger-full-access>
 *   --approval <untrusted|on-request|on-failure|never>
 *   --auto-approve             所有审批请求自动 acceptForSession（默认交互式询问）
 *   --decline                  所有审批请求自动 decline
 *   --verbose                  打印推理/思考增量
 *   --json                     只输出原始事件 JSON（便于程序处理）
 *   --timeout <sec>            等待 turn 完成的最长时间，默认 1800
 */

import readline from 'node:readline';

// ---------- 参数解析 ----------
const DEFAULT_HOST = '127.0.0.1';
const DEFAULT_PORT = 25258;

const argv = process.argv.slice(2);
const opts = {
  url: null,                                              // 完整地址（最高优先级）
  host: process.env.CODEX_WS_HOST || DEFAULT_HOST,
  port: Number(process.env.CODEX_WS_PORT) || DEFAULT_PORT,
  cwd: process.cwd(),
  thread: null,
  model: null,
  sandbox: null,
  approval: null,
  autoApprove: false,
  autoDecline: false,
  verbose: false,
  json: false,
  timeout: 1800,
  messages: [],
};
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  const next = () => argv[++i];
  switch (a) {
    case '--url': opts.url = next(); break;
    case '--host': case '--addr': {
      const v = String(next() ?? '').trim().replace(/^\[|\]$/g, '');
      const m = v.match(/^(\[?[^\]]+\]?):(\d+)$/);   // host:port
      if (m) { opts.host = m[1].replace(/^\[|\]$/g, ''); opts.port = Number(m[2]); }
      else if (/^\d+$/.test(v)) opts.port = Number(v);  // 只给端口
      else opts.host = v;
      break;
    }
    case '-p': case '--port': opts.port = Number(next()); break;
    case '--cwd': opts.cwd = next(); break;
    case '-t': case '--thread': opts.thread = next(); break;
    case '--model': opts.model = next(); break;
    case '--sandbox': opts.sandbox = next(); break;
    case '--approval': opts.approval = next(); break;
    case '--auto-approve': case '-y': opts.autoApprove = true; break;
    case '--decline': opts.autoDecline = true; break;
    case '--verbose': case '-v': opts.verbose = true; break;
    case '--json': opts.json = true; break;
    case '--timeout': opts.timeout = Number(next()); break;
    case '-h': case '--help': console.log(help()); process.exit(0); break;
    default: opts.messages.push(a);
  }
}

/** 把 --url / --host / --port / 环境变量 合成一个 ws:// 地址。 */
function resolveUrl(o) {
  const raw = String(o.url ?? process.env.CODEX_WS_URL ?? '').trim().replace(/^["']|["']$/g, '');
  if (raw) {
    if (/^wss?:\/\//i.test(raw)) return raw;
    if (/^https?:\/\//i.test(raw)) return raw.replace(/^http/i, 'ws');  // http(s) -> ws(s)
    return 'ws://' + raw;                                                // host:port[/path]
  }
  if (!Number.isInteger(o.port) || o.port < 1 || o.port > 65535) {
    console.error(`端口不合法: ${o.port}（应为 1-65535）`);
    process.exit(2);
  }
  const host = o.host.includes(':') && !o.host.startsWith('[') ? `[${o.host}]` : o.host;  // IPv6
  return `ws://${host}:${o.port}`;
}

opts.url = resolveUrl(opts);

function help() {
  const src = new URL(import.meta.url).pathname;
  return `用法: node ${src} [选项] ["消息" ...]

连接：
  --url <ws://host:port>   完整地址（也可只写 host:port），默认 ws://${DEFAULT_HOST}:${DEFAULT_PORT}
  --addr <host:port>      地址 + 端口
  --host <host>            主机，默认 ${DEFAULT_HOST}
  -p, --port <n>           端口，默认 ${DEFAULT_PORT}
  环境变量：CODEX_WS_URL / CODEX_WS_HOST / CODEX_WS_PORT

其他：
  --cwd <dir>              工作目录
  -t, --thread <id>        复用/恢复已有 thread
  --model <name>           指定模型
  --sandbox <mode>         read-only | workspace-write | danger-full-access
  --approval <mode>        untrusted | on-request | on-failure | never
  -y, --auto-approve       自动同意审批；--decline 自动拒绝
  -v, --verbose            打印推理增量；--json 只输出事件 JSON
  --timeout <sec>          等待 turn 结束的超时，默认 1800`;
}

const log = (...a) => process.stderr.write(a.join(' ') + '\n');

// ---------- RPC over WebSocket ----------
class CodexClient {
  #listeners = new Map();

  constructor(url) {
    this.url = url;
    this.ws = null;
    this.nextId = 1;
    this.pending = new Map();
  }

  on(name, fn, { once = false } = {}) {
    const list = this.#listeners.get(name) ?? [];
    list.push({ fn, once });
    this.#listeners.set(name, list);
    return () => this.off(name, fn);
  }

  off(name, fn) {
    const list = this.#listeners.get(name) ?? [];
    this.#listeners.set(name, list.filter((l) => l.fn !== fn));
  }

  emit(name, detail) {
    for (const l of [...(this.#listeners.get(name) ?? [])]) {
      if (l.once) this.off(name, l.fn);
      try { l.fn({ detail }); } catch (e) { log(`[listener error] ${e.stack}`); }
    }
  }

  connect() {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(this.url);
      this.ws = ws;
      ws.onopen = () => {
        log(`[已连接] ${this.url}`);
        resolve();
      };
      ws.onerror = (e) => reject(new Error(`WebSocket 连接失败: ${e.message ?? e.type}`));
      ws.onclose = (e) => {
        this.emit('closed', { code: e.code, reason: e.reason });
        for (const { reject: rj } of this.pending.values()) rj(new Error('连接已关闭'));
        this.pending.clear();
      };
      ws.onmessage = (e) => this.#onMessage(String(e.data));
    });
  }

  #onMessage(raw) {
    let msg;
    try { msg = JSON.parse(raw); } catch { return this.emit('raw', raw); }

    // 1) 响应（带 id 且有 result/error）
    if (msg.id !== undefined && msg.method === undefined) {
      const p = this.pending.get(msg.id);
      if (p) {
        this.pending.delete(msg.id);
        msg.error ? p.reject(new Error(JSON.stringify(msg.error))) : p.resolve(msg.result);
        return;
      }
    }
    // 2) 服务端 -> 客户端 请求（带 method 和 id），需回复
    if (msg.id !== undefined && msg.method) return this.emit('serverRequest', msg);
    // 3) 通知
    this.emit('notification', msg);
  }

  send(msg) { this.ws.send(JSON.stringify(msg)); }

  request(method, params) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.send({ method, id, params });
    });
  }

  notify(method, params) { this.send(params === undefined ? { method } : { method, params }); }

  respond(id, result) { this.send({ id, result }); }
  respondError(id, message) { this.send({ id, error: { code: -32603, message } }); }

  close() { try { this.ws?.close(); } catch {} }
}

// ---------- 主流程 ----------
const client = new CodexClient(opts.url);
try {
  await client.connect();
} catch (e) {
  console.error(`[连接失败] ${opts.url} — ${e.message}`);
  console.error('  请确认 app-server 已启动，例如：codex app-server --listen ' + opts.url.replace(/^ws/, 'ws'));
  process.exit(1);
}

const init = await client.request('initialize', {
  clientInfo: { name: 'codex-ws-client', title: 'Codex WS Client', version: '1.0.0' },
  capabilities: { experimentalApi: true, requestAttestation: false },
});
log(`[server] ${init.userAgent}  codexHome=${init.codexHome}`);

client.notify('initialized');

// 建立 / 恢复 thread
const threadResp = opts.thread
  ? await client.request('thread/resume', {
      threadId: opts.thread,
      ...(opts.model ? { model: opts.model } : {}),
      ...(opts.cwd ? { cwd: opts.cwd } : {}),
      ...(opts.approval ? { approvalPolicy: opts.approval } : {}),
      ...(opts.sandbox ? { sandbox: opts.sandbox } : {}),
    })
  : await client.request('thread/start', {
      ...(opts.model ? { model: opts.model } : {}),
      cwd: opts.cwd,
      ...(opts.approval ? { approvalPolicy: opts.approval } : {}),
      ...(opts.sandbox ? { sandbox: opts.sandbox } : {}),
    });

const threadId = threadResp.thread.id;
log(`[thread] ${threadId}  model=${threadResp.model}  cwd=${threadResp.cwd}  sandbox=${JSON.stringify(threadResp.sandbox)}`);

// ---------- 事件渲染 ----------
let inAgentMessage = false;   // 正在流式输出 assistant 文本
let inReasoning = false;
let pendingApproval = null;   // { id, method, params }
let rl = null;                // readline 实例（交互模式）

client.on('notification', (ev) => {
  const { method, params } = ev.detail;
  if (opts.json) return void process.stdout.write(JSON.stringify(ev.detail) + '\n');

  switch (method) {
    case 'item/agentMessage/delta':
      if (!inAgentMessage) { process.stdout.write('\n'); inAgentMessage = true; }
      process.stdout.write(params.delta);
      break;

    case 'item/reasoning/summaryTextDelta':
    case 'item/reasoning/textDelta':
      if (!opts.verbose) break;
      if (inAgentMessage) { process.stdout.write('\n'); inAgentMessage = false; }
      if (!inReasoning) { process.stdout.write('\x1b[2m💭 '); inReasoning = true; }
      process.stdout.write(params.delta);
      break;

    case 'item/started': {
      const it = params.item ?? {};
      if (inAgentMessage) { process.stdout.write('\n'); inAgentMessage = false; }
      if (inReasoning) { process.stdout.write('\x1b[0m\n'); inReasoning = false; }
      if (it.type === 'commandExecution') {
        log(`\x1b[36m▶ exec\x1b[0m ${it.command ?? it.commandLine ?? ''}`);
      } else if (it.type === 'fileChange') {
        log(`\x1b[33m✎ patch\x1b[0m ${(it.changes ?? []).length} file(s)`);
      } else if (it.type === 'mcpToolCall' || it.type === 'dynamicToolCall') {
        log(`\x1b[35m⚙ tool\x1b[0m ${it.tool ?? it.name ?? ''}`);
      } else if (it.type === 'plan' && it.text) {
        log(`\x1b[2m📋 plan: ${it.text.replace(/\n/g, ' ').slice(0, 200)}\x1b[0m`);
      }
      break;
    }

    case 'item/completed': {
      const it = params.item ?? {};
      if (inReasoning) { process.stdout.write('\x1b[0m'); inReasoning = false; }
      if (it.type === 'commandExecution') {
        const code = it.exitCode ?? it.exit_code;
        log(`\x1b[36m◀ exec done\x1b[0m exit=${code ?? '?'}`);
      }
      break;
    }

    case 'turn/completed': {
      if (inAgentMessage) { process.stdout.write('\n'); inAgentMessage = false; }
      if (inReasoning) { process.stdout.write('\x1b[0m\n'); inReasoning = false; }
      const t = params.turn ?? {};
      const err = t.error ? ` error=${JSON.stringify(t.error)}` : '';
      log(`\x1b[2m── turn ${t.status ?? 'done'}${err} ──\x1b[0m`);
      client.emit('turnDone', t);
      break;
    }

    case 'error':
      log(`\x1b[31m[error] ${JSON.stringify(params)}\x1b[0m`);
      break;

    // 其余通知静默；需要看全部事件时加 --json
  }
});

// 服务端 -> 客户端 请求（审批 / 用户输入等）
client.on('serverRequest', async (ev) => {
  const { id, method, params } = ev.detail;
  if (opts.json) process.stdout.write(JSON.stringify(ev.detail) + '\n');

  if (opts.autoApprove) return decide(id, 'acceptForSession');
  if (opts.autoDecline) return decide(id, 'decline');

  if (method === 'item/commandExecution/requestApproval') {
    log(`\x1b[33m⚠ 需要审批执行命令:\x1b[0m ${params.command ?? ''} (cwd=${params.cwd ?? ''})${params.reason ? ' 原因: ' + params.reason : ''}`);
  } else if (method === 'item/fileChange/requestApproval') {
    log(`\x1b[33m⚠ 需要审批文件修改\x1b[0m${params.reason ? ' 原因: ' + params.reason : ''}`);
  } else {
    log(`\x1b[33m⚠ 服务端请求 ${method}:\x1b[0m ${JSON.stringify(params).slice(0, 400)}`);
  }

  if (process.stdin.isTTY && rl) {
    pendingApproval = { id, method };
    rl.setPrompt('同意? [y=本次 / a=本会话 / n=拒绝] > ');
    rl.prompt();
    return;
  }
  // 非交互环境：默认拒绝（安全兜底）
  log('  非交互模式，默认拒绝（可用 --auto-approve / --decline 调整）');
  decide(id, 'decline');
});

function decide(id, decision) {
  pendingApproval = null;
  client.respond(id, { decision });
  log(`  → ${decision}`);
}

// ---------- 发送一条用户消息并等待 turn 结束 ----------
async function ask(text) {
  const done = new Promise((resolve) => client.on('turnDone', resolve, { once: true }));
  await client.request('turn/start', {
    threadId,
    input: [{ type: 'text', text, text_elements: [] }],
  });
  const timer = setTimeout(() => {
    log(`\x1b[31m[超时] 等待 turn 完成超过 ${opts.timeout}s\x1b[0m`);
    client.emit('turnDone', { status: 'timeout' });
  }, opts.timeout * 1000);
  await done;
  clearTimeout(timer);
}

// ---------- 交互循环 ----------
function setupRepl() {
  rl = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: process.stdin.isTTY });
  rl.on('line', async (line) => {
    const text = line.trim();
    if (!text) { if (process.stdin.isTTY) rl.prompt(); return; }
    if (pendingApproval) {
      if (/^(y|yes|是)$/i.test(text)) decide(pendingApproval.id, 'accept');
      else if (/^(a|all|本会话)$/i.test(text)) decide(pendingApproval.id, 'acceptForSession');
      else decide(pendingApproval.id, 'decline');
      if (process.stdin.isTTY) rl.prompt();
      return;
    }
    rl.pause();
    try { await ask(text); } catch (e) { log(`\x1b[31m[错误] ${e.message}\x1b[0m`); }
    rl.resume();
    if (process.stdin.isTTY) rl.prompt();
  });
  rl.on('close', () => { client.close(); process.exit(0); });
  if (process.stdin.isTTY) {
    log('\n输入消息回车发送（Ctrl-D 退出）。审批时输入 y=本次 / a=本会话 / n=拒绝\n');
    rl.prompt();
  }
}

if (opts.messages.length) {
  // 命令行参数：逐条发送后退出
  for (const msg of opts.messages) {
    try { await ask(msg); } catch (e) { log(`\x1b[31m[错误] ${e.message}\x1b[0m`); }
  }
  client.close();
  process.exit(0);
} else if (process.stdin.isTTY) {
  setupRepl();
} else {
  // 管道输入：整个 stdin 作为一条消息
  let buf = '';
  process.stdin.setEncoding('utf8');
  for await (const chunk of process.stdin) buf += chunk;
  const text = buf.trim();
  if (text) { try { await ask(text); } catch (e) { log(`\x1b[31m[错误] ${e.message}\x1b[0m`); } }
  client.close();
  process.exit(0);
}
