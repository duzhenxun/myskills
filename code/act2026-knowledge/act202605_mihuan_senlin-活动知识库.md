# act202605_mihuan_senlin 活动项目知识库

## 一图知识图谱
```mermaid
flowchart LR
  n2e427c26["Backend"]
  nc00e2a7b["HTTP 接口"]
  n05ebd5bf["HTTP 接口/Handler"]
  nd324d0dd["KeyAnchorDayRank: anchor_day_rank:tab:%d:date:%s"]
  n15e7f34c["KeyAnchorLoveTotal: anchor_love_total:date:%s"]
  nb3e23381["KeyAnchorTaskScore: anchor_task_score"]
  na7890754["KeyUserDayAnchor: user_day_anchor:date:%s"]
  nf47cab19["KeyUserDayRank: user_day_rank:date:%s"]
  n1d431157["KeyUserLoopTask: user_loop_task"]
  na795ac74["KeyUserLoveTotal: user_love_total:date:%s"]
  n9c3a32eb["KeyUserTaskScore: user_task_score"]
  nb43314ef["ModuleName: act202605_mihuan_senlin"]
  n2102196f["Redis/状态 Key"]
  n77b2b14c["act202605"]
  n71506c47["act202605_mihuan_senlin"]
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
  n4abc26ec["handler: iRecoverData"]
  nf534b047["handler: iTestWeb"]
  n68cbe357["handler: index"]
  nc2d5a20f["handler: interfaceConf"]
  n4693c645["handler: userDayRank"]
  n29a50c2f["handler: webBroadcast"]
  n7cbd76cf["service: formatMsgContent"]
  n18e456b6["service: formatPrize"]
  n98d01bb2["service: getAnchorTab"]
  n7a2e36b4["service: getAnchorTaskTab"]
  nb3f11d03["service: jobAnchorDayRankTop"]
  nbd86d42c["service: jobUserDayRankTop"]
  na455f0b2["service: sendPrize"]
  nae6403ea["service: systemDrawPrize"]
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
  nda238ed0["类型: 游戏玩法"]
  n716e776e["缓存/Redis"]
  ndc861ff4["配置 JSON"]
  n05ebd5bf --> nb2f14d27
  n05ebd5bf --> nc26a6343
  n05ebd5bf --> n4abc26ec
  n05ebd5bf --> nf534b047
  n05ebd5bf --> n68cbe357
  n05ebd5bf --> nc2d5a20f
  n05ebd5bf --> n4693c645
  n05ebd5bf --> n29a50c2f
  n2102196f --> nd324d0dd
  n2102196f --> n15e7f34c
  n2102196f --> nb3e23381
  n2102196f --> na7890754
  n2102196f --> nf47cab19
  n2102196f --> n1d431157
  n2102196f --> na795ac74
  n2102196f --> n9c3a32eb
  n71506c47 -- "exposes" --> n05ebd5bf
  n71506c47 -- "module" --> nb43314ef
  n71506c47 -- "state" --> n2102196f
  n71506c47 -- "month" --> n77b2b14c
  n71506c47 -- "uses" --> n099e1afb
  n71506c47 -- "defines" --> nde2f9a1b
  n71506c47 -- "imports" --> n50239d91
  n71506c47 -- "core" --> n5c886211
  n71506c47 -- "type" --> n5cbc9d99
  n71506c47 -- "type" --> n1b9349a8
  n71506c47 -- "type" --> n2bdbab4b
  n71506c47 -- "type" --> nda238ed0
  n099e1afb --> nc00e2a7b
  n099e1afb --> n88de2679
  n099e1afb --> n95b52d26
  n099e1afb --> n4a731954
  n099e1afb --> n33557018
  n099e1afb --> nd99a3a80
  n099e1afb --> n716e776e
  n099e1afb --> ndc861ff4
  nde2f9a1b --> n2e427c26
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
  n5c886211 --> nbd86d42c
  n5c886211 --> na455f0b2
  n5c886211 --> nae6403ea
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/opd/activitys/inke.activity.service/act/2026/act202605/act202605_mihuan_senlin`
- 所属月份：`act202605`
- 活动类型判断：KA/SVIP 活动, 游戏玩法, 榜单冲榜, 任务/活跃
- ModuleName：`act202605_mihuan_senlin`
- README 摘要：无标题

```text
未发现 README 或 README 内容为空
```

## 静态结构画像
- 文本/代码文件数：12
- Go 文件数：11
- 文件类型分布：.go(11), .md(1)

## 入口与接口
### 路由线索
- 未发现显式路由字符串，需结合活动总路由注册确认

### Handler 函数
- `index`
- `webBroadcast`
- `userDayRank`
- `anchorDayRank`
- `anchorDayTop`
- `interfaceConf`
- `iTestWeb`
- `iRecoverData`
- `iCronJob`
- `iBaseScore`
- `anchorTaskCheckIn`
- `anchorTaskLoveTotal`
- `anchorTaskUserTotal`
- `icon`
- `giftTaskInfo`
- `userTaskCheckIn`
- `userTaskLoveTotal`
- `userTaskAnchorTotal`

## 核心业务逻辑
### service 方法
- `sendPrize`
- `formatMsgContent`
- `formatPrize`
- `getAnchorTab`
- `getAnchorTaskTab`
- `jobAnchorDayRankTop`
- `jobUserDayRankTop`
- `systemDrawPrize`
- `setAnchorTaskScore`
- `getAnchorTaskScore`
- `setAnchorTask`
- `setAnchorLoveTotal`
- `setAnchorTaskCheckIn`
- `setAnchorTaskUserTotal`
- `setLevelTask`
- `getIcon1Data`
- `getIcon12DataA`
- `getIcon12DataC`
- `getIcon12DataB`
- `getIcon7DataA`
- `game`
- `getUserTaskScore`
- `setUserTaskScore`
- `setUserTask`
- `setUserTask2`
- `setUserRoundTask`
- `setUserLoopTask`
- `getScoreDiffRound`

### 业务能力信号
- 任务系统: 432 处信号
- 排行榜: 164 处信号
- 奖励发放/领奖: 126 处信号
- 日志/埋点: 79 处信号
- 缓存/Redis: 64 处信号
- 活动基础信息: 29 处信号
- HTTP 接口: 18 处信号
- 配置 JSON: 11 处信号
- 用户初始化/身份: 2 处信号

## 状态与缓存 Key
- `KeyAnchorDayRank` = `anchor_day_rank:tab:%d:date:%s`
- `KeyAnchorLoveTotal` = `anchor_love_total:date:%s`
- `KeyAnchorTaskScore` = `anchor_task_score`
- `KeyUserDayRank` = `user_day_rank:date:%s`
- `KeyUserDayAnchor` = `user_day_anchor:date:%s`
- `KeyUserLoveTotal` = `user_love_total:date:%s`
- `KeyUserTaskScore` = `user_task_score`
- `KeyUserLoopTask` = `user_loop_task`
- `KeyAnchorLoopTask` = `anchor_loop_task`
- `KeyUserDayTopPrize` = `user_day_top_prize`
- `KeyUserEndTopPrize` = `user_end_top_prize`
- `KeyAnchorDayTopPrize` = `anchor_day_top_prize_%d`
- `KeyAnchorEndTopPrize` = `anchor_end_top_prize_%d`
- `KeyAnchorTask` = `anchor_task_%d`
- `KeyUserDayGiftTotal` = `user_day_gift_total:date:%s`

## 模型与导出 API
- 导出结构体：Backend
- 导出函数/方法：InitRoute, Cron, GiftHandle

## 文件分层
- 配置/常量: 10 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_anchor_task.go`, `route.go`, `kafka.go`
- 任务逻辑: 10 个文件，示例：`service.go`, `internal.go`, `server_anchor_task.go`, `route.go`, `cron.go`, `kafka.go`
- 工具辅助: 9 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_anchor_task.go`, `cron.go`, `kafka.go`
- 接口处理: 6 个文件，示例：`server.go`, `internal.go`, `server_anchor_task.go`, `server_icon.go`, `server_gift_game.go`, `server_user_task.go`
- 模型结构: 6 个文件，示例：`service.go`, `internal.go`, `kafka.go`, `server_icon.go`, `model.go`, `server_user_task.go`
- 服务逻辑: 5 个文件，示例：`service.go`, `server_anchor_task.go`, `server_icon.go`, `server_gift_game.go`, `server_user_task.go`
- 入口/路由: 1 个文件，示例：`route.go`

## 内部依赖
- `git.inke.cn/opd/activitys/inke.activity.service/act`: 10
- `git.inke.cn/opd/activitys/inke.activity.service/utils`: 9
- `git.inke.cn/opd/activitys/inke.activity.service/dao`: 8
- `git.inke.cn/inkelogic/daenerys/http/server`: 7
- `git.inke.cn/BackendPlatform/golang/logging`: 5
- `git.inke.cn/opd/activitys/inke.activity.service/model`: 5
- `git.inke.cn/opd/activitys/inke.activity.service/utils/big_log`: 3
- `git.inke.cn/opd/activitys/inke.activity.service/api/code`: 2
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRoom`: 1
- `git.inke.cn/BackendPlatform/golang/safego`: 1
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRank`: 1
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
- `cron.go`
- `kafka.go`
- `server_icon.go`
- `model.go`
- `server_gift_game.go`
- `flow.md`
- `server_user_task.go`

## 阅读路径建议
- 先确认 `ModuleName` 与活动配置，活动时间、入口 URL、奖励配置通常通过 `act.Srv.GetActInfoByte` 或 `act.Srv.GetActBaseInfo` 获取。
- 再读 Handler 列表，按页面接口、榜单接口、任务接口、领奖接口拆分主流程。
- 重点跟踪 `Key*` 常量和 `act.Dao.GetKey`，它们通常对应 Redis 状态、榜单 ZSet、领奖锁和任务进度。
- 看到 `Claim`、`Prize`、`Reward`、`SendGift`、`AddBag` 相关代码时，优先核对幂等锁、活动时间校验和奖励次数限制。
