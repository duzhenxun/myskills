# dws-xiaozhi-mcp

把你电脑上的 **dws（钉钉工作台 CLI）** 能力接入 **小智 AI**（xiaozhi.me）的 MCP 接入点，
让你可以直接用语音让小智帮你查日程、查待办、找人、搜公司知识、发钉钉消息、建日程……

同时也支持任何标准 MCP 客户端（Claude Desktop / Cursor / Cherry Studio / Pi 等）通过 stdio 调用。

---

## 1. 工作原理

官方文档：<https://my.feishu.cn/wiki/HiPEwZ37XiitnwktX13cEM5KnSb>（小智AI配置MCP接入点使用说明）
官方示例：<https://github.com/78/mcp-calculator>

```
 小智设备/App  <->  小智云  <->  wss://api.xiaozhi.me/mcp/?token=...
                                      ^
                                      |  pipe.py 作为 WebSocket 客户端主动连上去
                                      v
                                 pipe.py  <-- stdio JSON-RPC -->  server.py  <-->  dws CLI
```

- `server.py`：一个 stdio MCP Server，把 dws 的常用能力包装成 15 个工具（工具名 ASCII、描述中文）。
- `pipe.py`：WebSocket ↔ stdio 的桥，自动重连（指数退避），断线后自动重启本地 server。
- `dws` 本身负责钉钉的登录态、权限和组织上下文。

---

## 2. 前置条件

| 依赖 | 说明 |
| --- | --- |
| macOS / Linux | 本机运行 |
| `dws` CLI | 已安装且已完成登录：`dws doctor` 应显示「已登录」 |
| `uv` | 用于管理 Python 3.12 虚拟环境（`brew install uv` 或 `curl -LsSf https://astral.sh/uv/install.sh \| sh`） |
| 小智 MCP 接入点 | 在 [xiaozhi.me 控制台](https://xiaozhi.me) → 智能体 → 配置角色页面右下角获取 `wss://...?token=...` |

先确认 dws 正常：

```bash
dws doctor
dws contact user get-self -f json | head
```

---

## 3. 快速开始

```bash
cd /Users/dds/data/ai/work/dws-xiaozhi-mcp

# 1) 写入 MCP 接入点地址
cp .env.example .env        # 已经帮你写好 .env 的话跳过
vim .env                    # 把 MCP_ENDPOINT 换成你自己的

# 2) 本地自测（不经过小智，确认 dws 工具链可用）
uv run --python 3.12 test_tools.py

# 3) 前台启动（看到 "已连接 MCP 接入点" 即成功）
./run.sh
```

启动后回到 xiaozhi.me 控制台，**MCP 接入点状态** 会变成「在线」，
然后对设备说：「我今天有什么日程？」即可。

后台常驻：

```bash
./start.sh     # nohup 后台启动，日志 .dws-mcp.log
./status.sh    # 查看状态与最近日志
./stop.sh      # 停止
```

开机自启（macOS launchd）：见 `com.local.dws-xiaozhi-mcp.plist.example` 里的注释。

---

## 4. 工具清单

### 只读类

| 工具 | 作用 | 典型说法 |
| --- | --- | --- |
| `query_schedule` | 查今天/明天/本周/下一个日程 | 「我今天有什么安排」 |
| `list_todos` | 查待办（可只看今天到期） | 「我有什么待办」 |
| `list_unread_chats` | 列出有未读的会话 | 「我有没有新消息」 |
| `search_messages` | 按关键词/群/发送人/`@我` 搜消息 | 「项目群里关于发布的讨论」 |
| `list_my_groups` | 列出我加入的群 | 「我有哪些群」 |
| `search_person` | 通讯录找人（部门/职位/上级…） | 「张三在哪个部门」 |
| `search_knowledge` | 搜企业内部知识（文档/IM/纪要/邮件…） | 「上次评审会的结论是什么」 |
| `get_my_profile` | 我的资料 | 「我是谁」 |

### 写入类（会自动加 `--yes`）

| 工具 | 作用 |
| --- | --- |
| `send_message` | 给某人 / 某个群发钉钉消息 |
| `send_ding` | 发 DING（app / sms / call） |
| `create_todo` | 建待办（可指派给他人） |
| `complete_todo` | 按标题关键词完成待办 |
| `create_event` | 建日程 / 约会议（可邀请参会人） |

### 通用类

| 工具 | 作用 |
| --- | --- |
| `dws_help` | 查任何 dws 命令的帮助 |
| `dws_run` | 兜底执行任意 dws 命令（默认只允许只读，写操作需 `allow_write=true`） |

工具总量控制在 15 个，因为小智会把工具描述整段喂给模型，太多工具反而会降低选中率。

---

## 5. 安全设计

- **不经过 shell**：所有命令用 `argv` 数组 + `create_subprocess_exec` 执行，没有命令注入面。
- **兜底工具分级**：`dws_run` 会先调 `dws schema` 查该命令的 `effect`：
  - `read` → 直接执行；
  - `write` / `destructive` → 必须显式 `allow_write=true`（模型需先向你复述并得到确认）；
  - 查不到 → **fail-closed**，默认拒绝。
- **硬黑名单**：`dws auth` / `upgrade` / `config` / `plugin` / `profile` 等本地自管理命令一律禁止。
- **超时保护**：单次 dws 调用默认 9 秒（`DWS_TOOL_TIMEOUT`），超时直接 kill，避免小智侧 10 秒超时报错。
- **输出截断**：返回给模型的文本默认最多 6000 字符（`DWS_MAX_CHARS`）。

---

## 6. 配置项（.env）

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `MCP_ENDPOINT` | 必填 | 小智 MCP 接入点地址 |
| `DWS_TOOL_TIMEOUT` | `9` | 单次 dws 调用总超时（秒），建议 ≤ 9 |
| `DWS_HTTP_TIMEOUT` | `8` | 传给 `dws --timeout` 的 HTTP 超时 |
| `DWS_MAX_CHARS` | `6000` | 返回给模型的最大字符数 |
| `DWS_PROFILE` | 空 | 多组织时指定 `corpId:userId`（见 `dws profile list`） |
| `DWS_BIN` | 自动探测 | dws 可执行文件路径 |
| `DWS_MCP_CMD` | 当前 Python 跑 `server.py` | 覆盖本地 MCP server 启动命令 |

---

## 7. 在小智里怎么用效果更好

MCP 工具是否被调用，很大程度取决于智能体的**角色提示词**。建议在智能体的角色设定里加一段：

```
你可以调用本机钉钉(dws)工具来查资料、查日程待办、发消息。
- 涉及“我的日程/待办/未读消息”时，直接调用对应工具，不要凭空回答。
- 需要发消息、建待办、建日程等写操作前，先复述一遍内容让用户确认，再执行。
- 搜索结果如果太长，请只总结要点，不要逐条念 JSON。
```

另外注意：接入点的 token 会随智能体配置刷新而更换（社区反馈「地址会变」），
如果突然不在线，去控制台重新复制一次地址更新 `.env` 即可。

---

## 8. 常见问题

**Q: 小智显示「MCP 接入点状态：未连接」**
1. `./status.sh` 看日志，确认出现「已连接 MCP 接入点」；
2. 确认 `.env` 里的 token 是最新复制的；
3. 确认电脑没有休眠断网；`pipe.py` 会自动重连，但电脑关机/休眠时无法保持在线。

**Q: 提示 `Tool call was aborted due to timeout (10000ms)`**
小智服务端对工具调用有约 10 秒超时。本项目已默认 9 秒 + 输出截断；
如果个别查询确实慢，可以让用户把问题问得更具体（例如指定群名/时间范围）。

**Q: dws 登录过期**
重新 `dws auth login` 即可，`pipe.py` 不用重启。

**Q: 想把 MCP 也给 Claude / Cursor 用**
在对应客户端的 MCP 配置里加 stdio server：

```json
{
  "mcpServers": {
    "dws": {
      "command": "uv",
      "args": ["run", "--python", "3.12", "/Users/dds/data/ai/work/dws-xiaozhi-mcp/server.py"]
    }
  }
}
```

---

## 9. 目录结构

```
dws-xiaozhi-mcp/
├── server.py                              # stdio MCP server（15 个工具）
├── pipe.py                                # 小智 MCP 接入点 <-> 本地 server 桥
├── test_tools.py                          # 本地自测
├── run.sh / start.sh / stop.sh / status.sh
├── com.local.dws-xiaozhi-mcp.plist.example # macOS 开机自启示例
├── pyproject.toml
├── .env / .env.example
└── README.md
```
