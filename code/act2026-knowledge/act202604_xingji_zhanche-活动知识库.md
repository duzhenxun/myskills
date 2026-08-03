# act202604_xingji_zhanche 活动项目知识库

## 一图知识图谱
```mermaid
flowchart LR
  nbf5666a4["DrawBag"]
  n0316eaf3["DrawConf"]
  n263be4c2["DrawStyleConf"]
  nc00e2a7b["HTTP 接口"]
  n05ebd5bf["HTTP 接口/Handler"]
  nbe960d8a["KeyBroadcast: broadcast"]
  n183d456e["KeyMinIncome: min_income"]
  n236100b1["KeyUserLoss: user_loss:draw_type:%s"]
  n2ce84797["ModuleName: act202604_xingji_zhanche"]
  n82bfbb57["PrizeInfo"]
  n2102196f["Redis/状态 Key"]
  ne69ecd46["ReqBuyDrawBag"]
  n0874d5b2["ReqUserDraw"]
  n7ebf1f48["ResDrawPrize"]
  n2c47d69d["ResDrawPrizeLog"]
  nb3e96168["act202604"]
  nd8f0df53["act202604_xingji_zhanche"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n7643d9c0["git.inke.cn/opd/activitys/inke.activity.service/act"]
  n2eb4e126["git.inke.cn/opd/activitys/inke.activity.service/api/code"]
  n05487b5c["git.inke.cn/opd/activitys/inke.activity.service/dao"]
  n04a9e5ed["git.inke.cn/opd/activitys/inke.activity.service/model"]
  ncd038f67["git.inke.cn/opd/activitys/inke.activity.service/model/modelRoom"]
  na3bdde25["git.inke.cn/opd/activitys/inke.activity.service/utils"]
  n3460d96f["handler: drawBuyBag"]
  n49e9897f["handler: drawUserConf"]
  na404601c["handler: iBaseScore"]
  n4abc26ec["handler: iRecoverData"]
  nce80e685["handler: iSendPrize"]
  nf534b047["handler: iTestWeb"]
  n68cbe357["handler: index"]
  nc2d5a20f["handler: interfaceConf"]
  n9d4de674["service: allPrizePool"]
  n461e98ee["service: drawPrize"]
  n7cbd76cf["service: formatMsgContent"]
  n18e456b6["service: formatPrize"]
  nac136737["service: game2"]
  nad682fbc["service: getDrawConf"]
  ndfbe1a61["service: getMinIncome"]
  na455f0b2["service: sendPrize"]
  n099e1afb["业务能力信号"]
  n95b52d26["奖励发放/领奖"]
  n4a731954["排行榜"]
  n33557018["日志/埋点"]
  nde2f9a1b["模型/响应结构"]
  n50239d91["活动公共依赖"]
  nd99a3a80["活动基础信息"]
  n5c886211["活动服务逻辑"]
  ndbf77fd8["用户初始化/身份"]
  n5cbc9d99["类型: KA/SVIP 活动"]
  n1b9349a8["类型: 任务/活跃"]
  n2bdbab4b["类型: 榜单冲榜"]
  nda238ed0["类型: 游戏玩法"]
  n716e776e["缓存/Redis"]
  ndc861ff4["配置 JSON"]
  n05ebd5bf --> n3460d96f
  n05ebd5bf --> n49e9897f
  n05ebd5bf --> na404601c
  n05ebd5bf --> n4abc26ec
  n05ebd5bf --> nce80e685
  n05ebd5bf --> nf534b047
  n05ebd5bf --> n68cbe357
  n05ebd5bf --> nc2d5a20f
  n2102196f --> nbe960d8a
  n2102196f --> n183d456e
  n2102196f --> n236100b1
  nd8f0df53 -- "exposes" --> n05ebd5bf
  nd8f0df53 -- "module" --> n2ce84797
  nd8f0df53 -- "state" --> n2102196f
  nd8f0df53 -- "month" --> nb3e96168
  nd8f0df53 -- "uses" --> n099e1afb
  nd8f0df53 -- "defines" --> nde2f9a1b
  nd8f0df53 -- "imports" --> n50239d91
  nd8f0df53 -- "core" --> n5c886211
  nd8f0df53 -- "type" --> n5cbc9d99
  nd8f0df53 -- "type" --> n1b9349a8
  nd8f0df53 -- "type" --> n2bdbab4b
  nd8f0df53 -- "type" --> nda238ed0
  n099e1afb --> nc00e2a7b
  n099e1afb --> n95b52d26
  n099e1afb --> n4a731954
  n099e1afb --> n33557018
  n099e1afb --> nd99a3a80
  n099e1afb --> ndbf77fd8
  n099e1afb --> n716e776e
  n099e1afb --> ndc861ff4
  nde2f9a1b --> nbf5666a4
  nde2f9a1b --> n0316eaf3
  nde2f9a1b --> n263be4c2
  nde2f9a1b --> n82bfbb57
  nde2f9a1b --> ne69ecd46
  nde2f9a1b --> n0874d5b2
  nde2f9a1b --> n7ebf1f48
  nde2f9a1b --> n2c47d69d
  n50239d91 --> n7d7ea8b2
  n50239d91 --> n7bacf918
  n50239d91 --> n7643d9c0
  n50239d91 --> n2eb4e126
  n50239d91 --> n05487b5c
  n50239d91 --> n04a9e5ed
  n50239d91 --> ncd038f67
  n50239d91 --> na3bdde25
  n5c886211 --> n9d4de674
  n5c886211 --> n461e98ee
  n5c886211 --> n7cbd76cf
  n5c886211 --> n18e456b6
  n5c886211 --> nac136737
  n5c886211 --> nad682fbc
  n5c886211 --> ndfbe1a61
  n5c886211 --> na455f0b2
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/opd/activitys/inke.activity.service/act/2026/act202604/act202604_xingji_zhanche`
- 所属月份：`act202604`
- 活动类型判断：KA/SVIP 活动, 游戏玩法, 榜单冲榜, 任务/活跃
- ModuleName：`act202604_xingji_zhanche`
- README 摘要：无标题

```text
未发现 README 或 README 内容为空
```

## 静态结构画像
- 文本/代码文件数：6
- Go 文件数：6
- 文件类型分布：.go(6)

## 入口与接口
### 路由线索
- 未发现显式路由字符串，需结合活动总路由注册确认

### Handler 函数
- `index`
- `interfaceConf`
- `iTestWeb`
- `iRecoverData`
- `iSendPrize`
- `iBaseScore`
- `drawUserConf`
- `drawBuyBag`
- `drawPrize`
- `drawWebBroadcast`
- `drawPrizeLog`

## 核心业务逻辑
### service 方法
- `sendPrize`
- `formatMsgContent`
- `formatPrize`
- `getMinIncome`
- `getDrawConf`
- `drawPrize`
- `game2`
- `allPrizePool`

### 业务能力信号
- 奖励发放/领奖: 134 处信号
- 日志/埋点: 50 处信号
- 排行榜: 17 处信号
- 活动基础信息: 16 处信号
- 配置 JSON: 16 处信号
- HTTP 接口: 11 处信号
- 缓存/Redis: 7 处信号
- 用户初始化/身份: 2 处信号
- 任务系统: 2 处信号

## 状态与缓存 Key
- `KeyBroadcast` = `broadcast`
- `KeyMinIncome` = `min_income`
- `KeyUserLoss` = `user_loss:draw_type:%s`

## 模型与导出 API
- 导出结构体：DrawConf, DrawBag, DrawStyleConf, PrizeInfo, ReqUserDraw, ReqBuyDrawBag, ResDrawPrizeLog, ResDrawPrize, ResDrawLog, ReqDrawLog, GiftIdPoolConf
- 导出函数/方法：InitRoute

## 文件分层
- 配置/常量: 5 个文件，示例：`service.go`, `internal.go`, `route.go`, `server_draw.go`, `model.go`
- 工具辅助: 4 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_draw.go`
- 模型结构: 4 个文件，示例：`service.go`, `internal.go`, `server_draw.go`, `model.go`
- 接口处理: 3 个文件，示例：`server.go`, `internal.go`, `server_draw.go`
- 服务逻辑: 2 个文件，示例：`service.go`, `server_draw.go`
- 入口/路由: 1 个文件，示例：`route.go`
- 任务逻辑: 1 个文件，示例：`server_draw.go`

## 内部依赖
- `git.inke.cn/opd/activitys/inke.activity.service/act`: 5
- `git.inke.cn/inkelogic/daenerys/http/server`: 4
- `git.inke.cn/opd/activitys/inke.activity.service/utils`: 4
- `git.inke.cn/opd/activitys/inke.activity.service/model`: 4
- `git.inke.cn/BackendPlatform/golang/logging`: 2
- `git.inke.cn/opd/activitys/inke.activity.service/api/code`: 2
- `git.inke.cn/opd/activitys/inke.activity.service/dao`: 2
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRoom`: 1
- `git.inke.cn/BackendPlatform/golang/safego`: 1
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRank`: 1
- `git.inke.cn/opd/activitys/inke.activity.service/conf`: 1
- `git.inke.cn/opd/activitys/inke.activity.service/utils/big_log`: 1

## 第三方 import 概览
- github.com(1), bufio(1), os(1)

## 文件清单摘录
- `server.go`
- `service.go`
- `internal.go`
- `route.go`
- `server_draw.go`
- `model.go`

## 阅读路径建议
- 先确认 `ModuleName` 与活动配置，活动时间、入口 URL、奖励配置通常通过 `act.Srv.GetActInfoByte` 或 `act.Srv.GetActBaseInfo` 获取。
- 再读 Handler 列表，按页面接口、榜单接口、任务接口、领奖接口拆分主流程。
- 重点跟踪 `Key*` 常量和 `act.Dao.GetKey`，它们通常对应 Redis 状态、榜单 ZSet、领奖锁和任务进度。
- 看到 `Claim`、`Prize`、`Reward`、`SendGift`、`AddBag` 相关代码时，优先核对幂等锁、活动时间校验和奖励次数限制。
