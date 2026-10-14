# pi-xiaozhi-mcp

让小智 AI（xiaozhi.me）能够**直接用语音指挥你电脑上的 Pi coding agent**——
写代码、改文件、跑命令、抓网页、做多步骤自动化，全部在你本机执行。

配套项目：`../dws-xiaozhi-mcp`（钉钉 dws 能力）。
**两者可以同时挂在同一个 MCP 接入点上**，小智会把两边的工具合并成一个工具列表。

---

## 1. 为什么不是简单地跑 `pi -p "..."`

实测数据（同一台机器，同一模型）：

| 方式 | 一次简单问答耗时 |
| --- | --- |
| `pi -p "..."`（每次冷启动） | **12 ~ 22 秒** |
| 常驻 `pi --mode rpc` 热进程 | **1.7 ~ 3.8 秒** |

小智服务端对 tool call 有约 **10 秒超时**，所以冷启动方案基本必然超时。
本项目维持一个常驻的 `pi --mode rpc` 子进程，并且：

- **启动即预热**：MCP server 一起来就在后台把 Pi 进程拉起来，用户第一句话不用等冷启动；
- **超时任务异步化**：Pi 跑得久时先返回「处理中」，用户稍后问「好了吗」再取结果。

---

## 2. 架构

```
            小智设备/App
                 |
             小智云
                 |
   wss://api.xiaozhi.me/mcp/?token=...   ← 一个接入点可以挂多个 MCP server
        /                        \
 dws-xiaozhi-mcp/pipe.py     pi-xiaozhi-mcp/pipe.py
        |                          |
 dws_server（15 个工具）      pi_server（5 个工具）+ 常驻 pi --mode rpc
        |                          |
     dws CLI                本机代码 / 文件 / 命令
```

接入点的多服务器合并与按工具名路由由接入点服务负责（工具名不冲突即可）。

---

## 3. 快速开始

```bash
cd /Users/dds/data/ai/work/pi-xiaozhi-mcp

# 1) 配置（已帮你写好 .env，确认下面两项即可）
#    MCP_ENDPOINT   —— 和 dws 项目用同一个 token
#    PI_MCP_CWD     —— Pi 的工作目录
vim .env

# 2) 本地自测
uv run --python 3.12 test_pi.py          # 列工具 + 一个短问答
uv run --python 3.12 test_pi.py --long   # 演示「先返回、后查询」的异步任务

# 3) 前台启动
./run.sh

# 4) 后台常驻
./start.sh && ./status.sh
```

---

## 4. 工具清单

| 工具 | 作用 | 典型说法 |
| --- | --- | --- |
| `ask_pi` | 把任务交给 Pi 执行（最多等 8 秒，超时先返回进度） | 「让 Pi 帮我把这个脚本改成 Python3」 |
| `check_pi` | 查上一个任务的结果 | 「刚才那个任务好了吗」 |
| `cancel_pi` | 中断当前任务 | 「停，不用做了」 |
| `pi_status` | 看 Pi 进程/工作目录/模型/进度 | 「Pi 现在在干嘛」 |
| `reset_pi` | 重启 Pi、清空上下文 | 「忘掉之前的，重新开始」 |

---

## 5. 异步任务模式（关键）

Pi 干活经常要几十秒到几分钟，而小智 10 秒就超时。所以流程是这样：

```
用户：让小智帮我统计一下 ~/Downloads 有多少个文件
  → 小智调用 ask_pi(...)          → 8 秒内没跑完，返回「还在处理中」
  → 小智说：任务已经开始执行了，稍后你可以问我好了吗
用户：好了吗？
  → 小智调用 check_pi()           → 还在跑，返回进度「正在调用 bash」
  → 小智说：还在执行，正在跑命令
用户：好了吗？
  → 小智调用 check_pi()           → 已完成，返回结果
  → 小智把结果念给你听
```

**一定要在智能体的角色提示词里写清楚这个约定**，否则小模型会在超时后自己瞎编答案。建议追加：

```
你可以调用本机 Pi 编程智能体（ask_pi / check_pi / cancel_pi）来操作这台电脑：
读写文件、运行命令、写代码、抓网页、多步骤自动化。

规则：
1. 需要操作电脑、写代码、跑命令、查本地文件时，调用 ask_pi 把任务交给 Pi。
2. Pi 任务常常要几十秒。如果 ask_pi 返回「还在处理中」，你必须如实告诉用户
   任务已经开始、稍后可以问「好了吗」，绝对不要假装任务已经完成或编造结果。
3. 用户问「好了吗 / 有结果了吗」时，调用 check_pi 取结果，并只念关键结论。
4. 用户说「停 / 取消」时调用 cancel_pi。
5. 结果里如果有大段代码或路径列表，只总结要点，不要逐字念出来。
```

---

## 6. 配置项（.env）

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `MCP_ENDPOINT` | 必填 | 小智 MCP 接入点地址 |
| `PI_MCP_CWD` | 启动目录 | Pi 的工作目录（决定它能读写哪个目录） |
| `PI_MCP_PROVIDER` | `nexita-anthropic` | 模型 provider |
| `PI_MCP_MODEL` | `deepseek-v4.1-flash` | 模型 |
| `PI_MCP_WAIT` | `8` | ask_pi 最多等待秒数（硬上限 9） |
| `PI_MCP_MAX_CHARS` | `4000` | 返回给大模型的最大字符数 |
| `PI_MCP_APPROVE` | 关 | `1` = 给 pi 传 `--approve`（信任项目内 AGENTS.md/技能） |
| `PI_MCP_EXTRA_ARGS` | 空 | 追加给 pi 的参数，如 `--no-extensions --no-skills` |
| `PI_BIN` | 自动探测 | pi 可执行文件路径 |

> ⚠️ **模型坑**：本机 pi 设置里的默认 provider `aigw-xs25` 目前会报
> `unknown variant 'developer'` 而完全不可用。所以这里默认显式指定
> `nexita-anthropic/deepseek-v4.1-flash`。
> 用 `pi --list-models` 挑一个可用的；换模型后重启本服务即可。

---

## 7. 安全说明

- Pi 拥有你本机的完整读写和执行权限。**只把这个接入点用在你自己的智能体上**。
- `PI_MCP_CWD` 决定 Pi 的工作目录，建议设成专门的目录，而不是 `$HOME`。
- 默认**不传** `--approve`，即不信任项目内的 `AGENTS.md` / 本地技能（更安全，但 Pi 能用的上下文少一些）；
  确认可信后再设 `PI_MCP_APPROVE=1`。
- 写操作（改文件、跑命令）不会被二次确认——这是设计取舍：语音场景做确认太啰嗦。
  如果需要「先复述再执行」，把它写进角色提示词，由小智在调 `ask_pi` 前来问你。

---

## 8. 常见问题

**Q: `pi_status` 显示「未启动」**
第一次调用 `ask_pi` 会自动拉起进程；预热完成后就会变成 `idle`。

**Q: ask_pi 总是返回「还在处理中」，从来没直接给过结果**
说明任务普遍超过 8 秒，属于正常现象。可以让用户把问题拆小、更具体，
或把 `PI_MCP_WAIT` 调到 9（再大就会撞上小智的超时）。

**Q: 报 `unknown variant 'developer'`**
当前 provider 不可用（见上文模型坑），换 `PI_MCP_PROVIDER` / `PI_MCP_MODEL` 后重启。

**Q: 重启 pipe 后 Pi 的上下文没了**
Pi 进程是 MCP server 的子进程，随连接重建。用 `--no-session` 是为了避免语音场景把
超长会话一直续下去。需要跨重启保留上下文可以改用 `--session-id`（自行改 `PI_EXTRA_ARGS`）。

**Q: 想再加第三个能力（浏览器自动化 / 智能家居 / …）**
照着这个项目复制一份，写个 MCP server，用**同一个 token** 再起一个 `pipe.py` 就行，
接入点会自动合并工具列表。注意工具名不要和已有的重名。

---

## 9. 目录结构

```
pi-xiaozhi-mcp/
├── pi_server.py      # MCP server（5 个工具 + 常驻 pi --mode rpc 管理）
├── pipe.py           # 小智 MCP 接入点 <-> 本地 server 桥
├── test_pi.py        # 本地自测
├── run.sh / start.sh / stop.sh / status.sh
├── pyproject.toml
├── .env / .env.example
└── README.md
```
