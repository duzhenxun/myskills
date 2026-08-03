# act202605_xintiaogongzhen 活动项目知识库

## 一图知识图谱
```mermaid
flowchart LR
  n2e427c26["Backend"]
  n34ea80c3["GBroadcast"]
  nc00e2a7b["HTTP 接口"]
  n05ebd5bf["HTTP 接口/Handler"]
  ndb0cc0a6["KeyAnchorTask: anchor_task_%d"]
  nb3e23381["KeyAnchorTaskScore: anchor_task_score"]
  n7e55e6c3["KeyCPTask: cp_task"]
  n64b233a5["KeyCPTaskAide: cp_task_anchor_%d"]
  n5b4194b8["KeyCPTaskUser: cp_task_user_%d"]
  n376ea686["KeyRound0521: round_reward_0521"]
  nf47cab19["KeyUserDayRank: user_day_rank:date:%s"]
  n2d46d03c["KeyUserRank: user_rank"]
  nc0e4c3df["ModuleName: act202605_xintiaogongzhen"]
  n2102196f["Redis/状态 Key"]
  n77b2b14c["act202605"]
  nbf68e0fb["act202605_xintiaogongzhen"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n7643d9c0["git.inke.cn/opd/activitys/inke.activity.service/act"]
  n2eb4e126["git.inke.cn/opd/activitys/inke.activity.service/api/code"]
  n05487b5c["git.inke.cn/opd/activitys/inke.activity.service/dao"]
  n04a9e5ed["git.inke.cn/opd/activitys/inke.activity.service/model"]
  nf98059d1["git.inke.cn/opd/activitys/inke.activity.service/model/modelRank"]
  na3bdde25["git.inke.cn/opd/activitys/inke.activity.service/utils"]
  nb2f14d27["handler: anchorDayRank"]
  na171d610["handler: anchorHourRank"]
  ndba745f2["handler: anchorRank"]
  n7e5e8e80["handler: cpTask"]
  n30f235e0["handler: getBroadcast"]
  n68cbe357["handler: index"]
  n4693c645["handler: userDayRank"]
  n407ebf5f["handler: userRank"]
  ndbdbb2b8["service: addBroadcast"]
  n2fb39da3["service: fillCpRankTaskInfo"]
  n7cbd76cf["service: formatMsgContent"]
  n18e456b6["service: formatPrize"]
  n98d01bb2["service: getAnchorTab"]
  n7a2e36b4["service: getAnchorTaskTab"]
  n8b7b2635["service: getBroadcast"]
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
  n538ab97d["类型: 节日/节点活动"]
  n716e776e["缓存/Redis"]
  ndc861ff4["配置 JSON"]
  n05ebd5bf --> nb2f14d27
  n05ebd5bf --> na171d610
  n05ebd5bf --> ndba745f2
  n05ebd5bf --> n7e5e8e80
  n05ebd5bf --> n30f235e0
  n05ebd5bf --> n68cbe357
  n05ebd5bf --> n4693c645
  n05ebd5bf --> n407ebf5f
  n2102196f --> ndb0cc0a6
  n2102196f --> nb3e23381
  n2102196f --> n7e55e6c3
  n2102196f --> n64b233a5
  n2102196f --> n5b4194b8
  n2102196f --> n376ea686
  n2102196f --> nf47cab19
  n2102196f --> n2d46d03c
  nbf68e0fb -- "exposes" --> n05ebd5bf
  nbf68e0fb -- "module" --> nc0e4c3df
  nbf68e0fb -- "state" --> n2102196f
  nbf68e0fb -- "month" --> n77b2b14c
  nbf68e0fb -- "uses" --> n099e1afb
  nbf68e0fb -- "defines" --> nde2f9a1b
  nbf68e0fb -- "imports" --> n50239d91
  nbf68e0fb -- "core" --> n5c886211
  nbf68e0fb -- "type" --> n5cbc9d99
  nbf68e0fb -- "type" --> n1b9349a8
  nbf68e0fb -- "type" --> n2bdbab4b
  nbf68e0fb -- "type" --> n538ab97d
  n099e1afb --> nc00e2a7b
  n099e1afb --> n88de2679
  n099e1afb --> n95b52d26
  n099e1afb --> n4a731954
  n099e1afb --> n33557018
  n099e1afb --> nd99a3a80
  n099e1afb --> n716e776e
  n099e1afb --> ndc861ff4
  nde2f9a1b --> n2e427c26
  nde2f9a1b --> n34ea80c3
  n50239d91 --> n7d7ea8b2
  n50239d91 --> n7bacf918
  n50239d91 --> n7643d9c0
  n50239d91 --> n2eb4e126
  n50239d91 --> n05487b5c
  n50239d91 --> n04a9e5ed
  n50239d91 --> nf98059d1
  n50239d91 --> na3bdde25
  n5c886211 --> ndbdbb2b8
  n5c886211 --> n2fb39da3
  n5c886211 --> n7cbd76cf
  n5c886211 --> n18e456b6
  n5c886211 --> n98d01bb2
  n5c886211 --> n7a2e36b4
  n5c886211 --> n8b7b2635
  n5c886211 --> na455f0b2
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/opd/activitys/inke.activity.service/act/2026/act202605/act202605_xintiaogongzhen`
- 所属月份：`act202605`
- 活动类型判断：KA/SVIP 活动, 榜单冲榜, 任务/活跃, 节日/节点活动
- ModuleName：`act202605_xintiaogongzhen`
- README 摘要：无标题

```text
未发现 README 或 README 内容为空
```

## 静态结构画像
- 文本/代码文件数：11
- Go 文件数：10
- 文件类型分布：.go(10), .md(1)

## 入口与接口
### 路由线索
- 未发现显式路由字符串，需结合活动总路由注册确认

### Handler 函数
- `index`
- `getBroadcast`
- `cpTask`
- `anchorHourRank`
- `userDayRank`
- `userRank`
- `anchorDayRank`
- `anchorRank`
- `interfaceConf`
- `iTestWeb`
- `iRecoverData`
- `iCronJob`
- `iBaseScore`
- `icon`
- `userTask`
- `sharePrize`
- `shareUserRank`

## 核心业务逻辑
### service 方法
- `addBroadcast`
- `getBroadcast`
- `fillCpRankTaskInfo`
- `sendPrize`
- `formatMsgContent`
- `formatPrize`
- `getAnchorTab`
- `getAnchorTaskTab`
- `jobAnchorDayRankTop`
- `jobAnchorEndRankTop`
- `jobUserDayRankTop`
- `jobUserEndRankTop`
- `jobUserAllRankPrize`
- `getUserRound`
- `randConfessionContent`
- `getRoundRewardDateConf`
- `getRoundReward0520Conf`
- `sendStageReward0520`
- `setAnchorCpTask`
- `sendRoundReward0519`
- `sendRoundReward0521`
- `setAnchorLoopTask`
- `setAnchorTaskScore`
- `getAnchorTaskScore`
- `setAnchorTask`
- `setAnchorRoundTask`
- `setLevelTask`
- `getIcon1Data`
- `getIcon12DataA`
- `getIcon12DataB`
- `getHourRankIcon`
- `getIcon7Data`
- `getUserTaskScore`
- `setUserTaskScore`
- `setUserTask`

### 业务能力信号
- 排行榜: 345 处信号
- 任务系统: 275 处信号
- 奖励发放/领奖: 206 处信号
- 缓存/Redis: 79 处信号
- 日志/埋点: 77 处信号
- 配置 JSON: 54 处信号
- 活动基础信息: 29 处信号
- HTTP 接口: 17 处信号
- 用户初始化/身份: 4 处信号

## 状态与缓存 Key
- `KeyAnchorTask` = `anchor_task_%d`
- `KeyCPTask` = `cp_task`
- `KeyCPTaskUser` = `cp_task_user_%d`
- `KeyCPTaskAide` = `cp_task_anchor_%d`
- `KeyRound0521` = `round_reward_0521`
- `KeyAnchorTaskScore` = `anchor_task_score`
- `KeyUserDayRank` = `user_day_rank:date:%s`
- `KeyUserRank` = `user_rank`
- `KeyUserDayPayScore` = `user_day_pay_score:date:%s`
- `KeyUserTaskScore` = `user_task_score`
- `KeyAnchorDayRank` = `anchor_day_rank:tab:%d:date:%s`
- `KeyAnchorHourRank` = `anchor_hour_rank:tab:%d:hour:%s`
- `KeyAnchorRank` = `anchor_rank:tab:%d`
- `KeyFlowerPoint` = `KeyFlowerPoint:date_%s:uid_%d`
- `KeyAnchorCpFireNum` = `KeyAnchorCpFireNum:date_%s:aid_%d`
- `KeyUserCpFireNum` = `KeyUserCpFireNum:date_%s:uid_%d`
- `KeyWebBroadcast` = `web_broadcast`
- `KeyUserWebBroadcast` = `user_web_broadcast:uid_%d`
- `KeyRoundReward0519` = `round_reward_0519:date_%s:aid_%d:uid_%d:round_%d`
- `KeyRoundReward0520` = `round_reward_0520:date_%s:aid_%d:uid_%d:round_%d:task_%s`
- `KeyRoundReward0521` = `round_reward_0521:date_%s:aid_%d:uid_%d:round_%d`
- `KeyUserLoopTask` = `user_loop_task`
- `KeyAnchorLoopTask` = `anchor_loop_task`
- `KeyUserDayTopPrize` = `user_day_top_prize`
- `KeyUserEndTopPrize` = `user_end_top_prize`
- `KeyAnchorDayTopPrize` = `anchor_day_top_prize_%d`
- `KeyAnchorDayTopUser` = `anchor_day_top_user_prize_%d`
- `KeyAnchorEndTopPrize` = `anchor_end_top_prize_%d`

## 模型与导出 API
- 导出结构体：Backend, GBroadcast
- 导出函数/方法：InitRoute, Cron, GiftHandle, RechargeHandle

## 文件分层
- 任务逻辑: 10 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_anchor_task.go`, `route.go`, `cron.go`
- 配置/常量: 9 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_anchor_task.go`, `route.go`, `kafka.go`
- 工具辅助: 8 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_anchor_task.go`, `cron.go`, `kafka.go`
- 模型结构: 8 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_anchor_task.go`, `kafka.go`, `server_icon.go`
- 接口处理: 4 个文件，示例：`server.go`, `internal.go`, `server_icon.go`, `server_user_task.go`
- 服务逻辑: 4 个文件，示例：`service.go`, `server_anchor_task.go`, `server_icon.go`, `server_user_task.go`
- 入口/路由: 1 个文件，示例：`route.go`

## 内部依赖
- `git.inke.cn/opd/activitys/inke.activity.service/act`: 9
- `git.inke.cn/opd/activitys/inke.activity.service/dao`: 8
- `git.inke.cn/opd/activitys/inke.activity.service/utils`: 8
- `git.inke.cn/opd/activitys/inke.activity.service/model`: 6
- `git.inke.cn/inkelogic/daenerys/http/server`: 5
- `git.inke.cn/BackendPlatform/golang/logging`: 5
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRank`: 3
- `git.inke.cn/opd/activitys/inke.activity.service/api/code`: 3
- `git.inke.cn/opd/activitys/inke.activity.service/utils/big_log`: 2
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRoom`: 1
- `git.inke.cn/BackendPlatform/golang/safego`: 1
- `git.inke.cn/BackendPlatform/golang/trace`: 1
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelIcon`: 1

## 第三方 import 概览
- github.com(2), bufio(1), os(1), crypto(1)

## 文件清单摘录
- `server.go`
- `service.go`
- `internal.go`
- `server_anchor_task.go`
- `execution-steps.md`
- `route.go`
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
