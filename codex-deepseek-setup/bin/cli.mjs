#!/usr/bin/env node
/**
 * npx front-end for the Codex + DeepSeek adapter (nexita relay).
 *
 *   npx codex-deepseek-setup              装（问你要 key）
 *   npx codex-deepseek-setup uninstall    停服务 + 还原 config.toml + 删适配器
 *   npx codex-deepseek-setup status       现在是什么状态
 *   npx codex-deepseek-setup ui           打开实时请求/回复网页
 *   npx codex-deepseek-setup logs -n 50   看抓取到的请求
 *
 * 这是个**薄壳**，不是重写：真正干活的还是 install.sh / uninstall.sh /
 * files/*.py —— 那部分已经对着 launchd、systemd 和网关验过。Node 在这里只
 * 负责让 `npx` 成为唯一的安装入口（做子命令、状态探查、已装检测）。
 *
 * 两个和 npx 有关的实现细节：
 *  1. bin 在 npx 缓存里是 symlink，但 node 默认会把主模块解析成真实路径，
 *     所以 import.meta.url 直接指向 node_modules/<pkg>/bin/cli.mjs，
 *     往上找 package.json 和 install.sh 都不会错（不需要 readlink 那一套）。
 *  2. npx 缓存目录（npm config get cache）可以被清理，绝不能把常驻进程跑在
 *     里面。install.sh 本来就会把适配器拷到 ~/.codex/deepseek-adapter/，
 *     服务只跑那份拷贝 —— npx 只是"把文件送过去"的通道。
 */
import { spawnSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import http from "node:http";
import readline from "node:readline";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PKG = JSON.parse(readFileSync(path.join(ROOT, "package.json"), "utf8"));
const IS_MAC = process.platform === "darwin";
const IS_LINUX = process.platform === "linux";

// ---------------------------------------------------------------- utilities
const readText = (p) => {
  try {
    return readFileSync(p, "utf8");
  } catch {
    return null;
  }
};

const readJson = (p) => {
  const t = readText(p);
  if (t === null) return null;
  try {
    return JSON.parse(t);
  } catch {
    return null;
  }
};

const mask = (key) =>
  !key ? "-" : key.length <= 10 ? "****" : `${key.slice(0, 4)}…${key.slice(-4)}`;

const hasFlag = (argv, ...names) => argv.some((a) => names.includes(a));

/** Value of a `--flag value` / `--flag=value` pair, or null. */
function flagValue(argv, name) {
  const eq = argv.find((a) => a.startsWith(`${name}=`));
  if (eq) return eq.slice(name.length + 1);
  const i = argv.indexOf(name);
  if (i >= 0 && argv[i + 1] && !argv[i + 1].startsWith("-")) return argv[i + 1];
  return null;
}

const expandTilde = (p) => p.replace(/^~(?=$|\/)/, os.homedir());

/** Codex home, honouring the same --codex-home / $CODEX_HOME that install.sh uses. */
const codexHome = (argv) =>
  path.resolve(expandTilde(flagValue(argv, "--codex-home") || process.env.CODEX_HOME || path.join(os.homedir(), ".codex")));

const adapterDir = (argv) => path.join(codexHome(argv), "deepseek-adapter");

const serviceLabel = () =>
  `com.${process.env.USER || (() => { try { return os.userInfo().username; } catch { return "user"; } })()}.codex-deepseek-adapter`;

/** Port the adapter actually listens on, read back from config.toml. */
function adapterPort(argv) {
  const cfg = readText(path.join(codexHome(argv), "config.toml")) || "";
  const m = cfg.match(/base_url\s*=\s*"http:\/\/(?:127\.0\.0\.1|localhost):(\d+)/);
  return m ? Number(m[1]) : 8899;
}

/** Provider tables other than `deepseek` that already point at the adapter. */
function repointedProviders(argv) {
  const cfg = readText(path.join(codexHome(argv), "config.toml"));
  if (!cfg) return [];
  const marks = [];
  const re = /^[ \t]*\[model_providers\.([^\]]+)\][ \t]*$/gm;
  let m;
  while ((m = re.exec(cfg)) !== null) marks.push({ name: m[1].trim(), at: m.index });
  const loopback = /^[ \t]*base_url[ \t]*=[ \t]*"https?:\/\/(?:127\.0\.0\.1|localhost)(?::\d+)?\/?"[ \t]*$/m;
  return marks
    .filter((mk, i) => {
      const body = cfg.slice(mk.at, i + 1 < marks.length ? marks[i + 1].at : cfg.length);
      return mk.name !== "deepseek" && loopback.test(body);
    })
    .map((mk) => mk.name);
}

/** Prompts on the tty; returns the typed line, or `def` when the user just hits enter. */
function ask(question, def = "Y") {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question(question, (answer) => {
      rl.close();
      const a = String(answer).trim();
      resolve(a === "" ? def : a);
    });
  });
}

/** Runs a child with our own tty, so install.sh's wizard keeps working. */
function run(cmd, args) {
  const r = spawnSync(cmd, args, { stdio: "inherit", cwd: ROOT });
  if (r.error) {
    console.error(`  无法执行 ${cmd}：${r.error.message}`);
    return 1;
  }
  return r.status === null ? 1 : r.status;
}

function httpGet(url, timeoutMs) {
  return new Promise((resolve) => {
    const req = http.get(url, (res) => {
      let body = "";
      res.on("data", (c) => (body += c));
      res.on("end", () => resolve({ status: res.statusCode, body }));
    });
    req.on("error", (e) => resolve({ status: 0, body: e.code || e.message }));
    req.setTimeout(timeoutMs, () => {
      req.destroy();
      resolve({ status: 0, body: "timeout" });
    });
  });
}

function serviceState() {
  const label = serviceLabel();
  if (IS_MAC) {
    const r = spawnSync("launchctl", ["list"], { encoding: "utf8" });
    const line = (r.stdout || "").split("\n").find((l) => l.trim().endsWith(label));
    if (!line) return { registered: false, text: "未注册" };
    const [pid, status] = line.trim().split(/\s+/);
    return { registered: true, text: `已注册 pid=${pid === "-" ? "未运行" : pid} last_exit=${status}` };
  }
  const r = spawnSync("systemctl", ["--user", "is-active", `${label}.service`], { encoding: "utf8" });
  const state = (r.stdout || "").trim() || "unknown";
  return { registered: existsSync(path.join(os.homedir(), ".config/systemd/user", `${label}.service`)), text: state };
}

function adapterProcesses() {
  const r = spawnSync("ps", ["-Ao", "pid=,command="], { encoding: "utf8" });
  return (r.stdout || "")
    .split("\n")
    .filter((l) => l.includes("adapter.py") && !l.includes("grep"))
    .map((l) => l.trim());
}

/** Display width, counting CJK as two columns so the columns line up. */
const width = (s) =>
  [...s].reduce(
    (n, c) => n + (/[\u1100-\u115F\u2E80-\uA4CF\uAC00-\uD7A3\uF900-\uFAFF\uFE30-\uFE6F\uFF00-\uFF60\uFFE0-\uFFE6]/.test(c) ? 2 : 1),
    0,
  );
const pad = (s, n) => s + " ".repeat(Math.max(0, n - width(s)));

const todayDir = () => {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
};

function todayCaptureCount(argv) {
  const dir = path.join(adapterDir(argv), "logs", "exchanges", todayDir());
  try {
    return readdirSync(dir).filter((f) => f.endsWith(".json")).length;
  } catch {
    return 0;
  }
}

// ---------------------------------------------------------------- commands
async function cmdInstall(argv) {
  if (hasFlag(argv, "-h", "--help")) return run("bash", [path.join(ROOT, "install.sh"), "--help"]);

  let args = argv.slice();
  const adir = adapterDir(args);
  const installed = existsSync(path.join(adir, "adapter.py"));

  if (installed && !hasFlag(args, "--key")) {
    const stored = readJson(path.join(adir, "keys.json"))?.open_model_key || "";
    console.log(`\n  ── 已经装过了 ──────────────────────────────────────`);
    console.log(`  适配器目录 : ${adir}`);
    if (stored) {
      console.log(`  已保存的 key : ${mask(stored)}`);
      const a = await ask(
        "  回车 = 用它重新安装/修复（升级、换端口都走这里）\n" +
          "  输入 n 后回车 = 改成手动输入新的 key\n" +
          "  Control-C = 放弃\n  > ",
      );
      if (!/^n/i.test(a)) args = ["--key", stored, ...args];
    } else {
      console.log("  没找到已保存的 key，接下来会问你要。");
    }
    // 别把用户之前特意 repoint 过的 provider 丢掉
    for (const name of repointedProviders(args)) {
      if (!hasFlag(args, "--repoint-provider")) args = [...args, "--repoint-provider", name];
    }
    console.log("");
  }

  return run("bash", [path.join(ROOT, "install.sh"), ...args]);
}

async function cmdUninstall(argv) {
  const passthrough = argv.filter((a) => !["-y", "--yes"].includes(a));
  const adir = adapterDir(passthrough);
  const label = serviceLabel();

  if (!existsSync(adir)) {
    console.log(`  没找到 ${adir}，看起来没装过（或已经卸干净了）。`);
    if (!IS_MAC) console.log(`  服务单元检查：${serviceState().text}`);
    return 0;
  }

  console.log(`\n  将要执行：`);
  console.log(`    1. 停掉并移除后台服务 ${label}`);
  console.log(`    2. 用安装时的备份还原 ${path.join(codexHome(passthrough), "config.toml")}`);
  console.log(`    3. 删除 ${adir}（含里面的请求日志）`);

  if (!hasFlag(argv, "-y", "--yes")) {
    // Default is CANCEL here, matching 一键卸载.command: a stray enter must not
    // wipe someone's setup. Pass -y / --yes to skip the prompt in scripts.
    const a = await ask("  确认卸载请输入 y 再回车（直接回车 = 取消）：", "");
    if (!/^y/i.test(a)) {
      console.log("  已取消，什么都没改。");
      return 3;
    }
  }
  return run("bash", [path.join(ROOT, "uninstall.sh"), ...passthrough]);
}

async function cmdStatus(argv) {
  const home = codexHome(argv);
  const adir = adapterDir(argv);
  const port = adapterPort(argv);
  const installed = existsSync(path.join(adir, "adapter.py"));
  const key = readJson(path.join(adir, "keys.json"))?.open_model_key || "";
  const settings = readJson(path.join(adir, "settings.json")) || {};
  const cfg = readText(path.join(home, "config.toml")) || "";
  const hasBlock = cfg.includes("codex-deepseek: managed block");
  const model = (cfg.match(/^model[ \t]*=[ \t]*"([^"]+)"/m) || [])[1] || "-";
  const catalog = /model_catalog_json[ \t]*=[ \t]*"([^"]+)"/.exec(cfg)?.[1] || "-";
  const providers = repointedProviders(argv);
  const svc = serviceState();
  const procs = adapterProcesses();
  const health = installed ? await httpGet(`http://127.0.0.1:${port}/__health`, 3000) : null;

  const row = (label, value) => console.log(`  ${pad(label, 12)}: ${value}`);
  console.log(`\n  Codex + DeepSeek adapter  v${PKG.version}`);
  console.log(`  ${"─".repeat(52)}`);
  row("Codex 目录", home);
  row("适配器目录", `${adir}${installed ? "" : "  （不存在）"}`);
  row("后台服务", `${serviceLabel()}  ${svc.text}`);
  row(
    "适配器进程",
    procs.length
      ? procs
          .map((p) => {
            const pid = p.split(/\s+/)[0];
            const script = /\/[^\s]*adapter\.py/.exec(p)?.[0] || "?";
            return `${pid}  ${script}`;
          })
          .join("\n" + " ".repeat(16))
      : "没有在跑",
  );
  row("健康检查", health ? `${health.status === 200 && health.body.trim() === "ok" ? "ok" : `异常 (${health.status} ${health.body.slice(0, 60)})`}   http://127.0.0.1:${port}/__health` : "-");
  row("网页", `http://127.0.0.1:${port}/__ui${settings.ui === false ? "  （settings.json 里已关闭）" : ""}`);
  row("日志落盘", settings.capture === false ? "已关闭（settings.json capture=false）" : `开，保留 ${settings.capture_keep_days ?? 7} 天`);
  row("主模型", `${model}   catalog=${catalog}`);
  row("provider", ["deepseek", ...providers].map((p) => `${p} -> http://127.0.0.1:${port}`).join(", "));
  row("托管块", hasBlock ? "在 config.toml 里（卸载时可还原）" : "没找到");
  row("网关 key", `${mask(key)}${key ? "   （~/.codex/deepseek-adapter/keys.json, 600）" : ""}`);
  row("今日抓取", `${todayCaptureCount(argv)} 次请求`);
  console.log("");
  if (!installed) console.log(`  装：npx ${PKG.name}\n`);
  return 0;
}

function cmdUi(argv) {
  const port = adapterPort(argv);
  const url = `http://127.0.0.1:${port}/__ui`;
  console.log(`  ${url}`);
  const r = spawnSync(IS_MAC ? "open" : "xdg-open", [url], { stdio: "ignore" });
  if (r.error) console.log("  打不开浏览器，手动复制上面的地址即可。");
  return 0;
}

function cmdLogs(argv) {
  const adir = adapterDir(argv);
  const script = path.join(adir, "captures.py");
  if (!existsSync(script)) {
    console.error(`  没找到 ${script}，先装一次。`);
    return 1;
  }
  const passthrough = argv.filter((a) => a !== "--codex-home" && a !== flagValue(argv, "--codex-home"));
  const env = { ...process.env, CODEX_ADAPTER_SETTINGS: path.join(adir, "settings.json") };
  const r = spawnSync("python3", [script, ...passthrough], { stdio: "inherit", env });
  if (r.error) {
    console.error(`  无法执行 python3：${r.error.message}`);
    return 1;
  }
  return r.status === null ? 1 : r.status;
}

function cmdHelp() {
  const n = PKG.name;
  console.log(`
  Codex + DeepSeek adapter  v${PKG.version}
  把 Codex CLI 接到 DeepSeek 网关。日常就用这三条：

    npx ${n}                装（问你一个 key，其余回车）
    npx ${n} status         现在是什么状态
    npx ${n} uninstall      停服务 + 还原 config.toml + 删适配器

  用法：npx ${n} [install|uninstall|status|ui|logs|help] [选项]

    install (默认)          引导式安装；已装过则默认沿用原 key 重装/修复
    uninstall, del, rm      卸载并还原；默认需输入 y 确认（-y / --yes 跳过）
    status, st              安装目录 / 服务 / 进程 / 健康 / 端口 / key（打码）
    ui, open                打开实时请求·回复网页 http://127.0.0.1:<port>/__ui
    logs [-n 50|--show 1]   浏览抓取到的请求与回复（转发给 captures.py）
    help, -h                这段说明
    --version, -v           版本号

  install / uninstall 认的参数会原样转给底层脚本（npx ${n} install --help
  看全量），常用的是：

    --key KEY               直接给 key（跳过问答）
    --port N                适配器端口，默认 8899
    --model SLUG            主模型，默认 deepseek-v4.1-flash
    --codex-home DIR        Codex 目录，默认 $CODEX_HOME 或 ~/.codex
    --repoint-provider NAME 把历史会话记录的 provider 也指到适配器（如 OpenAI）
    --no-capture            不落盘请求日志     --no-ui  不提供网页
    --no-service            只写文件，不注册后台服务
    --skip-verify           跳过装后自检
    --openai-key KEY        同时用 gpt-* 模型时的第二把 key
    --capture-keep-days N   日志保留天数，默认 7     --purge（卸载）连模型目录也删

  说明：
    · 适配器会被拷到 <codex-home>/deepseek-adapter/，launchd/systemd 只运行
      那份拷贝；npx 缓存被清掉也不影响已装好的服务。
    · 装完记得完全退出并重开 Codex 桌面端（它启动时才读 config.toml）。
    · 需要 python3（macOS 自带 /usr/bin/python3 即可），适配器是纯标准库。
`);
  return 0;
}

// -------------------------------------------------------------------- main
async function main() {
  const raw = process.argv.slice(2);

  if (!IS_MAC && !IS_LINUX) {
    console.error(`  这个包只支持 macOS / Linux（当前 ${process.platform}）：适配器是 launchd/systemd 常驻服务。`);
    return 1;
  }

  if (raw[0] === "--version" || raw[0] === "-v") {
    console.log(PKG.version);
    return 0;
  }

  const aliases = {
    install: "install",
    i: "install",
    uninstall: "uninstall",
    un: "uninstall",
    del: "uninstall",
    remove: "uninstall",
    rm: "uninstall",
    status: "status",
    st: "status",
    ui: "ui",
    open: "ui",
    web: "ui",
    logs: "logs",
    log: "logs",
    captures: "logs",
    help: "help",
  };

  let cmd = "install";
  let argv = raw;
  if (argv.length && !argv[0].startsWith("-")) {
    const key = argv[0].toLowerCase();
    if (!(key in aliases)) {
      console.error(`  不认识的子命令：${argv[0]}\n  试试：npx ${PKG.name} help`);
      return 2;
    }
    cmd = aliases[key];
    argv = argv.slice(1);
  }

  switch (cmd) {
    case "help":
      return cmdHelp();
    case "install":
      return cmdInstall(argv);
    case "uninstall":
      return cmdUninstall(argv);
    case "status":
      return cmdStatus(argv);
    case "ui":
      return cmdUi(argv);
    case "logs":
      return cmdLogs(argv);
  }
  return 1;
}

main().then(
  (code) => process.exit(code),
  (err) => {
    console.error(`  出错了：${err && err.message ? err.message : err}`);
    process.exit(1);
  },
);
