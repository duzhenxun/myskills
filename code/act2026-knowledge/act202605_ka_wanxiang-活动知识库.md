# act202605_ka_wanxiang 活动项目知识库

## 一图知识图谱
```mermaid
flowchart LR
  n2e427c26["Backend"]
  nc00e2a7b["HTTP 接口"]
  n05ebd5bf["HTTP 接口/Handler"]
  n09f4a893["KeyDayPrize: day_prize:date:%s"]
  nd279f006["KeyUserActPayScore: user_act_pay_score"]
  nc1d8026e["KeyUserActTaskPrize: user_act_task_prize:task:%s"]
  n4f653631["KeyUserDayPayScore: user_day_pay_score:date:%s"]
  nf47cab19["KeyUserDayRank: user_day_rank:date:%s"]
  n18869b0f["KeyUserDayTaskPrize: user_day_task_prize:date:%s:task:%s"]
  n2d46d03c["KeyUserRank: user_rank"]
  n65702610["KeyUserSignTotal: user_sign_total"]
  n605eb0ec["ModuleName: act202605_ka_wanxiang"]
  n2102196f["Redis/状态 Key"]
  n581dac73["UserDataLog"]
  n135fa1ae["UserDayTaskInfo"]
  n77b2b14c["act202605"]
  n2ca289ef["act202605_ka_wanxiang"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n7643d9c0["git.inke.cn/opd/activitys/inke.activity.service/act"]
  n2eb4e126["git.inke.cn/opd/activitys/inke.activity.service/api/code"]
  n05487b5c["git.inke.cn/opd/activitys/inke.activity.service/dao"]
  n04a9e5ed["git.inke.cn/opd/activitys/inke.activity.service/model"]
  na3bdde25["git.inke.cn/opd/activitys/inke.activity.service/utils"]
  n0306c622["git.inke.cn/opd/activitys/inke.activity.service/utils/big_log"]
  n8e3d0c9d["handler: actTask"]
  ne3570145["handler: dayTask"]
  n09620d1b["handler: getActTaskPrize"]
  n55128f34["handler: getDayTaskPrize"]
  naa696be4["handler: getPrize"]
  n68cbe357["handler: index"]
  n4693c645["handler: userDayRank"]
  nbe4c9f5a["handler: userTask"]
  n7cbd76cf["service: formatMsgContent"]
  n18e456b6["service: formatPrize"]
  n9e7574da["service: getCanReceiveUserDayTask"]
  n28d7cc6e["service: getUserDayTaskList"]
  na455f0b2["service: sendPrize"]
  nb8e8a65e["service: sendUserDayTaskPrize"]
  ne7df0f70["service: setUserLoopTask"]
  n75c2b4ba["service: setUserSignTask"]
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
  n05ebd5bf --> n8e3d0c9d
  n05ebd5bf --> ne3570145
  n05ebd5bf --> n09620d1b
  n05ebd5bf --> n55128f34
  n05ebd5bf --> naa696be4
  n05ebd5bf --> n68cbe357
  n05ebd5bf --> n4693c645
  n05ebd5bf --> nbe4c9f5a
  n2102196f --> n09f4a893
  n2102196f --> nd279f006
  n2102196f --> nc1d8026e
  n2102196f --> n4f653631
  n2102196f --> nf47cab19
  n2102196f --> n18869b0f
  n2102196f --> n2d46d03c
  n2102196f --> n65702610
  n2ca289ef -- "exposes" --> n05ebd5bf
  n2ca289ef -- "module" --> n605eb0ec
  n2ca289ef -- "state" --> n2102196f
  n2ca289ef -- "month" --> n77b2b14c
  n2ca289ef -- "uses" --> n099e1afb
  n2ca289ef -- "defines" --> nde2f9a1b
  n2ca289ef -- "imports" --> n50239d91
  n2ca289ef -- "core" --> n5c886211
  n2ca289ef -- "type" --> n5cbc9d99
  n2ca289ef -- "type" --> n1b9349a8
  n2ca289ef -- "type" --> n2bdbab4b
  n2ca289ef -- "type" --> n57367205
  n099e1afb --> nc00e2a7b
  n099e1afb --> n88de2679
  n099e1afb --> n95b52d26
  n099e1afb --> n4a731954
  n099e1afb --> n33557018
  n099e1afb --> nd99a3a80
  n099e1afb --> n716e776e
  n099e1afb --> ndc861ff4
  nde2f9a1b --> n2e427c26
  nde2f9a1b --> n581dac73
  nde2f9a1b --> n135fa1ae
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
  n5c886211 --> n9e7574da
  n5c886211 --> n28d7cc6e
  n5c886211 --> na455f0b2
  n5c886211 --> nb8e8a65e
  n5c886211 --> ne7df0f70
  n5c886211 --> n75c2b4ba
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/opd/activitys/inke.activity.service/act/2026/act202605/act202605_ka_wanxiang`
- 所属月份：`act202605`
- 活动类型判断：KA/SVIP 活动, 榜单冲榜, 任务/活跃, 用户侧活动
- ModuleName：`act202605_ka_wanxiang`
- README 摘要：无标题

```text
未发现 README 或 README 内容为空
```

## 静态结构画像
- 文本/代码文件数：7
- Go 文件数：7
- 文件类型分布：.go(7)

## 入口与接口
### 路由线索
- 未发现显式路由字符串，需结合活动总路由注册确认

### Handler 函数
- `index`
- `getPrize`
- `userTask`
- `dayTask`
- `actTask`
- `getDayTaskPrize`
- `getActTaskPrize`
- `userDayRank`
- `userRank`
- `repSign`
- `userDataLog`
- `interfaceConf`
- `iExchange`
- `iTestWeb`
- `iRecoverData`
- `iCronJob`
- `iBaseScore`
- `iSign`
- `iDayTask`
- `iActTask`

## 核心业务逻辑
### service 方法
- `sendPrize`
- `formatMsgContent`
- `formatPrize`
- `setUserLoopTask`
- `setUserSignTask`
- `getUserDayTaskList`
- `getCanReceiveUserDayTask`
- `sendUserDayTaskPrize`
- `getUserActTaskList`
- `getCanReceiveUserActTask`
- `sendUserActTaskPrize`
- `jobUserDayTopRank`
- `jobUserEndRankTop`
- `jobUserAllRankPrize`

### 业务能力信号
- 任务系统: 329 处信号
- 排行榜: 164 处信号
- 奖励发放/领奖: 111 处信号
- 日志/埋点: 52 处信号
- 缓存/Redis: 51 处信号
- 活动基础信息: 30 处信号
- HTTP 接口: 20 处信号
- 配置 JSON: 7 处信号

## 状态与缓存 Key
- `KeyUserDayRank` = `user_day_rank:date:%s`
- `KeyUserRank` = `user_rank`
- `KeyDayPrize` = `day_prize:date:%s`
- `KeyUserDayPayScore` = `user_day_pay_score:date:%s`
- `KeyUserDayTaskPrize` = `user_day_task_prize:date:%s:task:%s`
- `KeyUserActPayScore` = `user_act_pay_score`
- `KeyUserActTaskPrize` = `user_act_task_prize:task:%s`
- `KeyUserSignTotal` = `user_sign_total`
- `KeyUserSignDate` = `user_sign:date:%s`
- `KeyUserSignUser` = `user_sign:user:%d`
- `KeyUserDayTop` = `user_day_top_prize`

## 模型与导出 API
- 导出结构体：Backend, UserDataLog, UserDayTaskInfo
- 导出函数/方法：InitRoute, Cron, RechargeHandle

## 文件分层
- 任务逻辑: 6 个文件，示例：`server.go`, `service.go`, `internal.go`, `route.go`, `cron.go`, `model.go`
- 工具辅助: 5 个文件，示例：`server.go`, `service.go`, `internal.go`, `cron.go`, `kafka.go`
- 模型结构: 5 个文件，示例：`server.go`, `service.go`, `internal.go`, `kafka.go`, `model.go`
- 配置/常量: 5 个文件，示例：`server.go`, `service.go`, `internal.go`, `route.go`, `model.go`
- 接口处理: 2 个文件，示例：`server.go`, `internal.go`
- 服务逻辑: 1 个文件，示例：`service.go`
- 入口/路由: 1 个文件，示例：`route.go`

## 内部依赖
- `git.inke.cn/opd/activitys/inke.activity.service/act`: 6
- `git.inke.cn/opd/activitys/inke.activity.service/utils`: 5
- `git.inke.cn/BackendPlatform/golang/logging`: 4
- `git.inke.cn/opd/activitys/inke.activity.service/dao`: 4
- `git.inke.cn/opd/activitys/inke.activity.service/model`: 4
- `git.inke.cn/inkelogic/daenerys/http/server`: 3
- `git.inke.cn/opd/activitys/inke.activity.service/api/code`: 2
- `git.inke.cn/opd/activitys/inke.activity.service/utils/big_log`: 2
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelTask`: 2
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRoom`: 1
- `git.inke.cn/BackendPlatform/golang/safego`: 1
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRank`: 1

## 第三方 import 概览
- github.com(2), bufio(1), os(1)

## 文件清单摘录
- `server.go`
- `service.go`
- `internal.go`
- `route.go`
- `cron.go`
- `kafka.go`
- `model.go`

## 阅读路径建议
- 先确认 `ModuleName` 与活动配置，活动时间、入口 URL、奖励配置通常通过 `act.Srv.GetActInfoByte` 或 `act.Srv.GetActBaseInfo` 获取。
- 再读 Handler 列表，按页面接口、榜单接口、任务接口、领奖接口拆分主流程。
- 重点跟踪 `Key*` 常量和 `act.Dao.GetKey`，它们通常对应 Redis 状态、榜单 ZSet、领奖锁和任务进度。
- 看到 `Claim`、`Prize`、`Reward`、`SendGift`、`AddBag` 相关代码时，优先核对幂等锁、活动时间校验和奖励次数限制。
