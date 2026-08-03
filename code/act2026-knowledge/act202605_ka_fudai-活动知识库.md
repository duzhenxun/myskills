# act202605_ka_fudai 活动项目知识库

## 一图知识图谱
```mermaid
flowchart LR
  n2e427c26["Backend"]
  nc00e2a7b["HTTP 接口"]
  n05ebd5bf["HTTP 接口/Handler"]
  n8bd5600b["KeyUserBuyBagTime: user_buy_bag_time"]
  n0c82cc76["KeyUserGetGiftTime: user_get_gift_time"]
  n838b8d0e["KeyUserPayTime: user_pay_time"]
  n788b6bf2["KeyUserTime: user_time"]
  n76c0cadf["ModuleName: act202605_ka_fudai"]
  n2102196f["Redis/状态 Key"]
  n77b2b14c["act202605"]
  n33d2a09b["act202605_ka_fudai"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n7643d9c0["git.inke.cn/opd/activitys/inke.activity.service/act"]
  n2eb4e126["git.inke.cn/opd/activitys/inke.activity.service/api/code"]
  n05487b5c["git.inke.cn/opd/activitys/inke.activity.service/dao"]
  n04a9e5ed["git.inke.cn/opd/activitys/inke.activity.service/model"]
  na3bdde25["git.inke.cn/opd/activitys/inke.activity.service/utils"]
  n0306c622["git.inke.cn/opd/activitys/inke.activity.service/utils/big_log"]
  n038b3430["handler: buyBag"]
  n4b488b78["handler: getPayPrize"]
  na404601c["handler: iBaseScore"]
  n6bb23849["handler: iCronJob"]
  n4abc26ec["handler: iRecoverData"]
  nf534b047["handler: iTestWeb"]
  n68cbe357["handler: index"]
  nc2d5a20f["handler: interfaceConf"]
  n7cbd76cf["service: formatMsgContent"]
  n18e456b6["service: formatPrize"]
  n2c026a0d["service: getActUser"]
  n0b7077a3["service: getUserBuyBagTime"]
  naff6d79d["service: getUserGetGiftTime"]
  ncd395ad2["service: getUserPayTime"]
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
  n05ebd5bf --> n038b3430
  n05ebd5bf --> n4b488b78
  n05ebd5bf --> na404601c
  n05ebd5bf --> n6bb23849
  n05ebd5bf --> n4abc26ec
  n05ebd5bf --> nf534b047
  n05ebd5bf --> n68cbe357
  n05ebd5bf --> nc2d5a20f
  n2102196f --> n8bd5600b
  n2102196f --> n0c82cc76
  n2102196f --> n838b8d0e
  n2102196f --> n788b6bf2
  n33d2a09b -- "exposes" --> n05ebd5bf
  n33d2a09b -- "module" --> n76c0cadf
  n33d2a09b -- "state" --> n2102196f
  n33d2a09b -- "month" --> n77b2b14c
  n33d2a09b -- "uses" --> n099e1afb
  n33d2a09b -- "defines" --> nde2f9a1b
  n33d2a09b -- "imports" --> n50239d91
  n33d2a09b -- "core" --> n5c886211
  n33d2a09b -- "type" --> n5cbc9d99
  n33d2a09b -- "type" --> n1b9349a8
  n33d2a09b -- "type" --> n2bdbab4b
  n33d2a09b -- "type" --> n57367205
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
  n5c886211 --> n2c026a0d
  n5c886211 --> n0b7077a3
  n5c886211 --> naff6d79d
  n5c886211 --> ncd395ad2
  n5c886211 --> na455f0b2
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/opd/activitys/inke.activity.service/act/2026/act202605/act202605_ka_fudai`
- 所属月份：`act202605`
- 活动类型判断：KA/SVIP 活动, 榜单冲榜, 任务/活跃, 用户侧活动
- ModuleName：`act202605_ka_fudai`
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
- `buyBag`
- `getPayPrize`
- `interfaceConf`
- `iTestWeb`
- `iRecoverData`
- `iCronJob`
- `iBaseScore`
- `iUserTime`

## 核心业务逻辑
### service 方法
- `sendPrize`
- `formatMsgContent`
- `formatPrize`
- `getActUser`
- `getUserBuyBagTime`
- `getUserPayTime`
- `getUserGetGiftTime`

### 业务能力信号
- 排行榜: 35 处信号
- 奖励发放/领奖: 25 处信号
- 日志/埋点: 25 处信号
- 缓存/Redis: 21 处信号
- 活动基础信息: 19 处信号
- 配置 JSON: 14 处信号
- HTTP 接口: 9 处信号
- 任务系统: 2 处信号

## 状态与缓存 Key
- `KeyUserBuyBagTime` = `user_buy_bag_time`
- `KeyUserPayTime` = `user_pay_time`
- `KeyUserGetGiftTime` = `user_get_gift_time`
- `KeyUserTime` = `user_time`

## 模型与导出 API
- 导出结构体：Backend
- 导出函数/方法：InitRoute, RechargeHandle

## 文件分层
- 配置/常量: 6 个文件，示例：`server.go`, `service.go`, `internal.go`, `route.go`, `kafka.go`, `model.go`
- 模型结构: 5 个文件，示例：`server.go`, `service.go`, `internal.go`, `kafka.go`, `model.go`
- 工具辅助: 4 个文件，示例：`server.go`, `service.go`, `internal.go`, `kafka.go`
- 任务逻辑: 3 个文件，示例：`server.go`, `internal.go`, `route.go`
- 接口处理: 2 个文件，示例：`server.go`, `internal.go`
- 服务逻辑: 1 个文件，示例：`service.go`
- 入口/路由: 1 个文件，示例：`route.go`

## 内部依赖
- `git.inke.cn/opd/activitys/inke.activity.service/act`: 5
- `git.inke.cn/opd/activitys/inke.activity.service/model`: 4
- `git.inke.cn/opd/activitys/inke.activity.service/utils`: 4
- `git.inke.cn/BackendPlatform/golang/logging`: 3
- `git.inke.cn/inkelogic/daenerys/http/server`: 3
- `git.inke.cn/opd/activitys/inke.activity.service/api/code`: 2
- `git.inke.cn/opd/activitys/inke.activity.service/dao`: 2
- `git.inke.cn/opd/activitys/inke.activity.service/utils/big_log`: 1
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRoom`: 1
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
- `server_draw.go`
- `kafka.go`
- `model.go`

## 阅读路径建议
- 先确认 `ModuleName` 与活动配置，活动时间、入口 URL、奖励配置通常通过 `act.Srv.GetActInfoByte` 或 `act.Srv.GetActBaseInfo` 获取。
- 再读 Handler 列表，按页面接口、榜单接口、任务接口、领奖接口拆分主流程。
- 重点跟踪 `Key*` 常量和 `act.Dao.GetKey`，它们通常对应 Redis 状态、榜单 ZSet、领奖锁和任务进度。
- 看到 `Claim`、`Prize`、`Reward`、`SendGift`、`AddBag` 相关代码时，优先核对幂等锁、活动时间校验和奖励次数限制。
