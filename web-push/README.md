# Web Push 注册演示（端口 25259）

单页面的 Web Push 演示服务：页面既能**注册订阅**（导出 subscription 对象），也能**选择设备推送消息**。

## 启动

```bash
cd web-push
npm install               # 只需装 web-push（服务端发推送用）
npm start                 # node server.js
# 打开 http://localhost:25259
```

```bash
PORT=25259 npm start      # 自定义端口
HTTPS=1 npm start         # 启用 HTTPS（需先生成证书，见下）
```

## 手机上测试（必须 HTTPS）

浏览器只在 `https` 或 `http://localhost` 下允许 Service Worker / Push。

```bash
npm run cert              # openssl 生成 certs/server.crt + server.key（自签，10 年）
HTTPS=1 npm start         # 启动后按提示用局域网地址访问，手机需先信任自签证书
```

## 页面功能

| 功能 | 说明 |
| --- | --- |
| 注册推送 | 注册 SW → 申请通知权限 → `pushManager.subscribe()` → 展示并自动复制 subscription，同时登记到服务端设备列表 |
| 复制 subscription JSON | 复制 `JSON.stringify(subscription.toJSON(), null, 2)` |
| 复制 JSON.stringify(subscription) | 复制单行字符串，适合塞进接口调试工具 |
| 取消订阅 | `subscription.unsubscribe()`，并同步删除服务端记录 |
| 本地通知测试 | `registration.showNotification()`，验证通知通道 |
| VAPID 公钥 | 默认内置已生成的公钥，可在输入框替换（保存在 localStorage） |
| **推送消息** | 设备列表勾选目标（支持全选 / 全不选 / 仅推它）→ 选内容模板 → 编辑标题内容 → 发送；也可一键「推送给所有设备」 |

页面分为 **3 个 Tab**（点击切换，状态存 localStorage，也支持 `#push` / `#help` 直达）：

| Tab | 内容 |
| --- | --- |
| ① 注册订阅 | 环境状态（浏览器支持 / 通知权限 / SW / 订阅）、注册推送、本地通知测试、subscription 对象与复制按钮 |
| ② 推送测试 | 目标设备列表 + 内容模板 + 标题内容编辑 + 发送结果 + 最近收到的推送（Tab 上带设备数角标） |
| 说明 | 使用步骤与注意事项 |

注册成功后 toast 会提示切到「② 推送测试」；键盘 `←/→/Home/End` 也可切换 Tab。UI 会实时显示浏览器支持、通知权限、Service Worker 状态、订阅状态，非安全上下文会有醒目提示。

## 推送面板

- **目标设备列表**：显示设备名（如 `macOS · Chrome`、`iOS · Safari PWA`）、短 id、endpoint 摘要、注册时间、上次推送结果；可重命名（PATCH）、单条删除（DELETE）、清空全部记录。
- **内容模板**：内置 6 个可直接用的模板（系统升级、订单发货、新消息、限时优惠、安全提醒、Hello Push），选中后自动填充标题/内容/TTL，仍可手动修改；也可选「自定义…」自己写。
- **发送结果**：逐台返回 `✓ HTTP 201` 或 `✗ 错误原因`；命中 404/410（订阅已失效）的设备会自动从 `subscriptions.json` 清理。
- 浏览器侧权限被拒 / 不是 HTTPS 时都会给出明确提示。

## VAPID 密钥

```
Public Key : BPnvp8p4QdnOh4vO6-oAhxFGouHJTqY68C_4-goxBh1sphBEb1blz2FgqyEVg5JoFMBdSJKu2tDR-VLkdUNIHrQ
Private Key: UArGsIjinVV7Lk0g3zOdkMctvWIoTzUT8jV2vayiOyQ   (仅服务端使用，切勿下发到浏览器)
```

重新生成：`npx web-push generate-vapid-keys`

## 订阅与推送接口

```
GET    /api/subscriptions        设备列表（id / label / endpoint / savedAt / lastPushAt / lastResult）
PATCH  /api/subscriptions        { id, label }  重命名设备
DELETE /api/subscriptions        { id } 删单台 / { endpoint } 删指定 / { all: true } 清空全部

POST   /api/subscribe            body = subscription JSON（可带 label），按 endpoint 去重保存

POST   /api/push                 { targets: 'all' | [id...], title, body, url, ttl }
                                 返回 { sent, total, removed, results[] }

GET    /api/vapid-public-key     当前使用的公钥
GET    /api/health               服务状态、设备数、web-push 依赖是否可用
```

命令行等价用法（curl）：

```bash
# 推给所有设备
curl -X POST http://localhost:25259/api/push -H 'Content-Type: application/json' \
  -d '{"targets":"all","title":"标题","body":"内容","url":"/","ttl":3600}'

# 只推给某台设备（id 从 /api/subscriptions 里取）
curl -X POST http://localhost:25259/api/push -H 'Content-Type: application/json' \
  -d '{"targets":["ff6fa057"],"title":"只给这台","body":"hello"}'
```

也可以直接跑脚本（等价，逐个发送并清理失效订阅）：

```bash
npm run send -- "标题" "内容"
```

## 目录结构

```
web-push/
├── server.js               # 静态服务 + 订阅/推送 API（web-push 发送，失效订阅自动清理）
├── public/
│   ├── index.html          # 单页面 UI（Tab 1 注册订阅 / Tab 2 推送测试 / Tab 3 说明）
│   ├── app.js              # 订阅逻辑 + 设备列表 + 内容模板 + 发送逻辑
│   ├── sw.js               # Service Worker（push / notificationclick）
│   ├── manifest.webmanifest# PWA 清单（iOS 需添加到主屏幕）
│   └── icons/              # 图标（由 scripts/make-icons.js 生成）
├── docs/
│   └── web-push-api-analysis.md  # 全链路 API 分析文档
├── scripts/
│   ├── make-icons.js       # 纯 Node 生成 PNG 图标（换图标时才需要跑）
│   ├── send.js             # 命令行推送（与 POST /api/push 能力重叠，供不想起服务/批处理时用）
│   └── raw-request.js      # 手写 HTTP 推送演示（教学用，见 docs）
├── .gitignore              # 忽略 node_modules / server.log / subscriptions.json / certs
├── package-lock.json       # 依赖锁定
├── node_modules/           # 仅 web-push 及其依赖
└── subscriptions.json      # 设备订阅与推送结果，运行时生成（已被 gitignore）
```

## 常见问题

- **点注册没反应 / 报权限错误**：此前点过「阻止」，需在地址栏站点设置里把通知改回「允许」再刷新。
- **iOS 拿不到权限**：iOS 16.4+ 才行，且必须先把网页「添加到主屏幕」，从主屏幕图标（standalone）打开再注册。
- **换端口后没权限**：Push 权限按 origin 隔离，`localhost:25259` 与 `localhost:25258` 是两个独立 origin。
- **推送返回 404/410**：该设备的订阅已失效（卸载 PWA、清除数据等），服务端会自动清理，重新在该设备点「注册推送」即可。
- **推送成功但没弹通知**：检查系统「通知」里该浏览器是否被静音/专注模式；macOS 需允许 Chrome/Safari 发通知。
- **iOS 推送返回成功但无通知**：确认已从主屏幕图标打开 PWA（standalone），Safari 标签页里的推送不会显示。

## 文档

- [docs/web-push-api-analysis.md](docs/web-push-api-analysis.md) —— 全链路 API 分析：注册与推送分别调了哪些 API（含源码行号、真实请求头、推送服务响应码、架构时序图），以及 `npx web-push` CLI 的密钥生成与手动推送用法
- 前文「附录：推送到底打的是哪个 API」是简要版

## 附录：推送到底打的是哪个 API（速查）

**没有中心化的「推送 API」**：请求打的就是 `subscription.endpoint` 本身，主机名由浏览器厂商决定（Chrome/Edge → `fcm.googleapis.com`，Safari → `web.push.apple.com`，Firefox → `updates.push.services.mozilla.com`）。

```
POST <endpoint>
TTL: 3600
Content-Encoding: aes128gcm        # 有 payload 时才有
Authorization: vapid t=<ES256 JWT>, k=<VAPID 公钥>
body: RFC8291 密文 / 或空
```

- 有 payload 必须加密（密钥来自订阅的 `p256dh`/`auth`）→ 纯 curl 写不出来，用库。
- 无 payload 可纯 curl：`node scripts/raw-request.js --send`（实测 201）。

> 完整版（调用栈、源码行号、响应码语义、CLI 用法、常见报错）见
> **[docs/web-push-api-analysis.md](docs/web-push-api-analysis.md)**。

本文档不再重复该部分内容，避免两处不同步。
