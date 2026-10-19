# Codex 改用 DeepSeek（nexita 网关）—— 一键安装 + 原理说明

在一台已经装好 Codex CLI（≥ 0.154）的 macOS / Linux 机器上，**双击 `一键安装.command`** 就行：
它会问你 1~2 个问题（主要就是那把网关 key），其余全部用推荐默认值。

```bash
tar xzf codex-deepseek-setup.tgz && cd codex-deepseek-setup
open 一键安装.command          # macOS；Linux 用 bash 一键安装.command

# 或者仍用命令行（效果完全一样，只是要自己把参数补齐）
./install.sh --key sk-你的网关key
```

已经有 Node 的同事可以直接 `npx codex-deepseek-setup`（见第十二节，同一个东西的 npm 通道），
不用解压也不用管路径。

装完重启一下 Codex 桌面端（如果开着），就能用了。想还原：双击 `一键卸载.command`。

---

## 零、不想敲命令：双击就行

包里有两个可以直接双击的文件（macOS 会自己开「终端」运行；Linux 上 `bash 一键安装.command` 一样可用）：

| 双击这个 | 作用 |
|---|---|
| **一键安装.command** | 问 1~2 个问题 → 自动装好 → 问你要不要打开日志网页 |
| **一键卸载.command** | 问一次确认 → 还原到安装前 |

要准备的只有一样：**网关 key**（`sk-...`）。除了 key 之外全部直接按回车，问答长这样：

```
key: ****************                              ← 粘贴 key（输入时不显示字符）
gpt key（可留空）:                                 ← 不用 gpt-* 模型就回车
以前跑过 gpt-* 的 Codex 任务吗？回车 = 是：         ← 不确定就回车
开始安装？回车 = 开始，输入 n 取消：
```

小技巧与例外情况：

- **先把 key 复制到剪贴板再双击**：脚本会提示「剪贴板里已有一串像 key 的文本，直接回车就用它」，连粘贴都省了。
- 想改端口 / 模型 / 关掉日志网页这些，就得走命令行重装（`./install.sh --key ... --port ...`），引导模式只用推荐默认值。
- **双击弹「无法打开，因为 Apple 无法检查它是否包含恶意软件」**：这是 macOS 对「从网上下载的文件」的隔离标记（quarantine），跟脚本内容无关。任选一种解法：
  1. 右键点文件 → **打开** → 再点一次「打开」（只需一次，之后双击正常）；
  2. 或者在该文件夹打开终端跑一次：`xattr -dr com.apple.quarantine .`
- **双击后被文本编辑器打开了**（说明文件丢了执行权限）：在该文件夹运行一次 `chmod +x 一键*.command`。
- 装完想确认在跑：终端里 `curl -s http://127.0.0.1:8899/__health`（返回 `ok`），或直接开日志网页 <http://127.0.0.1:8899/__ui>。
- 脚本退出码：`0` 成功、`3` 用户在问答里取消（什么都没改）、其他 = 失败。

---

## 一、为什么不只是"改两行 config"

直接把 `model_provider` 指向网关、`model` 换成 `deepseek-v4.1-flash` 会踩两个坑，这也是我在自己机器上踩完之后总结出来的：

### 坑 1：`max_tokens is less than thinking.budget_tokens`

nexita 网关把 OpenAI 的 `responses` 请求转成 Anthropic 的 Messages 协议，于是：

| Codex 发的 `reasoning.effort` | 网关推导出的 `thinking.budget_tokens` | 需要的 `max_tokens` |
|---|---|---|
| low / medium | ≤ 4096 | 默认 4096 就够 |
| high | 8192 | ≥ 12288 |
| xhigh / max | 16384 | ≥ 32768 |
| none / minimal / ultra | — | **网关直接拒绝** |

网关把 `max_tokens` 缺省填 4096，而 Anthropic 要求 `max_tokens > thinking.budget_tokens`，所以 **effort ≥ high 的请求一律 400**：

```
Invalid request body: max_tokens is less than thinking.budget_tokens
```

问题是 **Codex 根本不发 `max_output_tokens`**（我反汇编了 0.154.0 的二进制并抓包确认），provider 配置里也没有"附加 body 字段"的口子，没有任何 `CODEX_*` 环境变量能控制它。`~/.codex/agents/*.toml` 里一堆角色用的是 high/xhigh（那批文件由 oh-my-codex 生成，改了会被覆盖），所以不能靠"把 effort 降下来"绕过去。

→ 结论：需要一个**本地适配器**，在请求进网关前补上 `max_output_tokens`。

### 坑 2：续聊旧会话报 `Model "xxx" is not supported by any configured account in this group`

Codex 的每个会话文件第一行 `session_meta` 都记录了 `model_provider`。续聊旧会话时：

- **模型**取当前 config → `deepseek-v4.1-flash` ✅
- **provider**用会话里记录的（切换前是 `OpenAI`）→ 走 `[model_providers.OpenAI]` 的 base_url 和它自己的 key ❌

而网关里这两个 key 的模型清单是**完全不重叠**的（我实测：deepseek key 只有 deepseek/glm/kimi 共 17 个；OpenAI key 只有 gpt-5.x/gpt-6 共 22 个）。于是旧会话拿 OpenAI 的 key 去请求 deepseek 模型 → 404。

我这台机器 **908 个会话里有 870 个**记录的 provider 是 `OpenAI`，所以这个坑几乎必然踩到。

→ 结论：适配器要**按模型名选 key**（`files/keys.json`），旧会话不用改历史文件也能用；同时 `[model_providers.OpenAI]` 的 `base_url` 也指向适配器（用 `--repoint-provider OpenAI`）。

### 坑 3：模型元数据

Codex 0.154 只支持 `wire_api = "responses"`（用 `chat` 会直接报不支持），并且需要 `model_catalog_json` 提供模型目录，否则一直提示 `Model metadata for xxx not found`；同时必须设 `web_search = "disabled"`，否则某些模型下会报 `Invalid schema for function 'web_search'`。

---

## 二、前提

- Codex CLI ≥ 0.154：`codex --version`
- Python 3.8+（macOS 自带的 `/usr/bin/python3` 就行，脚本只用标准库）
- 网关 key（能访问 `deepseek-v4.1-flash`），网关地址默认 `https://codeapi.nexita.net`

## 三、安装

```bash
./install.sh --key sk-xxxxxxxx

# 不带参数 = 同样的引导问答（也是双击 一键安装.command 时跑的那套）
./install.sh
```

不带 `--key` 且在终端里运行时，脚本会依次问：key、可选第二把 gpt key、是否兼容老会话，
然后打印一份「将按下面的设置安装」的清单让你确认。非交互（管道 / CI）下仍要求 `--key`，不会卡住。

常用参数：

| 参数 | 默认 | 说明 |
|---|---|---|
| `--key` | 必填 | 主 key（deepseek/glm/kimi 等 open 模型用） |
| `--base-url` | `https://codeapi.nexita.net` | 网关地址 |
| `--model` | `deepseek-v4.1-flash` | 主模型（同时写进目录） |
| `--model-alt` | `deepseek-v4-pro` | 目录里的第二个模型，`""` 表示不要 |
| `--port` | `8899` | 本地适配器端口 |
| `--codex-home` | `$CODEX_HOME` 或 `~/.codex` | Codex 目录 |
| `--repoint-provider` | 无 | 例如 `OpenAI`：把历史会话记录的 provider 也指到适配器（**老用户建议加**） |
| `--openai-key` | 无 | 如果你还要用 gpt-* 模型，配上第二个 key，适配器会按模型自动选 |
| `--no-service` | 关 | 只写文件不起后台服务 |
| `--skip-verify` | 关 | 跳过安装后自检 |

老用户（有历史会话、且以前用过 gpt-6-astra）建议这样装：

```bash
./install.sh --key sk-xxxxxxxx --repoint-provider OpenAI --openai-key sk-你的gptkey
```

## 四、脚本到底改了哪 4 个地方

1. **`~/.codex/deepseek-adapter/adapter.py` + `captures.py` + `keys.json` + `settings.json`**
   本地透传代理（纯标准库，监听 `127.0.0.1:8899`）。只做两件事：按模型名选网关凭据、给 open 模型补 `max_output_tokens=32768`。流式返回原样搬运，其余请求一个字节都不动。`keys.json` / `settings.json` 权限 600。

2. **后台常驻服务**（macOS 用 launchd，Linux 用 systemd --user）
   `RunAtLoad` + `KeepAlive`，开机自启、挂了自动重启。macOS 标签默认 `com.<用户名>.codex-deepseek-adapter`。

3. **`~/.codex/config.toml`**（改动前会自动备份为 `config.toml.bak-时间戳`）
   顶部插入一段带标记的托管块，原有冲突的顶层设置会被打上 `#[codex-deepseek:disabled]` 标签保留（不删，方便改回去）：

   ```toml
   # >>> codex-deepseek: managed block (rewritten by install.sh) >>>
   model_provider = "deepseek"
   model = "deepseek-v4.1-flash"
   review_model = "deepseek-v4-pro"
   model_catalog_json = "/Users/你/.codex/models.json"
   web_search = "disabled"
   # <<< codex-deepseek: end managed block <<<

   [model_providers.deepseek]
   name = "deepseek"
   base_url = "http://127.0.0.1:8899"
   wire_api = "responses"
   experimental_bearer_token = "sk-xxxxxxxx"
   ```

4. **`~/.codex/models.json`**
   模型目录：`deepseek-v4.1-flash` / `deepseek-v4-pro`，reasoning 档位 `low / medium / high / xhigh / max`，默认 `medium`（网关不认 `none/minimal/ultra`，所以目录里没有）。

脚本是**幂等**的，重复执行不会重复插入（我实测两次安装后 config.toml 完全一致）。

## 五、请求 / 返回日志

代理是唯一能看到原始 HTTP 交换的地方，所以它把**每一次 Codex 请求**和**大模型的完整返回**（逐条 SSE 事件）都落盘：

```
~/.codex/deepseek-adapter/logs/exchanges/2026-09-23/
  11-37-27-50763-001-deepseek-v4.1-flash.json   完整数据（请求头 + 请求体 + 全部事件 + 元数据）
  11-37-27-50763-001-deepseek-v4.1-flash.txt    人读版（id / 请求头 / instructions / input / 回复 / 工具调用）
```

一个 Codex 回合通常产生多次请求（每轮工具调用一次），所以是**一请求一对文件**；文件名里带时间戳、pid、序号和模型名。

`.json` 关键字段：`status`、`model`、`adapter_note`（effort 与是否注入 max_output_tokens）、`duration_ms`、`auth`（这次用的哪个凭据）、`request_headers` / `response_headers`（已打码）、`codex`（id 元数据）、`request`（原样请求体）、`response.text` / `response.reasoning` / `response.tool_calls` / `response.usage` / `response.events`（全部原始事件）。

`.txt` 长这样（id 和请求头都在头部，单看一个文件就知道它属于哪个会话、哪次提问）：

```
==============================================================================
2026-09-23T11:37:27  POST /responses -> 200  (2322 ms, 6157 B)
model   : deepseek-v4.1-flash
note    : model=deepseek-v4.1-flash effort=low mt=-->32768
upstream: https://codeapi.nexita.net/responses
thread  : 01a0cc56-f668-7e33-afbc-1630c5b9386b        ← 会话 id
turn    : 01a0cc56-f740-7d22-b784-fdd507b6ab75   (你)   ← 一次用户提问的 id
message : msg_01a0cc56-fbaf-7e62-b088-90e06455aca1     ← 最新一条用户消息
kind    : turn / exec                                  ← request_kind / turn_trigger
auth    : adapter injected Bearer ****1cae (keys.json)
==============================================================================

--- REQUEST HEADERS ---
  authorization: Bearer ****1cae
  content-type: application/json
  user-agent: codex_exec/0.156.1 (Mac OS 15.7.3; arm64) iTerm.app (codex_exec; 0.156.1)
  accept: text/event-stream
  host: 127.0.0.1:8899
  originator: codex_exec
  session-id: 01a0cc56-f668-7e33-afbc-1630c5b9386b     ← 同样的 id 也在请求头里
  thread-id: 01a0cc56-f668-7e33-afbc-1630c5b9386b
  x-client-request-id: 01a0cc56-f668-7e33-afbc-1630c5b9386b
  x-codex-turn-metadata: {"turn_id":"01a0cc56-f740-...","request_kind":"turn",...}
  x-codex-window-id: 01a0cc56-f668-7e33-afbc-1630c5b9386b:0
  x-codex-beta-features: remote_compaction_v2

--- RESPONSE HEADERS ---
  content-type: text/event-stream
  server: nginx/1.20.1
  ...

--- REQUEST (134693 bytes) ---
instructions:
  You are Codex, an agent based on GPT-5. ...
input (6 items):
  [0] message role=user
        Run the shell command 'echo capcheck' ...
tools (14): shell, apply_patch, update_plan, ...

--- RESPONSE (6157 bytes, text/event-stream) ---
usage: {"input_tokens": 31421, "output_tokens": 56, ...}
reasoning summary:
  The user wants me to run a shell command ...
tool_call: exec_command {"cmd": "echo capcheck"}
```

请求头全部保存，但凭据类字段（`authorization` / `cookie` / 任何名字带 token、secret、password 的头）只留形如 `Bearer ****1cae` 的尾巴，避免日志里泄露完整 key。

查看方式：

```bash
cd ~/.codex/deepseek-adapter
./captures.py                 # 最近 20 次交换的表格（时间/状态/模型/耗时/字节/回复摘要）
./captures.py -n 50           # 多看几行
./captures.py --errors        # 只看失败或非 200 的
./captures.py --show 1        # 打印最新一次的完整 .txt
./captures.py --grep chmod    # 在所有抓取内容里搜关键字
./captures.py --json          # 机器可读的列表
```

保留策略在 `~/.codex/deepseek-adapter/settings.json`（安装参数 `--capture-dir` / `--capture-keep-days` / `--no-capture` 会写在这里）：

| 字段 | 默认 | 含义 |
|---|---|---|
| `capture` | `true` | 关掉就完全不落盘 |
| `capture_dir` | `logs/exchanges` | 存储目录（目录 700、文件 600） |
| `capture_keep_days` | `7` | 启动时删除超过 N 天的日期目录，`0` = 不按时间删 |
| `capture_max_bytes` | `8 MiB` | 单次交换保留的响应字节上限，超出部分丢弃并置 `response_truncated` |
| `capture_max_total_bytes` | `2 GiB` | 整棵树超限时从最旧的日期目录开始删 |
| `ui` | `true` | 是否提供 `/__ui` 实时网页 |
| `ui_token` | 无 | 设置了则网页需带 `?token=` 访问 |

环境变量 `CODEX_ADAPTER_CAPTURE*` 优先级高于 `settings.json`，方便临时排查（例如 `CODEX_ADAPTER_CAPTURE=0` 临时关掉）。

⚠️ 日志里有你的提示词、代码片段和模型回答，等于完整对话记录：目录权限刻意做成 700/600，别随手分享或同步到网盘；不需要时把 `capture` 设为 `false`。

### 网页版（实时看）

浏览器打开：**http://127.0.0.1:8899/__ui**

页面由适配器自己提供（同一个 8899 端口，也只监听回环，不需要额外服务）：

- **进行中**：请求一发出就出现卡片，模型的输出**逐字流式**显示（问题 + 正文 + 推理过程 + 工具调用 + 耗时 + tokens），完成时变绿并附上「查看完整请求/返回」
- **历史（按问题分组）**：一级是**问题**（父）：问题正文 + 开始/结束时间 + 请求数 + 总耗时 + 状态 + tokens 变化 + **最终回复**；最终回复默认只给一行干净摘要（去掉 markdown 符号与表格、`…` 截断），**展开后按 markdown 渲染**（标题、列表、表格、代码块、加粗、链接），底部标注模型/档位/字数与「看原始请求/返回」。点开二级是**这次问题下发出的每一次请求**：序号 / 时间 / HTTP / 模型·档位 / 耗时 / 请求→返回字节 / tokens / 本轮输出或工具名，点任意一条弹出完整的 `.txt`（可跳原始 `.json`）
- 归组规则（精确）：Codex 在每个请求的 `client_metadata` 里都带了 `thread_id`（会话）与 `turn_id`（**一次用户提问**）——同一提问下不管发多少次请求（工具调用、验证、重试）都是同一个 `turn_id`，所以直接用 `thread_id + turn_id` 归组。缺失这两个字段的请求（非 Codex 客户端或旧记录）退回用 `prompt_cache_key + 用户消息条数` 近似，并加一道保险：同一组请求间隔超过 2 小时自动切开（`CODEX_ADAPTER_GROUP_GAP_SECONDS` 可调）。
- 每个请求还带了来源信息，页面会直接显示：`thread_source` = `user`（你）/ `automation`（自动化）/ `guardian_review`（守卫审查）/ `memory_consolidation`（记忆整理）/ `system`（系统），`turn_trigger` = `composer` / `exec` / `automation_cron_scheduled`，子代理请求还会带 `subagent_kind` 与 `parent_turn_id`
- 请求头里还带一份相同的身份信息（`session-id`、`thread-id`、`x-client-request-id`、`x-codex-turn-metadata`、`x-codex-window-id`、`originator`、`user-agent`），并已一并存盘

每条记录的 `.txt` 头部也会带上这些 id，单看一个文件就知道它属于哪个会话/哪次提问（见上面的样例）。

交互：关键字搜索（问题/回复/模型/时间）、“只看失败”、“展开全部”、Esc 关弹窗；URL 加 `?expand=1` 可默认展开全部；断线自动重连（左上角绿点 = 实时连接正常）。

**主题**：右上角三档切换 —— `自动`（跟随系统）/ `暗` / `亮`，选择记在浏览器 localStorage，下次打开保持。临时指定可用 URL：`?theme=light`、`?theme=dark`、`?theme=auto`（发链接或截图时方便）。

关闭网页：`settings.json` 里 `"ui": false`（或安装时 `--no-ui`）。默认无口令；若想加一道口令，在 `settings.json` 写 `"ui_token": "你的口令"`，则访问 URL 需带 `?token=你的口令`（页面内部链接会自动携带）。

目录不可写或不想落盘时，把 `capture` 设为 `false` 仍可使用网页的实时流（只是不再写文件、没有历史）。

## 六、验证

安装脚本最后会自己跑：健康检查 → 一次 `effort=high` 的真实模型调用 → 一次 `codex exec` 冒烟测试。

手动核对：

```bash
curl -s http://127.0.0.1:8899/__health                      # ok
tail -f ~/.codex/deepseek-adapter/logs/adapter.log          # 看每次请求的 model/effort/是否注入

codex exec --skip-git-repo-check "回答 PONG"
codex exec -c model_reasoning_effort='"xhigh"' --skip-git-repo-check "回答 XHIGH-OK"   # 坑 1 的回归测试
```

日志每行形如：

```
2026-09-16T18:19:37 POST /responses -> 200 model=deepseek-v4.1-flash effort=xhigh mt=-->32768 3245B 3.3s
```

**⚠️ 必须做的一步：如果 Codex/ChatGPT 桌面端正在运行，请完全退出再打开。**
桌面端的 `codex ... app-server` 进程在启动时读取 `config.toml`，不重启就会继续用旧的 provider 配置（我这边就是这么复现出 404 的）。

## 七、常见报错对照

| 报错 | 原因 | 处理 |
|---|---|---|
| `Invalid request body: max_tokens is less than thinking.budget_tokens` | 请求没走适配器 | 确认 `base_url` 是 `http://127.0.0.1:8899`、适配器在跑（`/__health`） |
| `Model "xxx" is not supported by any configured account in this group` | key 和模型不匹配（典型：旧会话的 provider 用了另一个 key） | 加 `--repoint-provider OpenAI` 重装，或把该 key 的模型清单查出来对比：`curl -H "Authorization: Bearer $KEY" https://codeapi.nexita.net/v1/models` |
| `Model metadata for xxx not found` | 没有 `model_catalog_json` | 重跑 `install.sh` |
| `Invalid schema for function 'web_search'` | 没设 `web_search = "disabled"` | 重跑 `install.sh` |
| `429 All available accounts exhausted` / `502 Our servers are currently overloaded` | 网关上游额度/过载，与本地配置无关 | 等一会儿重试；`curl` 直连网关对比即可确认 |
| `thread ... already has an active writer` | 该会话正被桌面端占用 | 关掉桌面端里那个会话，或直接用桌面端继续 |

看适配器日志的 `note` 字段最省事：`mt=-->32768` 表示补了；`(passthrough)` 表示识别为 gpt-* 模型、原样转发。

## 八、想切回 gpt-6-astra

把托管块那 5 行注释掉、把带 `#[codex-deepseek:disabled]` 标签的行还原，重启桌面端即可。
注意 `model_catalog_json` 和 `web_search` 属于 DeepSeek 那一组，切回时也要一起去掉（目录里只有 deepseek 模型，留着会让 gpt 模型没有元数据）。
如果你装了 `--repoint-provider OpenAI`，gpt 请求同样会经过适配器，适配器识别到 gpt-* 会原样透传（用 `--openai-key` 配的凭据）。

## 九、卸载

双击 `一键卸载.command`（会先让确认一次），或者命令行：

```bash
./uninstall.sh                  # 停服务 + 恢复最近的 config.toml 备份 + 删适配器
./uninstall.sh --keep-config    # 只停服务删适配器，不动 config.toml
./uninstall.sh --purge          # 连 models.json 一起删
```

## 十、文件清单

```
codex-deepseek-setup/
├── 一键安装.command           # 双击安装（引导问答，给不想敲命令的人）
├── 一键卸载.command           # 双击卸载（问一次确认）
├── install.sh                 # 安装（幂等；不带参数 = 同一套引导问答）
├── uninstall.sh               # 卸载 / 回滚
├── README.md                  # 本文
├── make-release.sh            # 只在本仓库：跑一下生成 dist/*.tgz + *.zip
├── package.json               # npm 通道：bin / engines / files 白名单
├── bin/cli.mjs                # npm 通道：npx 子命令薄壳（见第十二节）
├── .gitignore                 # 只在本仓库：忽略 dist/、*.tgz、node_modules/
└── files/
    ├── adapter.py             # 本地适配器（透传 + 落盘 + /__ui 实时网页）
    ├── captures.py            # 命令行日志查看器（表格 / --show / --grep / --errors）
    ├── keys.json 生成逻辑     # 在 install.sh 里，权限 600
    ├── settings.json 生成逻辑 # capture / web UI 配置，权限 600
    ├── models.json            # 模型目录（slug 会按 --model 改写）
    └── setup_config.py        # config.toml / 目录的文本级改写（保留注释与顺序）
```

### 打个包发给别人

```bash
./make-release.sh                # -> dist/codex-deepseek-setup.tgz + .zip
./make-release.sh --tgz-only     # 只要 tgz
```

只打上面那几个文件（`make-release.sh`、`dist/`、`.gitignore` 不进包）。脚本会做几件事：

- 扫一遍待打包内容，**发现像 key 的字符串就拒绝出包**（`keys.json` / `settings.json` 是安装时才生成的，永远不该进包）；
- 解包后重跑 `bash -n` + `py_compile` + 检查执行位，确认包是完整可跑的；
- zip 用 python3 生成，保证中文文件名带 UTF-8 标志（macOS 自带的 Info-ZIP 3.0 不带，Windows 解出来会乱码）；
- 打印 sha256 和文件清单。

注意它打的是**双击那条通道**（含 `一键*.command`），所以包里没有 `package.json` /
`bin/`；npm 通道走 `npm publish`，但发布前 `make-release.sh` 会顺手用
`npm pack --dry-run` 检查 `package.json` 的 `files` 白名单是否把运行时文件带全了。

对方拿到后：`tar xzf codex-deepseek-setup.tgz && cd codex-deepseek-setup && open 一键安装.command`（Windows/微信/浏览器下载会加 quarantine，见第零节）。

适配器可用的环境变量（一般不用动）：`CODEX_ADAPTER_PORT`、`CODEX_ADAPTER_UPSTREAM`、`CODEX_ADAPTER_MIN_MAX_OUTPUT_TOKENS`（默认 32768）、`CODEX_ADAPTER_TIMEOUT`（默认 900s）、`CODEX_ADAPTER_KEYS`、`CODEX_ADAPTER_LOG`、`CODEX_ADAPTER_SETTINGS`，以及上面那组 `CODEX_ADAPTER_CAPTURE*`。

## 十一、已知限制
- `none` / `minimal` / `ultra` 档网关不支持，目录里已排除；正文里 Codex 仍接受 `-c model_reasoning_effort='"low"'` 这类覆盖。
- 目录只有两个 deepseek 条目，因此模型选择器里只有它们；要加别的模型，改 `--model-alt` 或自己编辑 `~/.codex/models.json`。
- 适配器是**本机 127.0.0.1** 服务，不对外暴露；key 只存在 `~/.codex/deepseek-adapter/keys.json`（600）和 `config.toml`（600）里。
- Claude Code（原生 Anthropic 协议、自己传 `max_tokens`）不受影响，不用这个适配器。

## 十二、用 npx 装（有 Node 的同事）

同一个东西也做成了 npm 包，适合已经有 Node 的人——不解压、不管路径：

```bash
npx codex-deepseek-setup            # 装：问一个 key，其余回车
npx codex-deepseek-setup status     # 目录 / 服务 / 进程 / 健康 / 端口 / key（打码）
npx codex-deepseek-setup uninstall  # 停服务 + 还原 config.toml + 删适配器
npx codex-deepseek-setup ui         # 打开实时请求·回复网页
npx codex-deepseek-setup logs -n 50 # 浏览抓取到的请求
```

- `del` / `rm` / `remove` 都是 `uninstall` 的别名；加 `-y` / `--yes` 跳过确认。
- `install` / `uninstall` 认的其它参数**原样转给底层脚本**，例如
  `npx codex-deepseek-setup install --port 9000 --model deepseek-v4-pro --repoint-provider OpenAI`；
  `npx codex-deepseek-setup install --help` 看全量参数。
- **不会重复问 key**：检测到已装时默认沿用 `keys.json` 里的 key 重装/修复（回车即可），
  并保留你之前 repoint 过的 provider。
- 名字我查过了，`codex-deepseek-setup` 和 `codex-deepseek` 都没被占用（两个名字都能用）。发布：

```bash
npm login && npm publish                      # 公网 registry
# 或先在本地验证（注意：npx 不认 tarball 路径，会把路径当命令执行，必须用 npm exec）
npm pack
npm exec --yes --package=./codex-deepseek-setup-1.0.0.tgz -- codex-deepseek-setup status
```

实现上是**薄壳**：`bin/cli.mjs` 只负责子命令分发、状态探查、已装检测，真正干活的仍然是
`install.sh` / `uninstall.sh` / `files/*.py`（那部分已经对着 launchd、systemd 和网关验过）。
两个和 npx 有关的点：

- **npx 缓存被清掉不影响已装好的服务**：安装时就把适配器拷到 `~/.codex/deepseek-adapter/`，
  launchd/systemd 只运行那份拷贝，npx 只是“把文件送过去”的通道。
- **为什么没有改成全 Node**：现在 plist 里写的是 `/usr/bin/python3`（macOS 自带、路径稳定）。
  换成 Node 就得写 `process.execPath`，而 nvm 装出来的 Node 路径带版本号
  （`~/.nvm/versions/node/vXX/bin/node`），升级 Node 就失效，而 `/usr/bin/node` 这类
  稳定路径在 macOS 上并不存在。另外 `files/adapter.py` 2030 行里含 SSE 透传、落盘和整个
  `/__ui` 页面，重写风险远大于收益。
