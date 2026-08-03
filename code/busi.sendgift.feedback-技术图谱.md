# busi.sendgift.feedback 技术图谱

## 一图技术图谱
```mermaid
flowchart LR
  naa1df2ef["Daenerys 框架"]
  n8f718eeb["GORM"]
  na05476e7["GitLab CI"]
  n7c735559["HTTP/外部接口"]
  n51be25b0["Kafka"]
  n62a004b9["MySQL"]
  n8aa21d2e["RPC/IDL 调用"]
  ne1114467["Redis"]
  n4e96cf40["Thrift/RPC"]
  nba4a09a6["busi.sendgift.feedback"]
  nbfa5311d["git.inke.cn/BackendPlatform/go-tools/cast"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  na283f7b0["git.inke.cn/BackendPlatform/golang/redis"]
  n14b7f193["git.inke.cn/BackendPlatform/golang/safego"]
  ne2260199["git.inke.cn/BackendPlatform/golang/trace"]
  nd4cd24ab["git.inke.cn/bpc/server/busi/busi.sendgift.feedback"]
  n7de617ec["git.inke.cn/bpc/server/sdk/commlib"]
  n961ac33a["git.inke.cn/inkelogic/rpc-go"]
  ne7b37ee1["golangci-lint"]
  nbd2d8634["src/backend/create_giftlog_tables.go"]
  nd440d6c6["src/backend/init.go"]
  n8a40d1f6["src/backend/update_bonus_trigger_conf.go"]
  n443cd9b7["src/backend/update_broadcast_trigger_conf.go"]
  n84d1e9fa["src/backend/update_group_effect_conf.go"]
  nfbfd2bab["src/client/client_utils.go"]
  n628ae18d["src/common/config.go"]
  nfa83182f["src/common/consts.go"]
  n3fcbc0ad["src/common/http.go"]
  nb4d1e1bf["src/dao/local_cache.go"]
  ne2faa0bd["src/handler/init.go"]
  n6933a139["src/model/http.go"]
  nf1e71428["src/model/kafka.go"]
  nac53d256["src/model/mysql.go"]
  nc22f0bbe["src/model/redis.go"]
  n7f5851c2["src/model/redis_proxy.go"]
  n8d81b440["任务/定时处理"]
  n7cc1b88f["公司内部包"]
  nb682654e["外部依赖"]
  nadeed157["工程质量"]
  n8de19b79["接入层 HTTP/API"]
  n9bfbba5f["数据访问层"]
  ne9fe3e59["模型/DTO"]
  nfc56e941["领域: 礼物/打赏"]
  n8aa21d2e --> nd440d6c6
  n8aa21d2e --> nfbfd2bab
  n8aa21d2e --> n628ae18d
  n8aa21d2e --> nfa83182f
  n8aa21d2e --> n3fcbc0ad
  nba4a09a6 -- "uses" --> n8aa21d2e
  nba4a09a6 -- "schedules" --> n8d81b440
  nba4a09a6 -- "imports" --> n7cc1b88f
  nba4a09a6 -- "depends" --> nb682654e
  nba4a09a6 -- "quality" --> nadeed157
  nba4a09a6 -- "exposes" --> n8de19b79
  nba4a09a6 -- "persists" --> n9bfbba5f
  nba4a09a6 -- "defines" --> ne9fe3e59
  nba4a09a6 -- "domain" --> nfc56e941
  n8d81b440 --> nbd2d8634
  n8d81b440 --> nd440d6c6
  n8d81b440 --> n8a40d1f6
  n8d81b440 --> n443cd9b7
  n8d81b440 --> n84d1e9fa
  n7cc1b88f --> nbfa5311d
  n7cc1b88f --> n7d7ea8b2
  n7cc1b88f --> na283f7b0
  n7cc1b88f --> n14b7f193
  n7cc1b88f --> ne2260199
  n7cc1b88f --> nd4cd24ab
  n7cc1b88f --> n7de617ec
  n7cc1b88f --> n961ac33a
  nb682654e --> naa1df2ef
  nb682654e --> n8f718eeb
  nb682654e --> n7c735559
  nb682654e --> n51be25b0
  nb682654e --> n62a004b9
  nb682654e --> ne1114467
  nb682654e --> n4e96cf40
  nadeed157 --> na05476e7
  nadeed157 --> ne7b37ee1
  n8de19b79 --> ne2faa0bd
  n9bfbba5f --> nb4d1e1bf
  ne9fe3e59 --> n6933a139
  ne9fe3e59 --> nf1e71428
  ne9fe3e59 --> nac53d256
  ne9fe3e59 --> nc22f0bbe
  ne9fe3e59 --> n7f5851c2
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/bpc/server/busi/busi.sendgift.feedback`
- 领域判断：礼物/打赏
- README 摘要：无标题

```text
未发现 README 或 README 内容为空
```

## 静态结构画像
- 文本/代码文件数：66
- Go 文件数：54
- 文件类型分布：.go(54), .toml(5), .json(4), .yml(2), .proto(1)
- 顶层目录分布：src(56), conf(6), etc(2)

## 关键目录
- `src`: 56 个文本/代码文件
- `conf`: 6 个文本/代码文件
- `etc`: 2 个文本/代码文件

## 代码分层
- 接入层文件：1 个
- 服务层文件：0 个
- 数据访问文件：1 个
- 模型文件：7 个
- 任务/定时相关文件：8 个
- RPC/IDL 相关文件：20 个

## API/路由线索
- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认

## 核心类型与方法线索
- 导出结构体：TestController, TestRequest, GiftLog, Event_super_gun_v2_slots_info, Bdsuper_gun_v2_slots, PushRequest, PushResponse, PushRequest, PushResponse, GiftInfo, Atom, CacheBillboardAgoInfo, Content, CardContent, SendMessageIn, SendMessageOut, MysteryIn, MysteryOut, BaseRes, GuardStarOut, Whitelist, GuardScoreFeedbackMgr, GuardRelation, GuardStar, FeedbackMgr, Config, AppConf, WhiteListControlConf, GiftTriggerBonusConf, GiftTriggerBroadcastConf
- 导出函数/方法：Serve, InitServer, SuperGunMaxSlotsEvent, Module, AppType, DataKey, DataKeyWithParam, Product, MetricServerEID, LoggingServerEID, Init, SetJSON, SetByte, GetJSON, FlowKeyDataDeal, InitBackend, Close, Enum, String, UnmarshalJSON, EnumDescriptor, Enum, String, UnmarshalJSON, EnumDescriptor, Enum, String, UnmarshalJSON, EnumDescriptor, Reset

## 外部依赖线索
- HTTP/外部接口: 26 处信号
- Kafka: 22 处信号
- Redis: 20 处信号
- Thrift/RPC: 8 处信号
- MySQL: 5 处信号
- Daenerys 框架: 4 处信号
- GORM: 2 处信号

## 内部依赖线索
- `git.inke.cn/bpc/server/busi/busi.sendgift.feedback`: 66
- `git.inke.cn/BackendPlatform/golang/logging`: 32
- `git.inke.cn/inkelogic/rpc-go`: 10
- `git.inke.cn/BackendPlatform/golang/trace`: 9
- `git.inke.cn/bpc/server/sdk/commlib`: 4
- `git.inke.cn/BackendPlatform/golang/safego`: 3
- `git.inke.cn/BackendPlatform/go-tools/cast`: 3
- `git.inke.cn/BackendPlatform/golang/redis`: 3
- `git.inke.cn/bpc/server/sdk/shanyin.server.serviceinfo`: 2
- `git.inke.cn/bpc/server/sdk/busi.gift.billboard_base`: 2
- `git.inke.cn/inkelogic/rpc-go/desc`: 2
- `git.inke.cn/tpc/inf/go-tls`: 2

## 第三方 import 概览
- golang.org(17), github.com(16), bytes(8), git.apache.org(5), runtime(3), go.uber.org(3), io(3), os(2), crypto(2), reflect(2)

## IDL/协议文件
- `src/link_msg/push.proto`

## 工程质量与交付
- GitLab CI：有
- golangci-lint：有
- 测试文件：
- 未发现 `_test.go`

## 阅读建议
- 先读 README 和 `server/http`、`handler`、`service` 目录，确认入口 API 与核心业务流程。
- 再沿服务层方法进入 DAO/Repo/Model，确认数据表、缓存 Key、RPC 调用和异步任务。
- 若图中只出现少量节点，通常表示该项目是配置型/胶水型服务，需结合上层共享工程和部署配置继续确认。
