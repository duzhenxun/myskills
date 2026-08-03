# act202603_masked_ball 活动项目知识库

## 一图知识图谱
```mermaid
flowchart LR
  nbf5666a4["DrawBag"]
  n0316eaf3["DrawConf"]
  n263be4c2["DrawStyleConf"]
  nc00e2a7b["HTTP 接口"]
  n05ebd5bf["HTTP 接口/Handler"]
  nd324d0dd["KeyAnchorDayRank: anchor_day_rank:tab:%d:date:%s"]
  n907c1800["KeyAnchorNamingFirstTimeUser: anchor_naming_first_time_user"]
  nc03ef89b["KeyAnchorNamingFirstTimeUserInfo: anchor_naming_first_time_user_info"]
  n79b8e4c9["KeyAnchorNamingRank: anchor_naming_rank"]
  n1a5e0ca7["KeyAnchorNamingUser: anchor_naming:aid:%d"]
  nb3e23381["KeyAnchorTaskScore: anchor_task_score"]
  ncd1aa4a7["KeyUserFragment: user_fragment:uid:%d:type:%s"]
  n2d46d03c["KeyUserRank: user_rank"]
  nd1edd9b6["ModuleName: act202603_masked_ball"]
  n82bfbb57["PrizeInfo"]
  n2102196f["Redis/状态 Key"]
  ne69ecd46["ReqBuyDrawBag"]
  n0874d5b2["ReqUserDraw"]
  n7ebf1f48["ResDrawPrize"]
  n2c47d69d["ResDrawPrizeLog"]
  n922fc411["act202603"]
  nc360e43c["act202603_masked_ball"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n7643d9c0["git.inke.cn/opd/activitys/inke.activity.service/act"]
  n2eb4e126["git.inke.cn/opd/activitys/inke.activity.service/api/code"]
  n05487b5c["git.inke.cn/opd/activitys/inke.activity.service/dao"]
  n04a9e5ed["git.inke.cn/opd/activitys/inke.activity.service/model"]
  na3bdde25["git.inke.cn/opd/activitys/inke.activity.service/utils"]
  n0306c622["git.inke.cn/opd/activitys/inke.activity.service/utils/big_log"]
  nb2f14d27["handler: anchorDayRank"]
  nc26a6343["handler: anchorDayTop"]
  nf9bea465["handler: anchorHighRank"]
  nf696b282["handler: anchorNamingRank"]
  n4abc26ec["handler: iRecoverData"]
  nf534b047["handler: iTestWeb"]
  n68cbe357["handler: index"]
  nc2d5a20f["handler: interfaceConf"]
  n7cbd76cf["service: formatMsgContent"]
  n18e456b6["service: formatPrize"]
  n98d01bb2["service: getAnchorTab"]
  n7a2e36b4["service: getAnchorTaskTab"]
  nb3f11d03["service: jobAnchorDayRankTop"]
  n78295049["service: jobUserAllRankPrize"]
  nfed57101["service: jobUserEndRankTop"]
  na455f0b2["service: sendPrize"]
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
  n57367205["类型: 用户侧活动"]
  n716e776e["缓存/Redis"]
  ndc861ff4["配置 JSON"]
  n05ebd5bf --> nb2f14d27
  n05ebd5bf --> nc26a6343
  n05ebd5bf --> nf9bea465
  n05ebd5bf --> nf696b282
  n05ebd5bf --> n4abc26ec
  n05ebd5bf --> nf534b047
  n05ebd5bf --> n68cbe357
  n05ebd5bf --> nc2d5a20f
  n2102196f --> nd324d0dd
  n2102196f --> n907c1800
  n2102196f --> nc03ef89b
  n2102196f --> n79b8e4c9
  n2102196f --> n1a5e0ca7
  n2102196f --> nb3e23381
  n2102196f --> ncd1aa4a7
  n2102196f --> n2d46d03c
  nc360e43c -- "exposes" --> n05ebd5bf
  nc360e43c -- "module" --> nd1edd9b6
  nc360e43c -- "state" --> n2102196f
  nc360e43c -- "month" --> n922fc411
  nc360e43c -- "uses" --> n099e1afb
  nc360e43c -- "defines" --> nde2f9a1b
  nc360e43c -- "imports" --> n50239d91
  nc360e43c -- "core" --> n5c886211
  nc360e43c -- "type" --> n5cbc9d99
  nc360e43c -- "type" --> n1b9349a8
  nc360e43c -- "type" --> n2bdbab4b
  nc360e43c -- "type" --> n57367205
  n099e1afb --> nc00e2a7b
  n099e1afb --> n88de2679
  n099e1afb --> n95b52d26
  n099e1afb --> n4a731954
  n099e1afb --> n33557018
  n099e1afb --> nd99a3a80
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
  n50239d91 --> na3bdde25
  n50239d91 --> n0306c622
  n5c886211 --> n7cbd76cf
  n5c886211 --> n18e456b6
  n5c886211 --> n98d01bb2
  n5c886211 --> n7a2e36b4
  n5c886211 --> nb3f11d03
  n5c886211 --> n78295049
  n5c886211 --> nfed57101
  n5c886211 --> na455f0b2
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/opd/activitys/inke.activity.service/act/2026/act202603/act202603_masked_ball`
- 所属月份：`act202603`
- 活动类型判断：KA/SVIP 活动, 榜单冲榜, 任务/活跃, 用户侧活动
- ModuleName：`act202603_masked_ball`
- README 摘要：无标题

```text
未发现 README 或 README 内容为空
```

## 静态结构画像
- 文本/代码文件数：11
- Go 文件数：11
- 文件类型分布：.go(11)

## 入口与接口
### 路由线索
- 未发现显式路由字符串，需结合活动总路由注册确认

### Handler 函数
- `index`
- `anchorDayRank`
- `anchorHighRank`
- `anchorNamingRank`
- `anchorDayTop`
- `interfaceConf`
- `iTestWeb`
- `iRecoverData`
- `iCronJob`
- `iBaseScore`
- `anchorTask`
- `drawUserConf`
- `drawBuyBag`
- `drawPrize`
- `drawWebBroadcast`
- `drawPrizeLog`
- `icon`
- `userTask`

## 核心业务逻辑
### service 方法
- `sendPrize`
- `formatMsgContent`
- `formatPrize`
- `getAnchorTab`
- `getAnchorTaskTab`
- `jobAnchorDayRankTop`
- `jobUserEndRankTop`
- `jobUserAllRankPrize`
- `getUserFragmentMinScore`
- `setUserFragment`
- `getAnchorHighLevel`
- `setAnchorTaskScore`
- `getAnchorTaskScore`
- `setAnchorTask`
- `setAnchorRoundTask`
- `getDrawConf`
- `drawPrize`
- `systemDrawPrize`
- `systemDrawPrizeOld`
- `drawPrizeOld`
- `drawListPrize`
- `allPrizePool`
- `getIcon1Data`
- `getIcon12DataA`
- `getIcon12DataB`
- `getIcon7DataA`
- `setUserTask`
- `setUserUserFragment`
- `setNamingUserTask`
- `getScoreDiffRound`
- `setUserActiveTask`

### 业务能力信号
- 奖励发放/领奖: 326 处信号
- 任务系统: 278 处信号
- 排行榜: 182 处信号
- 日志/埋点: 143 处信号
- 缓存/Redis: 43 处信号
- 活动基础信息: 39 处信号
- 配置 JSON: 23 处信号
- HTTP 接口: 18 处信号
- 用户初始化/身份: 5 处信号

## 状态与缓存 Key
- `KeyUserRank` = `user_rank`
- `KeyUserFragment` = `user_fragment:uid:%d:type:%s`
- `KeyAnchorDayRank` = `anchor_day_rank:tab:%d:date:%s`
- `KeyAnchorTaskScore` = `anchor_task_score`
- `KeyAnchorNamingRank` = `anchor_naming_rank`
- `KeyAnchorNamingUser` = `anchor_naming:aid:%d`
- `KeyAnchorNamingFirstTimeUser` = `anchor_naming_first_time_user`
- `KeyAnchorNamingFirstTimeUserInfo` = `anchor_naming_first_time_user_info`
- `KeyAnchorHighRank` = `anchor_high_rank`
- `KeyAnchorTask` = `anchor_task_%d`
- `KeyUserLoopTask` = `user_loop_task`
- `KeyAnchorLoopTask` = `anchor_loop_task`
- `KeyUserDayTopPrize` = `user_day_top_prize`
- `KeyUserEndTopPrize` = `user_end_top_prize`
- `KeyAnchorDayTopPrize` = `anchor_day_top_prize_%d`
- `KeyAnchorEndTopPrize` = `anchor_end_top_prize_%d`
- `KeyUserTaskScore` = `user_task_score`
- `KeyUserDayActiveTaskRound` = `user_active_task:task_key:%s:date:%s`

## 模型与导出 API
- 导出结构体：DrawConf, DrawBag, DrawStyleConf, PrizeInfo, ReqUserDraw, ReqBuyDrawBag, ResDrawPrizeLog, ResDrawPrize, ResDrawLog, ReqDrawLog, Backend, UserDataLog
- 导出函数/方法：InitRoute, Cron, GiftHandle, RoomInOutHandle

## 文件分层
- 配置/常量: 10 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_anchor_task.go`, `route.go`, `server_draw.go`
- 任务逻辑: 10 个文件，示例：`service.go`, `internal.go`, `server_anchor_task.go`, `route.go`, `server_draw.go`, `cron.go`
- 工具辅助: 9 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_anchor_task.go`, `server_draw.go`, `cron.go`
- 模型结构: 7 个文件，示例：`service.go`, `internal.go`, `server_draw.go`, `kafka.go`, `server_icon.go`, `model.go`
- 接口处理: 6 个文件，示例：`server.go`, `internal.go`, `server_anchor_task.go`, `server_draw.go`, `server_icon.go`, `server_user_task.go`
- 服务逻辑: 5 个文件，示例：`service.go`, `server_anchor_task.go`, `server_draw.go`, `server_icon.go`, `server_user_task.go`
- 入口/路由: 1 个文件，示例：`route.go`

## 内部依赖
- `git.inke.cn/opd/activitys/inke.activity.service/act`: 10
- `git.inke.cn/opd/activitys/inke.activity.service/utils`: 9
- `git.inke.cn/opd/activitys/inke.activity.service/dao`: 8
- `git.inke.cn/inkelogic/daenerys/http/server`: 7
- `git.inke.cn/opd/activitys/inke.activity.service/model`: 6
- `git.inke.cn/BackendPlatform/golang/logging`: 5
- `git.inke.cn/opd/activitys/inke.activity.service/api/code`: 3
- `git.inke.cn/opd/activitys/inke.activity.service/utils/big_log`: 3
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRoom`: 1
- `git.inke.cn/BackendPlatform/golang/safego`: 1
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRank`: 1
- `git.inke.cn/opd/activitys/inke.activity.service/conf`: 1
- `git.inke.cn/BackendPlatform/golang/trace`: 1
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelIcon`: 1

## 第三方 import 概览
- github.com(2), bufio(1), os(1)

## 文件清单摘录
- `server.go`
- `service.go`
- `internal.go`
- `server_anchor_task.go`
- `route.go`
- `server_draw.go`
- `cron.go`
- `kafka.go`
- `server_icon.go`
- `model.go`
- `server_user_task.go`

## 阅读路径建议
- 先确认 `ModuleName` 与活动配置，活动时间、入口 URL、奖励配置通常通过 `act.Srv.GetActInfoByte` 或 `act.Srv.GetActBaseInfo` 获取。
- 再读 Handler 列表，按页面接口、榜单接口、任务接口、领奖接口拆分主流程。
- 重点跟踪 `Key*` 常量和 `act.Dao.GetKey`，它们通常对应 Redis 状态、榜单 ZSet、领奖锁和任务进度。
- 看到 `Claim`、`Prize`、`Reward`、`SendGift`、`AddBag` 相关代码时，优先核对幂等锁、活动时间校验和奖励次数限制。
