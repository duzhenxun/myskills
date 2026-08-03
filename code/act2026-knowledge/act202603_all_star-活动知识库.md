# act202603_all_star 活动项目知识库

## 一图知识图谱
```mermaid
flowchart LR
  n2e427c26["Backend"]
  nc423e99c["BaseAnchorInfo"]
  neefefcbe["EmailStruct"]
  n40c88742["FriendsInfo"]
  n0452179d["GuildInfo"]
  nc00e2a7b["HTTP 接口"]
  n05ebd5bf["HTTP 接口/Handler"]
  n3d4e82ab["InitPartUser"]
  nd324d0dd["KeyAnchorDayRank: anchor_day_rank:tab:%d:date:%s"]
  n83aee5e5["KeyAnchorRank: anchor_rank:tab:%d"]
  n04c071b7["KeyAnchorTab: anchor_tab"]
  ndb0cc0a6["KeyAnchorTask: anchor_task_%d"]
  nb3e23381["KeyAnchorTaskScore: anchor_task_score"]
  n26a30c2b["KeyAnchorTrack: anchor_track"]
  nf47cab19["KeyUserDayRank: user_day_rank:date:%s"]
  n2d46d03c["KeyUserRank: user_rank"]
  n0d414d7f["ModuleName: act202603_all_star"]
  n2102196f["Redis/状态 Key"]
  ne0846950["SubTaskInfo"]
  n922fc411["act202603"]
  naf90a2d9["act202603_all_star"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n7643d9c0["git.inke.cn/opd/activitys/inke.activity.service/act"]
  n05487b5c["git.inke.cn/opd/activitys/inke.activity.service/dao"]
  n04a9e5ed["git.inke.cn/opd/activitys/inke.activity.service/model"]
  nf98059d1["git.inke.cn/opd/activitys/inke.activity.service/model/modelRank"]
  na3bdde25["git.inke.cn/opd/activitys/inke.activity.service/utils"]
  n0306c622["git.inke.cn/opd/activitys/inke.activity.service/utils/big_log"]
  nf64fb8ae["handler: boostInfo"]
  n68cbe357["handler: index"]
  neb4de894["handler: invitation"]
  n3ed694c6["handler: invitationWill"]
  n939bd774["handler: liveSmallRank"]
  nca787c83["handler: part1TaskInfo"]
  n4709d15b["handler: teamSupport"]
  n95389c36["handler: test"]
  n7cbd76cf["service: formatMsgContent"]
  n18e456b6["service: formatPrize"]
  nd3e33175["service: getBaseAnchorTab"]
  n04154978["service: getNickAndPortrait"]
  nacb99d6a["service: indexGetAnchorTab"]
  na455f0b2["service: sendPrize"]
  n1ee0d6f2["service: setAnchorTab"]
  n099e1afb["业务能力信号"]
  n88de2679["任务系统"]
  n95b52d26["奖励发放/领奖"]
  n4a731954["排行榜"]
  n33557018["日志/埋点"]
  nde2f9a1b["模型/响应结构"]
  n50239d91["活动公共依赖"]
  nd99a3a80["活动基础信息"]
  n5c886211["活动服务逻辑"]
  n1b9349a8["类型: 任务/活跃"]
  n2bdbab4b["类型: 榜单冲榜"]
  nda238ed0["类型: 游戏玩法"]
  n538ab97d["类型: 节日/节点活动"]
  n716e776e["缓存/Redis"]
  ndc861ff4["配置 JSON"]
  n05ebd5bf --> nf64fb8ae
  n05ebd5bf --> n68cbe357
  n05ebd5bf --> neb4de894
  n05ebd5bf --> n3ed694c6
  n05ebd5bf --> n939bd774
  n05ebd5bf --> nca787c83
  n05ebd5bf --> n4709d15b
  n05ebd5bf --> n95389c36
  n2102196f --> nd324d0dd
  n2102196f --> n83aee5e5
  n2102196f --> n04c071b7
  n2102196f --> ndb0cc0a6
  n2102196f --> nb3e23381
  n2102196f --> n26a30c2b
  n2102196f --> nf47cab19
  n2102196f --> n2d46d03c
  naf90a2d9 -- "exposes" --> n05ebd5bf
  naf90a2d9 -- "module" --> n0d414d7f
  naf90a2d9 -- "state" --> n2102196f
  naf90a2d9 -- "month" --> n922fc411
  naf90a2d9 -- "uses" --> n099e1afb
  naf90a2d9 -- "defines" --> nde2f9a1b
  naf90a2d9 -- "imports" --> n50239d91
  naf90a2d9 -- "core" --> n5c886211
  naf90a2d9 -- "type" --> n1b9349a8
  naf90a2d9 -- "type" --> n2bdbab4b
  naf90a2d9 -- "type" --> nda238ed0
  naf90a2d9 -- "type" --> n538ab97d
  n099e1afb --> nc00e2a7b
  n099e1afb --> n88de2679
  n099e1afb --> n95b52d26
  n099e1afb --> n4a731954
  n099e1afb --> n33557018
  n099e1afb --> nd99a3a80
  n099e1afb --> n716e776e
  n099e1afb --> ndc861ff4
  nde2f9a1b --> n2e427c26
  nde2f9a1b --> nc423e99c
  nde2f9a1b --> neefefcbe
  nde2f9a1b --> n40c88742
  nde2f9a1b --> n0452179d
  nde2f9a1b --> n3d4e82ab
  nde2f9a1b --> ne0846950
  n50239d91 --> n7d7ea8b2
  n50239d91 --> n7bacf918
  n50239d91 --> n7643d9c0
  n50239d91 --> n05487b5c
  n50239d91 --> n04a9e5ed
  n50239d91 --> nf98059d1
  n50239d91 --> na3bdde25
  n50239d91 --> n0306c622
  n5c886211 --> n7cbd76cf
  n5c886211 --> n18e456b6
  n5c886211 --> nd3e33175
  n5c886211 --> n04154978
  n5c886211 --> nacb99d6a
  n5c886211 --> na455f0b2
  n5c886211 --> n1ee0d6f2
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/opd/activitys/inke.activity.service/act/2026/act202603/act202603_all_star`
- 所属月份：`act202603`
- 活动类型判断：游戏玩法, 榜单冲榜, 任务/活跃, 节日/节点活动
- ModuleName：`act202603_all_star`
- README 摘要：无标题

```text
未发现 README 或 README 内容为空
```

## 静态结构画像
- 文本/代码文件数：12
- Go 文件数：12
- 文件类型分布：.go(12)

## 入口与接口
### 路由线索
- 未发现显式路由字符串，需结合活动总路由注册确认

### Handler 函数
- `index`
- `part1TaskInfo`
- `teamSupport`
- `boostInfo`
- `invitation`
- `invitationWill`
- `test`
- `liveSmallRank`
- `liveTestRank`
- `interfaceConf`
- `iSendEff`
- `iSendNotice`
- `iImplodeUserList`
- `iTestWeb`
- `iRecoverData`
- `iSendPrize`
- `iBaseScore`
- `iChangeAnchorTab`
- `iMainPartRankScore`
- `iOutClear`
- `iPartyClear`
- `iImplodeGuild`
- `guestPart1promote`
- `guestPartConf`
- `guestPartRank`
- `anchorTask`
- `mainPartConf`
- `mainPartRank`
- `mainPart1promote`
- `icon`
- `userTask`
- `userActiveTask`

## 核心业务逻辑
### service 方法
- `sendPrize`
- `formatMsgContent`
- `formatPrize`
- `getNickAndPortrait`
- `indexGetAnchorTab`
- `getBaseAnchorTab`
- `getBaseAnchorTab`
- `setAnchorTab`
- `getAnchorTab`
- `getTabMap`
- `part1SignTask`
- `firstGift`
- `GetNextPartPrize`
- `sendEmail`
- `GetTopRankPrize`
- `setDieOutPartRankMap`
- `setDieOutPartRank`
- `setAnchorTask`
- `iSelectOpt`
- `getMainTabMap`
- `getPartTabMap`
- `getGuestTabMap`
- `getTrackMap`
- `getGuestTrackMap`
- `setAnchorTrack`
- `getAnchorTrack`
- `getDieOutPartRankMap`
- `getDieOutPartRankList`
- `getDieOutPartRank`
- `checkMoveUp`
- `checkDieOut`
- `roomActRankInfo`
- `getLiveSmallRankData`
- `geTestRankData`
- `joinRoomPrize`
- `sendDingDing`
- `inheritScore`
- `relativesFriendsTask`
- `relativesGroupTask`
- `setGuestPartRank`
- `setGuestDayLoopTask`
- `setGuestNextPart1`
- `GuestAnchorPartNext`
- `guestCheckRankRiseProgress`
- `guestRankList`
- `setAnchorTaskScore`
- `getAnchorTaskScore`
- `setAnchorRoundTask`
- `setLevelTask`
- `mainRankList`
- `setMainDayLoopTask`
- `setMainPartRank`
- `MainAnchorPartNext`
- `setMainNextPart1`
- `getIcon1Data`
- `getIcon2Data`
- `getIcon12DataPart1`
- `getIcon17DataPart1`
- `getIcon12DataA`
- `getIcon12DataB`
- `getIcon7DataA`
- `getUserTaskScore`
- `setUserTaskScore`
- `setUserTask`
- `setUserTask2`
- `setUserRoundTask`
- `setUserLoopTask`
- `getScoreDiffRound`
- `setUserActiveTask`

### 业务能力信号
- 排行榜: 819 处信号
- 任务系统: 572 处信号
- 缓存/Redis: 256 处信号
- 日志/埋点: 194 处信号
- 奖励发放/领奖: 144 处信号
- 活动基础信息: 69 处信号
- 配置 JSON: 53 处信号
- HTTP 接口: 32 处信号
- 用户初始化/身份: 24 处信号

## 状态与缓存 Key
- `KeyAnchorTask` = `anchor_task_%d`
- `KeyAnchorTaskScore` = `anchor_task_score`
- `KeyUserDayRank` = `user_day_rank:date:%s`
- `KeyUserRank` = `user_rank`
- `KeyAnchorDayRank` = `anchor_day_rank:tab:%d:date:%s`
- `KeyAnchorRank` = `anchor_rank:tab:%d`
- `KeyAnchorTab` = `anchor_tab`
- `KeyAnchorTrack` = `anchor_track`
- `KeySignTotalNum` = `sign_total_num`
- `KeyMainPartRank` = `main_part_rank:part:%d:sub:%d:tab:%d:track:%d`
- `KeyMainPartRankTmp` = `main_part_rank_tmp:part:%d:sub:%d:tab:%d:track:%d`
- `KeyMainPartTmpRank` = `KeyMainPartTmpRank:part:%d:sub:%d:tab:%d:track:%d`
- `KeyPartBaseScore` = `part_base_score:part:%d:sub:%d`
- `KeyBroadcast` = `broadcast:part:%d:tab:%d`
- `KeyMoveUpTaskScore` = `KeyMoveUpTaskScore:tab:%d:track:%d:aid:%d`
- `KeyMoveUp` = `move_up:part:%d:tab:%d:track:%d`
- `KeyMoveUpTotal` = `move_up_total:part:%d:tab:%d:track:%d`
- `KeyTaskUpRank` = `KeyTaskUpRank`
- `KeyDieOutHash` = `die_out_map:part:%d:tab:%d:track:%d`
- `KeyDieOut` = `die_out:part:%d:tab:%d:track:%d`
- `KeyLoveGroup` = `love_group:tab:%d`
- `KeyLoveGroupLog` = `love_group_log:aid:%d`
- `KeyOpenGuard` = `open_guard:tab:%d`
- `KeyRankRadio` = `KeyRankRadio`
- `KeyPartTaskType` = `part_task_type:part:%d:tab:%d`
- `KeyAnchorPartTask` = `anchor_part_task:part:%d:tab:%d`
- `KeyGuildListInfo` = `guild_list_info`
- `KeyUserTaskScore` = `user_task_score`
- `KeyUserDayActiveTaskRound` = `user_active_task:task_key:%s:date:%s`

## 模型与导出 API
- 导出结构体：Backend, EmailStruct, BaseAnchorInfo, SubTaskInfo, FriendsInfo, InitPartUser, GuildInfo
- 导出函数/方法：GetNextPartPrize, GetTopRankPrize, GuestAnchorPartNext, InitRoute, Cron, MainAnchorPartNext, GiftHandle, RoomInOutHandle, FansJoinHandle, PrivilegeGuardNotify

## 文件分层
- 任务逻辑: 12 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_tab4.go`, `server_anchor_task.go`, `route.go`
- 配置/常量: 11 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_tab4.go`, `server_anchor_task.go`, `route.go`
- 工具辅助: 10 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_tab4.go`, `server_anchor_task.go`, `cron.go`
- 模型结构: 9 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_tab4.go`, `server_tab1_2.go`, `kafka.go`
- 接口处理: 7 个文件，示例：`server.go`, `internal.go`, `server_tab4.go`, `server_anchor_task.go`, `server_tab1_2.go`, `server_icon.go`
- 服务逻辑: 6 个文件，示例：`service.go`, `server_tab4.go`, `server_anchor_task.go`, `server_tab1_2.go`, `server_icon.go`, `server_user_task.go`
- 入口/路由: 1 个文件，示例：`route.go`

## 内部依赖
- `git.inke.cn/opd/activitys/inke.activity.service/act`: 11
- `git.inke.cn/opd/activitys/inke.activity.service/utils`: 10
- `git.inke.cn/opd/activitys/inke.activity.service/dao`: 9
- `git.inke.cn/BackendPlatform/golang/logging`: 8
- `git.inke.cn/inkelogic/daenerys/http/server`: 8
- `git.inke.cn/opd/activitys/inke.activity.service/model`: 8
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRank`: 5
- `git.inke.cn/opd/activitys/inke.activity.service/utils/big_log`: 5
- `git.inke.cn/opd/activitys/inke.activity.service/api/code`: 3
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRoom`: 2
- `git.inke.cn/opd/activitys/inke.activity.service/manager`: 1
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRoomActRank`: 1
- `git.inke.cn/BackendPlatform/golang/safego`: 1
- `git.inke.cn/opd/activitys/inke.activity.service/act/act_base`: 1
- `git.inke.cn/BackendPlatform/golang/trace`: 1
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelIcon`: 1

## 第三方 import 概览
- github.com(2), bufio(1), os(1)

## 文件清单摘录
- `server.go`
- `service.go`
- `internal.go`
- `server_tab4.go`
- `server_anchor_task.go`
- `route.go`
- `cron.go`
- `server_tab1_2.go`
- `kafka.go`
- `server_icon.go`
- `model.go`
- `server_user_task.go`

## 阅读路径建议
- 先确认 `ModuleName` 与活动配置，活动时间、入口 URL、奖励配置通常通过 `act.Srv.GetActInfoByte` 或 `act.Srv.GetActBaseInfo` 获取。
- 再读 Handler 列表，按页面接口、榜单接口、任务接口、领奖接口拆分主流程。
- 重点跟踪 `Key*` 常量和 `act.Dao.GetKey`，它们通常对应 Redis 状态、榜单 ZSet、领奖锁和任务进度。
- 看到 `Claim`、`Prize`、`Reward`、`SendGift`、`AddBag` 相关代码时，优先核对幂等锁、活动时间校验和奖励次数限制。
