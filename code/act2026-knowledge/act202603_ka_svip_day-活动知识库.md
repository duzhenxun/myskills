# act202603_ka_svip_day 活动项目知识库

## 一图知识图谱
```mermaid
flowchart LR
  n2e427c26["Backend"]
  n2b70248f["DayPrizeConf"]
  nc00e2a7b["HTTP 接口"]
  n05ebd5bf["HTTP 接口/Handler"]
  n63a0f9f3["KeyBuyShopDayDiscount: KeyBuyShopDayDiscount:day_%s"]
  nf9ec604f["KeyBuyShopGoodsId: buy_shop_goods_user:goods_id:%s"]
  ndc3e1dab["KeyBuyShopGoodsUser: buy_shop_goods_user:uid:%d"]
  n42d9ff51["KeyGetPrize: get_prize"]
  nbbb7863a["KeyUserAllPay: user_all_pay"]
  n8d3e76d1["KeyUserDayPay: user_day_pay:date:%s"]
  neaad9150["KeyUserSignDate: user_sign:date:%s"]
  n65702610["KeyUserSignTotal: user_sign_total"]
  n9dbb7524["ModuleName: act202603_ka_svip_day"]
  n0da38ad5["PrizeShow"]
  n2102196f["Redis/状态 Key"]
  n3d5d5c1c["ShopGoods"]
  n48149cf0["ShopGoodsLog"]
  n922fc411["act202603"]
  n96656dd2["act202603_ka_svip_day"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n7643d9c0["git.inke.cn/opd/activitys/inke.activity.service/act"]
  n2eb4e126["git.inke.cn/opd/activitys/inke.activity.service/api/code"]
  n05487b5c["git.inke.cn/opd/activitys/inke.activity.service/dao"]
  n04a9e5ed["git.inke.cn/opd/activitys/inke.activity.service/model"]
  na3bdde25["git.inke.cn/opd/activitys/inke.activity.service/utils"]
  n0306c622["git.inke.cn/opd/activitys/inke.activity.service/utils/big_log"]
  naa696be4["handler: getPrize"]
  n05a7ed6c["handler: getVipPrize"]
  n4abc26ec["handler: iRecoverData"]
  neb00f5ba["handler: iShop"]
  nf534b047["handler: iTestWeb"]
  n68cbe357["handler: index"]
  nc2d5a20f["handler: interfaceConf"]
  nd70808a9["handler: prizeList"]
  n04abfd57["service: addShopTicket"]
  n7cbd76cf["service: formatMsgContent"]
  n18e456b6["service: formatPrize"]
  nc507a1df["service: getDayDiscountGoods"]
  nac546732["service: getPay23To26"]
  ndaa1c904["service: getShopTicket"]
  na455f0b2["service: sendPrize"]
  n5970d491["service: useShopTicket"]
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
  n05ebd5bf --> naa696be4
  n05ebd5bf --> n05a7ed6c
  n05ebd5bf --> n4abc26ec
  n05ebd5bf --> neb00f5ba
  n05ebd5bf --> nf534b047
  n05ebd5bf --> n68cbe357
  n05ebd5bf --> nc2d5a20f
  n05ebd5bf --> nd70808a9
  n2102196f --> n63a0f9f3
  n2102196f --> nf9ec604f
  n2102196f --> ndc3e1dab
  n2102196f --> n42d9ff51
  n2102196f --> nbbb7863a
  n2102196f --> n8d3e76d1
  n2102196f --> neaad9150
  n2102196f --> n65702610
  n96656dd2 -- "exposes" --> n05ebd5bf
  n96656dd2 -- "module" --> n9dbb7524
  n96656dd2 -- "state" --> n2102196f
  n96656dd2 -- "month" --> n922fc411
  n96656dd2 -- "uses" --> n099e1afb
  n96656dd2 -- "defines" --> nde2f9a1b
  n96656dd2 -- "imports" --> n50239d91
  n96656dd2 -- "core" --> n5c886211
  n96656dd2 -- "type" --> n5cbc9d99
  n96656dd2 -- "type" --> n1b9349a8
  n96656dd2 -- "type" --> n2bdbab4b
  n96656dd2 -- "type" --> n57367205
  n099e1afb --> nc00e2a7b
  n099e1afb --> n88de2679
  n099e1afb --> n95b52d26
  n099e1afb --> n4a731954
  n099e1afb --> n33557018
  n099e1afb --> nd99a3a80
  n099e1afb --> n716e776e
  n099e1afb --> ndc861ff4
  nde2f9a1b --> n2e427c26
  nde2f9a1b --> n2b70248f
  nde2f9a1b --> n0da38ad5
  nde2f9a1b --> n3d5d5c1c
  nde2f9a1b --> n48149cf0
  n50239d91 --> n7d7ea8b2
  n50239d91 --> n7bacf918
  n50239d91 --> n7643d9c0
  n50239d91 --> n2eb4e126
  n50239d91 --> n05487b5c
  n50239d91 --> n04a9e5ed
  n50239d91 --> na3bdde25
  n50239d91 --> n0306c622
  n5c886211 --> n04abfd57
  n5c886211 --> n7cbd76cf
  n5c886211 --> n18e456b6
  n5c886211 --> nc507a1df
  n5c886211 --> nac546732
  n5c886211 --> ndaa1c904
  n5c886211 --> na455f0b2
  n5c886211 --> n5970d491
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/opd/activitys/inke.activity.service/act/2026/act202603/act202603_ka_svip_day`
- 所属月份：`act202603`
- 活动类型判断：KA/SVIP 活动, 榜单冲榜, 任务/活跃, 用户侧活动
- ModuleName：`act202603_ka_svip_day`
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
- `getPrize`
- `prizeList`
- `getVipPrize`
- `interfaceConf`
- `iShop`
- `iTestWeb`
- `iRecoverData`
- `iCronJob`
- `iBaseScore`
- `iRecharge`
- `iLevel`
- `iExchange`
- `raftConf`
- `raftAssemble`
- `goodsList`
- `buyGoods`
- `userGoodsLog`
- `userRank`

## 核心业务逻辑
### service 方法
- `sendPrize`
- `formatMsgContent`
- `formatPrize`
- `addShopTicket`
- `getShopTicket`
- `useShopTicket`
- `getDayDiscountGoods`
- `getPay23To26`
- `isSurvivalUser`
- `getShopGoodsPrice`
- `jobRaftHourlyEnergy`
- `jobUserEndRankTop`
- `shopGoodsList`
- `shopGoodsInfo`
- `userBuyGoods`
- `setUserLoopTask`
- `setUserRoundTask`

### 业务能力信号
- 排行榜: 143 处信号
- 奖励发放/领奖: 110 处信号
- 任务系统: 79 处信号
- 缓存/Redis: 74 处信号
- 日志/埋点: 57 处信号
- 活动基础信息: 38 处信号
- 配置 JSON: 20 处信号
- HTTP 接口: 19 处信号

## 状态与缓存 Key
- `KeyBuyShopGoodsUser` = `buy_shop_goods_user:uid:%d`
- `KeyBuyShopDayDiscount` = `KeyBuyShopDayDiscount:day_%s`
- `KeyBuyShopGoodsId` = `buy_shop_goods_user:goods_id:%s`
- `KeyGetPrize` = `get_prize`
- `KeyUserDayPay` = `user_day_pay:date:%s`
- `KeyUserAllPay` = `user_all_pay`
- `KeyUserSignTotal` = `user_sign_total`
- `KeyUserSignDate` = `user_sign:date:%s`
- `KeyUserSignUser` = `user_sign:user:%d`
- `KeyOpenPrize` = `KeyOpenPrize`
- `KeyRaftPart` = `raft_part`
- `KeyUserRaftPartUsed` = `raft_part_used`
- `KeyUserShopTicket` = `user_shop_ticket:raft`
- `KeyUserShopTicketAll` = `user_shop_ticket_all:raft`
- `KeyUserDayDiscountUsed` = `raft_day_discount_used:uid:%d:date:%s`
- `KeyRaftEnergyCronHour` = `raft_energy_cron:hour_%s`
- `KeyUserSurvivalWatch` = `survival_watch:date:%s`
- `KeyUserSurvivalChat` = `survival_chat:date:%s`
- `KeyUserEndTopPrize` = `user_end_top_prize_%d`

## 模型与导出 API
- 导出结构体：ShopGoods, ShopGoodsLog, Backend, PrizeShow, DayPrizeConf
- 导出函数/方法：InitRoute, Cron, RechargeHandle, RoomInOutHandle, ChatHandle

## 文件分层
- 配置/常量: 9 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_raft.go`, `route.go`, `server_shop.go`
- 任务逻辑: 8 个文件，示例：`server.go`, `internal.go`, `route.go`, `cron.go`, `server_shop.go`, `kafka.go`
- 工具辅助: 8 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_raft.go`, `cron.go`, `server_shop.go`
- 模型结构: 8 个文件，示例：`server.go`, `service.go`, `internal.go`, `server_raft.go`, `server_shop.go`, `kafka.go`
- 接口处理: 5 个文件，示例：`server.go`, `internal.go`, `server_raft.go`, `server_shop.go`, `server_user_task.go`
- 服务逻辑: 3 个文件，示例：`service.go`, `server_shop.go`, `server_user_task.go`
- 入口/路由: 1 个文件，示例：`route.go`

## 内部依赖
- `git.inke.cn/opd/activitys/inke.activity.service/act`: 9
- `git.inke.cn/opd/activitys/inke.activity.service/dao`: 8
- `git.inke.cn/opd/activitys/inke.activity.service/model`: 8
- `git.inke.cn/opd/activitys/inke.activity.service/utils`: 8
- `git.inke.cn/inkelogic/daenerys/http/server`: 6
- `git.inke.cn/BackendPlatform/golang/logging`: 5
- `git.inke.cn/opd/activitys/inke.activity.service/api/code`: 4
- `git.inke.cn/opd/activitys/inke.activity.service/utils/big_log`: 3
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRoom`: 1
- `git.inke.cn/BackendPlatform/golang/safego`: 1
- `git.inke.cn/opd/activitys/inke.activity.service/model/modelRank`: 1

## 第三方 import 概览
- github.com(2), bufio(1), os(1)

## 文件清单摘录
- `server.go`
- `service.go`
- `internal.go`
- `raft_plan_1.md`
- `server_raft.go`
- `route.go`
- `cron.go`
- `server_shop.go`
- `kafka.go`
- `model.go`
- `server_user_task.go`

## 阅读路径建议
- 先确认 `ModuleName` 与活动配置，活动时间、入口 URL、奖励配置通常通过 `act.Srv.GetActInfoByte` 或 `act.Srv.GetActBaseInfo` 获取。
- 再读 Handler 列表，按页面接口、榜单接口、任务接口、领奖接口拆分主流程。
- 重点跟踪 `Key*` 常量和 `act.Dao.GetKey`，它们通常对应 Redis 状态、榜单 ZSet、领奖锁和任务进度。
- 看到 `Claim`、`Prize`、`Reward`、`SendGift`、`AddBag` 相关代码时，优先核对幂等锁、活动时间校验和奖励次数限制。
