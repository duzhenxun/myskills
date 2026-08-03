# act202603_yuanxiao 活动项目知识库

## 一图知识图谱
```mermaid
flowchart LR
  n2e427c26["Backend"]
  nc00e2a7b["HTTP 接口"]
  n05ebd5bf["HTTP 接口/Handler"]
  nd324d0dd["KeyAnchorDayRank: anchor_day_rank:tab:%d:date:%s"]
  nd9633799["KeyAnchorLoopTask: anchor_loop_task"]
  n83aee5e5["KeyAnchorRank: anchor_rank:tab:%d"]
  nf47cab19["KeyUserDayRank: user_day_rank:date:%s"]
  nd6f4a0a7["KeyUserDayTopPrize: user_day_top_prize"]
  n166f82d0["KeyUserEndTopPrize: user_end_top_prize"]
  n1d431157["KeyUserLoopTask: user_loop_task"]
  n2d46d03c["KeyUserRank: user_rank"]
  n93be903e["ModuleName: act202603_yuanxiao"]
  n70b79b0e["RadioAnyPrize"]
  n484c8f68["RadioPrize"]
  n2102196f["Redis/状态 Key"]
  n581dac73["UserDataLog"]
  n922fc411["act202603"]
  n7ede16b8["act202603_yuanxiao"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n7643d9c0["git.inke.cn/opd/activitys/inke.activity.service/act"]
  n2eb4e126["git.inke.cn/opd/activitys/inke.activity.service/api/code"]
  n05487b5c["git.inke.cn/opd/activitys/inke.activity.service/dao"]
  n04a9e5ed["git.inke.cn/opd/activitys/inke.activity.service/model"]
  ncd038f67["git.inke.cn/opd/activitys/inke.activity.service/model/modelRoom"]
  na3bdde25["git.inke.cn/opd/activitys/inke.activity.service/utils"]
  nb2f14d27["handler: anchorDayRank"]
  ndba745f2["handler: anchorRank"]
  nf534b047["handler: iTestWeb"]
  n68cbe357["handler: index"]
  nc2d5a20f["handler: interfaceConf"]
  ne5445ba9["handler: userDataLog"]
  n4693c645["handler: userDayRank"]
  n407ebf5f["handler: userRank"]
  n7cbd76cf["service: formatMsgContent"]
  n18e456b6["service: formatPrize"]
  n98d01bb2["service: getAnchorTab"]
  n2d457bd0["service: getRadioAnyPrize"]
  naa5f5105["service: getRadioNoticeType"]
  n74ffdca9["service: sendAnyPrize"]
  na455f0b2["service: sendPrize"]
  ne5680b13["service: sendRadioNotice"]
  n099e1afb["业务能力信号"]
  n88de2679["任务系统"]
  n95b52d26["奖励发放/领奖"]
  n4a731954["排行榜"]
  n33557018["日志/埋点"]
  nde2f9a1b["模型/响应结构"]
  n50239d91["活动公共依赖"]
  nd99a3a80["活动基础信息"]
  n5c886211["活动服务逻辑"]
  n5cbc9d99["类型: KA/SVIP 活动"]
  n1b9349a8["类型: 任务/活跃"]
  n2bdbab4b["类型: 榜单冲榜"]
  n538ab97d["类型: 节日/节点活动"]
  n716e776e["缓存/Redis"]
  ndc861ff4["配置 JSON"]
  n05ebd5bf --> nb2f14d27
  n05ebd5bf --> ndba745f2
  n05ebd5bf --> nf534b047
  n05ebd5bf --> n68cbe357
  n05ebd5bf --> nc2d5a20f
  n05ebd5bf --> ne5445ba9
  n05ebd5bf --> n4693c645
  n05ebd5bf --> n407ebf5f
  n2102196f --> nd324d0dd
  n2102196f --> nd9633799
  n2102196f --> n83aee5e5
  n2102196f --> nf47cab19
  n2102196f --> nd6f4a0a7
  n2102196f --> n166f82d0
  n2102196f --> n1d431157
  n2102196f --> n2d46d03c
  n7ede16b8 -- "exposes" --> n05ebd5bf
  n7ede16b8 -- "module" --> n93be903e
  n7ede16b8 -- "state" --> n2102196f
  n7ede16b8 -- "month" --> n922fc411
  n7ede16b8 -- "uses" --> n099e1afb
  n7ede16b8 -- "defines" --> nde2f9a1b
  n7ede16b8 -- "imports" --> n50239d91
  n7ede16b8 -- "core" --> n5c886211
  n7ede16b8 -- "type" --> n5cbc9d99
  n7ede16b8 -- "type" --> n1b9349a8
  n7ede16b8 -- "type" --> n2bdbab4b
  n7ede16b8 -- "type" --> n538ab97d
  n099e1afb --> nc00e2a7b
  n099e1afb --> n88de2679
  n099e1afb --> n95b52d26
  n099e1afb --> n4a731954
  n099e1afb --> n33557018
  n099e1afb --> nd99a3a80
  n099e1afb --> n716e776e
  n099e1afb --> ndc861ff4
  nde2f9a1b --> n2e427c26
  nde2f9a1b --> n70b79b0e
  nde2f9a1b --> n484c8f68
  nde2f9a1b --> n581dac73
  n50239d91 --> n7d7ea8b2
  n50239d91 --> n7bacf918
  n50239d91 --> n7643d9c0
  n50239d91 --> n2eb4e126
  n50239d91 --> n05487b5c
  n50239d91 --> n04a9e5ed
  n50239d91 --> ncd038f67
  n50239d91 --> na3bdde25
  n5c886211 --> n7cbd76cf
  n5c886211 --> n18e456b6
  n5c886211 --> n98d01bb2
  n5c886211 --> n2d457bd0
  n5c886211 --> naa5f5105
  n5c886211 --> n74ffdca9
  n5c886211 --> na455f0b2
  n5c886211 --> ne5680b13
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/opd/activitys/inke.activity.service/act/2026/act202603/act202603_yuanxiao`
- 所属月份：`act202603`
- 活动类型判断：KA/SVIP 活动, 榜单冲榜, 任务/活跃, 节日/节点活动
- ModuleName：`act202603_yuanxiao`
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
- `userDataLog`
- `userDayRank`
- `userRank`
- `anchorDayRank`
- `anchorRank`
- `interfaceConf`
- `iTestWeb`
- `iRecoverData`
- `iCronJob`
- `iBaseScore`

## 核心业务逻辑
### service 方法
- `sendRadioNotice`
- `getRadioNoticeType`
- `sendPrize`
- `sendAnyPrize`
- `getRadioAnyPrize`
- `formatMsgContent`
- `formatPrize`
- `getAnchorTab`
- `getAnchorTaskTab`
- `jobAnchorDayRankTop`
- `jobAnchorEndRankTop`
- `jobUserDayRankTop`
- `jobUserEndRankTop`
- `jobUserAllRankPrize`

### 业务能力信号
- 排行榜: 150 处信号
- 奖励发放/领奖: 110 处信号
- 日志/埋点: 33 处信号
- 配置 JSON: 33 处信号
- 缓存/Redis: 22 处信号
- 活动基础信息: 19 处信号
- HTTP 接口: 11 处信号
- 任务系统: 8 处信号

## 状态与缓存 Key
- `KeyUserDayRank` = `user_day_rank:date:%s`
- `KeyUserRank` = `user_rank`
- `KeyAnchorDayRank` = `anchor_day_rank:tab:%d:date:%s`
- `KeyAnchorRank` = `anchor_rank:tab:%d`
- `KeyUserLoopTask` = `user_loop_task`
- `KeyAnchorLoopTask` = `anchor_loop_task`
- `KeyUserDayTopPrize` = `user_day_top_prize`
- `KeyUserEndTopPrize` = `user_end_top_prize`
- `KeyAnchorDayTopPrize` = `anchor_day_top_prize_%d`
- `KeyAnchorEndTopPrize` = `anchor_end_top_prize_%d`
- `KeyConfessId` = `KeyConfessId`
- `KeyConfessUserNum` = `KeyConfessUserNum:uid_%d`
- `KeyUserDataLog` = `user_data_log:uid:%d`

## 模型与导出 API
- 导出结构体：Backend, UserDataLog, RadioPrize, RadioAnyPrize
- 导出函数/方法：InitRoute, GiftHandle

## 文件分层
- 配置/常量: 6 个文件，示例：`server.go`, `service.go`, `internal.go`, `route.go`, `kafka.go`, `model.go`
- 任务逻辑: 5 个文件，示例：`server.go`, `service.go`, `internal.go`, `route.go`, `model.go`
- 工具辅助: 4 个文件，示例：`server.go`, `service.go`, `internal.go`, `kafka.go`
- 模型结构: 4 个文件，示例：`service.go`, `internal.go`, `kafka.go`, `model.go`
- 接口处理: 2 个文件，示例：`server.go`, `internal.go`
- 服务逻辑: 1 个文件，示例：`service.go`
- 入口/路由: 1 个文件，示例：`route.go`

## 内部依赖
- `git.inke.cn/opd/activitys/inke.activity.service/act`: 5
- `git.inke.cn/opd/activitys/inke.activity.service/utils`: 4
- `git.inke.cn/opd/activitys/inke.activity.service/model`: 4
- `git.inke.cn/inkelogic/daenerys/http/server`: 3
- `git.inke.cn/opd/activitys/inke.activity.service/dao`: 3
- `git.inke.cn/opd/activitys/inke.activity.service/api/code`: 2
- `git.inke.cn/BackendPlatform/golang/logging`: 2
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRoom`: 1
- `git.inke.cn/opd/activitys/inke.activity.service/utils/big_log`: 1
- `git.inke.cn/BackendPlatform/golang/safego`: 1
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRank`: 1
- `git.inke.cn/BackendPlatform/golang/trace`: 1

## 第三方 import 概览
- github.com(1), bufio(1), os(1)

## 文件清单摘录
- `server.go`
- `service.go`
- `internal.go`
- `route.go`
- `kafka.go`
- `model.go`

## 阅读路径建议
- 先确认 `ModuleName` 与活动配置，活动时间、入口 URL、奖励配置通常通过 `act.Srv.GetActInfoByte` 或 `act.Srv.GetActBaseInfo` 获取。
- 再读 Handler 列表，按页面接口、榜单接口、任务接口、领奖接口拆分主流程。
- 重点跟踪 `Key*` 常量和 `act.Dao.GetKey`，它们通常对应 Redis 状态、榜单 ZSet、领奖锁和任务进度。
- 看到 `Claim`、`Prize`、`Reward`、`SendGift`、`AddBag` 相关代码时，优先核对幂等锁、活动时间校验和奖励次数限制。
