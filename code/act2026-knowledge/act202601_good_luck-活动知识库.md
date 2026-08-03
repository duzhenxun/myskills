# act202601_good_luck 活动项目知识库

## 一图知识图谱
```mermaid
flowchart LR
  nbf5666a4["DrawBag"]
  n0316eaf3["DrawConf"]
  n263be4c2["DrawStyleConf"]
  nc00e2a7b["HTTP 接口"]
  n05ebd5bf["HTTP 接口/Handler"]
  na830a240["KeyActiveTaskFirst: active_task_first:task:%s"]
  ncb5ee46c["KeyAnchorCpGift: user_cp_gift:aid:%d"]
  nd324d0dd["KeyAnchorDayRank: anchor_day_rank:tab:%d:date:%s"]
  n69327c20["KeyAnchorGiftFirstRank: anchor_gift_first_rank"]
  n1e9d7ed8["KeyMedalAnchor: medal_anchor"]
  n479f5d61["KeyMedalTotal: medal_total"]
  n1143a4a5["KeyMedalUser: medal_user"]
  nf47cab19["KeyUserDayRank: user_day_rank:date:%s"]
  nc151207b["ModuleName: act202601_good_luck"]
  n82bfbb57["PrizeInfo"]
  n2102196f["Redis/状态 Key"]
  ne69ecd46["ReqBuyDrawBag"]
  n0874d5b2["ReqUserDraw"]
  n7ebf1f48["ResDrawPrize"]
  n2c47d69d["ResDrawPrizeLog"]
  n16eb613f["act202601"]
  n990896a1["act202601_good_luck"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n7643d9c0["git.inke.cn/opd/activitys/inke.activity.service/act"]
  n2eb4e126["git.inke.cn/opd/activitys/inke.activity.service/api/code"]
  n05487b5c["git.inke.cn/opd/activitys/inke.activity.service/dao"]
  n04a9e5ed["git.inke.cn/opd/activitys/inke.activity.service/model"]
  na3bdde25["git.inke.cn/opd/activitys/inke.activity.service/utils"]
  n0306c622["git.inke.cn/opd/activitys/inke.activity.service/utils/big_log"]
  nb2f14d27["handler: anchorDayRank"]
  na306a096["handler: cpTaskList"]
  nc00786b2["handler: dayTaskFirst"]
  nf534b047["handler: iTestWeb"]
  n68cbe357["handler: index"]
  nc2d5a20f["handler: interfaceConf"]
  ne5445ba9["handler: userDataLog"]
  n4693c645["handler: userDayRank"]
  n7cbd76cf["service: formatMsgContent"]
  n18e456b6["service: formatPrize"]
  n98d01bb2["service: getAnchorTab"]
  n7a2e36b4["service: getAnchorTaskTab"]
  nb3f11d03["service: jobAnchorDayRankTop"]
  nbd86d42c["service: jobUserDayRankTop"]
  n37d674eb["service: mascotGift"]
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
  n05ebd5bf --> na306a096
  n05ebd5bf --> nc00786b2
  n05ebd5bf --> nf534b047
  n05ebd5bf --> n68cbe357
  n05ebd5bf --> nc2d5a20f
  n05ebd5bf --> ne5445ba9
  n05ebd5bf --> n4693c645
  n2102196f --> na830a240
  n2102196f --> ncb5ee46c
  n2102196f --> nd324d0dd
  n2102196f --> n69327c20
  n2102196f --> n1e9d7ed8
  n2102196f --> n479f5d61
  n2102196f --> n1143a4a5
  n2102196f --> nf47cab19
  n990896a1 -- "exposes" --> n05ebd5bf
  n990896a1 -- "module" --> nc151207b
  n990896a1 -- "state" --> n2102196f
  n990896a1 -- "month" --> n16eb613f
  n990896a1 -- "uses" --> n099e1afb
  n990896a1 -- "defines" --> nde2f9a1b
  n990896a1 -- "imports" --> n50239d91
  n990896a1 -- "core" --> n5c886211
  n990896a1 -- "type" --> n5cbc9d99
  n990896a1 -- "type" --> n1b9349a8
  n990896a1 -- "type" --> n2bdbab4b
  n990896a1 -- "type" --> n57367205
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
  n5c886211 --> nbd86d42c
  n5c886211 --> n37d674eb
  n5c886211 --> na455f0b2
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/opd/activitys/inke.activity.service/act/2026/act202601/act202601_good_luck`
- 所属月份：`act202601`
- 活动类型判断：KA/SVIP 活动, 榜单冲榜, 任务/活跃, 用户侧活动
- ModuleName：`act202601_good_luck`
- README 摘要：无标题

```text
未发现 README 或 README 内容为空
```

## 静态结构画像
- 文本/代码文件数：9
- Go 文件数：9
- 文件类型分布：.go(9)

## 入口与接口
### 路由线索
- 未发现显式路由字符串，需结合活动总路由注册确认

### Handler 函数
- `index`
- `dayTaskFirst`
- `cpTaskList`
- `anchorDayRank`
- `userDayRank`
- `userDataLog`
- `interfaceConf`
- `iTestWeb`
- `iRecoverData`
- `iCronJob`
- `iBaseScore`
- `iDayFirst`
- `drawUserConf`
- `drawBuyBag`
- `drawPrize`
- `drawWebBroadcast`
- `drawPrizeLog`
- `icon`

## 核心业务逻辑
### service 方法
- `sendPrize`
- `formatMsgContent`
- `formatPrize`
- `getAnchorTab`
- `getAnchorTaskTab`
- `jobUserDayRankTop`
- `jobAnchorDayRankTop`
- `mascotGift`
- `setFirstActiveTask`
- `setFirstGiftScoreTask`
- `setCpActiveTask`
- `setCpGiftScoreTask`
- `getDayTaskFirst`
- `cpTaskAll`
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

### 业务能力信号
- 任务系统: 356 处信号
- 奖励发放/领奖: 309 处信号
- 排行榜: 182 处信号
- 日志/埋点: 137 处信号
- 缓存/Redis: 55 处信号
- 活动基础信息: 50 处信号
- 配置 JSON: 36 处信号
- HTTP 接口: 18 处信号
- 用户初始化/身份: 7 处信号

## 状态与缓存 Key
- `KeyAnchorDayRank` = `anchor_day_rank:tab:%d:date:%s`
- `KeyUserDayRank` = `user_day_rank:date:%s`
- `KeyAnchorGiftFirstRank` = `anchor_gift_first_rank`
- `KeyMedalTotal` = `medal_total`
- `KeyMedalUser` = `medal_user`
- `KeyMedalAnchor` = `medal_anchor`
- `KeyActiveTaskFirst` = `active_task_first:task:%s`
- `KeyAnchorCpGift` = `user_cp_gift:aid:%d`
- `KeyUserCpGift` = `user_cp_gift:uid:%d`
- `KeyAnchorCpWatch` = `user_cp_watch:aid:%d`
- `KeyUserCpWatch` = `user_cp_watch:uid:%d`
- `KeyAnchorCpTask` = `user_cp_task:aid:%d:task:%s`
- `KeyUserCpTask` = `user_cp_task:uid:%d:task:%s`
- `KeyAnchorCp` = `anchor_cp:aid:%d`
- `KeyUserCp` = `user_cp:uid:%d`
- `KeyAnchorDayTopPrize` = `anchor_day_top_prize_%d`
- `KeyUserDayTopPrize` = `user_day_top_prize`

## 模型与导出 API
- 导出结构体：DrawConf, DrawBag, DrawStyleConf, PrizeInfo, ReqUserDraw, ReqBuyDrawBag, ResDrawPrizeLog, ResDrawPrize, ResDrawLog, ReqDrawLog, Backend, Mascot, TUserInfo, UserDataLog
- 导出函数/方法：InitRoute, Cron, GiftHandle, RoomInOutHandle, FansJoinHandle, RoomLinkRelationHandle, NobleHandle

## 文件分层
- 任务逻辑: 9 个文件，示例：`server.go`, `service.go`, `internal.go`, `route.go`, `server_draw.go`, `cron.go`
- 配置/常量: 8 个文件，示例：`server.go`, `service.go`, `internal.go`, `route.go`, `server_draw.go`, `kafka.go`
- 工具辅助: 7 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_draw.go`, `cron.go`, `kafka.go`
- 模型结构: 7 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_draw.go`, `kafka.go`, `server_icon.go`
- 接口处理: 4 个文件，示例：`server.go`, `internal.go`, `server_draw.go`, `server_icon.go`
- 服务逻辑: 3 个文件，示例：`service.go`, `server_draw.go`, `server_icon.go`
- 入口/路由: 1 个文件，示例：`route.go`

## 内部依赖
- `git.inke.cn/opd/activitys/inke.activity.service/act`: 8
- `git.inke.cn/opd/activitys/inke.activity.service/dao`: 7
- `git.inke.cn/opd/activitys/inke.activity.service/utils`: 7
- `git.inke.cn/inkelogic/daenerys/http/server`: 5
- `git.inke.cn/opd/activitys/inke.activity.service/model`: 5
- `git.inke.cn/opd/activitys/inke.activity.service/api/code`: 4
- `git.inke.cn/BackendPlatform/golang/logging`: 3
- `git.inke.cn/opd/activitys/inke.activity.service/utils/big_log`: 2
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelTask`: 1
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
- `route.go`
- `server_draw.go`
- `cron.go`
- `kafka.go`
- `server_icon.go`
- `model.go`

## 阅读路径建议
- 先确认 `ModuleName` 与活动配置，活动时间、入口 URL、奖励配置通常通过 `act.Srv.GetActInfoByte` 或 `act.Srv.GetActBaseInfo` 获取。
- 再读 Handler 列表，按页面接口、榜单接口、任务接口、领奖接口拆分主流程。
- 重点跟踪 `Key*` 常量和 `act.Dao.GetKey`，它们通常对应 Redis 状态、榜单 ZSet、领奖锁和任务进度。
- 看到 `Claim`、`Prize`、`Reward`、`SendGift`、`AddBag` 相关代码时，优先核对幂等锁、活动时间校验和奖励次数限制。
