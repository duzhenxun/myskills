# busi.privilege.live_broadcast 技术图谱

## 一图技术图谱
```mermaid
flowchart LR
  n8f718eeb["GORM"]
  na05476e7["GitLab CI"]
  n7c735559["HTTP/外部接口"]
  n62a004b9["MySQL"]
  n8aa21d2e["RPC/IDL 调用"]
  ne1114467["Redis"]
  n07f743a7["busi.privilege.live_broadcast"]
  nef17c1c6["git.inke.cn/BackendPlatform/go-tools/cron"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  ne2260199["git.inke.cn/BackendPlatform/golang/trace"]
  n601c9c45["git.inke.cn/bpc/server/busi/busi.privilege.live_broadcast"]
  n780a94b0["git.inke.cn/bpc/server/sdk/commconst"]
  nba1d1b77["git.inke.cn/bpc/server/sdk/room.live.base"]
  n58d5ea77["git.inke.cn/bpc/server/sdk/shanyin.server.serviceinfo"]
  n961ac33a["git.inke.cn/inkelogic/rpc-go"]
  ne7b37ee1["golangci-lint"]
  ne2faa0bd["src/handler/init.go"]
  na9b33d5b["src/handler/send_broadcasting_handler.go"]
  n79ee049c["src/main.go"]
  n74b59756["src/manager/cache_manager.go"]
  n3a4c9e3c["src/util/client.go"]
  n8d81b440["任务/定时处理"]
  n7cc1b88f["公司内部包"]
  nb682654e["外部依赖"]
  nadeed157["工程质量"]
  n8de19b79["接入层 HTTP/API"]
  n5daeef3f["测试文件 1 个"]
  nfb754e86["领域: 权益/特权"]
  n8aa21d2e --> ne2faa0bd
  n8aa21d2e --> n79ee049c
  n8aa21d2e --> n3a4c9e3c
  n07f743a7 -- "uses" --> n8aa21d2e
  n07f743a7 -- "schedules" --> n8d81b440
  n07f743a7 -- "imports" --> n7cc1b88f
  n07f743a7 -- "depends" --> nb682654e
  n07f743a7 -- "quality" --> nadeed157
  n07f743a7 -- "exposes" --> n8de19b79
  n07f743a7 -- "domain" --> nfb754e86
  n8d81b440 --> na9b33d5b
  n8d81b440 --> n79ee049c
  n8d81b440 --> n74b59756
  n7cc1b88f --> nef17c1c6
  n7cc1b88f --> n7d7ea8b2
  n7cc1b88f --> ne2260199
  n7cc1b88f --> n601c9c45
  n7cc1b88f --> n780a94b0
  n7cc1b88f --> nba1d1b77
  n7cc1b88f --> n58d5ea77
  n7cc1b88f --> n961ac33a
  nb682654e --> n8f718eeb
  nb682654e --> n7c735559
  nb682654e --> n62a004b9
  nb682654e --> ne1114467
  nadeed157 --> na05476e7
  nadeed157 --> ne7b37ee1
  nadeed157 --> n5daeef3f
  n8de19b79 --> ne2faa0bd
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/bpc/server/busi/busi.privilege.live_broadcast`
- 领域判断：权益/特权
- README 摘要：服务化改造

```text
服务化改造
```

## 静态结构画像
- 文本/代码文件数：22
- Go 文件数：15
- 文件类型分布：.go(15), .toml(3), .yml(2), .md(1), .json(1)
- 顶层目录分布：src(16), etc(3)

## 关键目录
- `src`: 16 个文本/代码文件
- `etc`: 3 个文本/代码文件

## 代码分层
- 接入层文件：1 个
- 服务层文件：0 个
- 数据访问文件：0 个
- 模型文件：0 个
- 任务/定时相关文件：3 个
- RPC/IDL 相关文件：3 个

## API/路由线索
- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认

## 核心类型与方法线索
- 导出结构体：SendBroadCastring, VrSendBroadCastring, BaseHandler, Ret, Config, OPTTemplateConf, TemplateInfo, CommonMsgPush, EffectMsg
- 导出函数/方法：TestHandlerNewSendBroadCasting, NewSendBroadCasting, PreProcess, Process, PostProcess, VrNewSendBroadCasting, PreProcess, Process, PostProcess, Serve, Adapt, Serve, InitServer, InitConfig, DoHttpGet, DoHttpPost, NewRet, UpdateRet, Set, Get, GetCtxLogger, SetCtxLogger, ReadRequestBoday, GetTemplateRdsKey, BuildDefaultTemplate, GetliveInfos, BatchGetUserPublish, ChunkGetUserPublish, SplitArray, GetUserInfos

## 外部依赖线索
- HTTP/外部接口: 8 处信号
- GORM: 2 处信号
- Redis: 1 处信号
- MySQL: 1 处信号

## 内部依赖线索
- `git.inke.cn/bpc/server/busi/busi.privilege.live_broadcast`: 16
- `git.inke.cn/BackendPlatform/golang/logging`: 8
- `git.inke.cn/inkelogic/rpc-go`: 3
- `git.inke.cn/bpc/server/sdk/shanyin.server.serviceinfo`: 2
- `git.inke.cn/bpc/server/sdk/room.live.base`: 2
- `git.inke.cn/bpc/server/sdk/commconst`: 2
- `git.inke.cn/BackendPlatform/golang/trace`: 1
- `git.inke.cn/BackendPlatform/go-tools/cron`: 1
- `git.inke.cn/BackendPlatform/golang/sql`: 1
- `git.inke.cn/bpc/server/sdk/commlib`: 1

## 第三方 import 概览
- github.com(7), golang.org(6), busi.privilege.live_broadcast(5), io(2), flag(1), os(1), testing(1), runtime(1), bytes(1), crypto(1)

## IDL/协议文件
- 未发现 proto/thrift 文件

## 工程质量与交付
- GitLab CI：有
- golangci-lint：有
- 测试文件：
- `src/handler/send_broadcasting_handler_test.go`

## 阅读建议
- 先读 README 和 `server/http`、`handler`、`service` 目录，确认入口 API 与核心业务流程。
- 再沿服务层方法进入 DAO/Repo/Model，确认数据表、缓存 Key、RPC 调用和异步任务。
- 若图中只出现少量节点，通常表示该项目是配置型/胶水型服务，需结合上层共享工程和部署配置继续确认。
