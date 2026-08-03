# busi.sendgift.live-user-statistic 技术图谱

## 一图技术图谱
```mermaid
flowchart LR
  naa1df2ef["Daenerys 框架"]
  na05476e7["GitLab CI"]
  n7c735559["HTTP/外部接口"]
  n51be25b0["Kafka"]
  n8aa21d2e["RPC/IDL 调用"]
  ne1114467["Redis"]
  n4e96cf40["Thrift/RPC"]
  nb38bb925["busi.sendgift.live-user-statistic"]
  n63e74849["git.inke.cn/BackendPlatform/golang/ecode"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  n3f90e08f["git.inke.cn/bpc/server/busi/busi.sendgift.live-user-statistic"]
  n7de617ec["git.inke.cn/bpc/server/sdk/commlib"]
  n58d5ea77["git.inke.cn/bpc/server/sdk/shanyin.server.serviceinfo"]
  nbc9b0d20["git.inke.cn/bpc/server/sdk/user.base.risk-core"]
  n0d851172["git.inke.cn/inkelogic/daenerys"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n104ceb7d["src/client/billservice/Bill-consts.go"]
  n1dcb2bd9["src/client/billservice/Bill.go"]
  n3b4bdbdd["src/client/billservice/GoUnusedProtection__.go"]
  n2785ceef["src/client/privilege_common_test.go"]
  n4427e682["src/client/thrift.go"]
  n66cb3c7c["src/dal/redis/redis.go"]
  nbf9fedaa["src/handler/hide_status.go"]
  nf720eed9["src/handler/in_out.go"]
  nc36d10e1["src/handler/live_point_total_mget.go"]
  n3dd75958["src/handler/live_sender_point_total_mget.go"]
  n01af8c86["src/handler/live_sender_total_mget.go"]
  n7adb348d["src/handler/statistic_info.go"]
  n79ee049c["src/main.go"]
  n79a78224["src/model/config.go"]
  n95b15509["src/model/error_code.go"]
  n8d81b440["任务/定时处理"]
  n7cc1b88f["公司内部包"]
  nb682654e["外部依赖"]
  nadeed157["工程质量"]
  n8de19b79["接入层 HTTP/API"]
  ne9fe3e59["模型/DTO"]
  nda4751ff["测试文件 7 个"]
  nfc56e941["领域: 礼物/打赏"]
  n8aa21d2e --> n104ceb7d
  n8aa21d2e --> n1dcb2bd9
  n8aa21d2e --> n3b4bdbdd
  n8aa21d2e --> n2785ceef
  n8aa21d2e --> n4427e682
  nb38bb925 -- "uses" --> n8aa21d2e
  nb38bb925 -- "schedules" --> n8d81b440
  nb38bb925 -- "imports" --> n7cc1b88f
  nb38bb925 -- "depends" --> nb682654e
  nb38bb925 -- "quality" --> nadeed157
  nb38bb925 -- "exposes" --> n8de19b79
  nb38bb925 -- "defines" --> ne9fe3e59
  nb38bb925 -- "domain" --> nfc56e941
  n8d81b440 --> n66cb3c7c
  n8d81b440 --> n7adb348d
  n8d81b440 --> n79ee049c
  n7cc1b88f --> n63e74849
  n7cc1b88f --> n7d7ea8b2
  n7cc1b88f --> n3f90e08f
  n7cc1b88f --> n7de617ec
  n7cc1b88f --> n58d5ea77
  n7cc1b88f --> nbc9b0d20
  n7cc1b88f --> n0d851172
  n7cc1b88f --> n7bacf918
  nb682654e --> naa1df2ef
  nb682654e --> n7c735559
  nb682654e --> n51be25b0
  nb682654e --> ne1114467
  nb682654e --> n4e96cf40
  nadeed157 --> na05476e7
  nadeed157 --> nda4751ff
  n8de19b79 --> nbf9fedaa
  n8de19b79 --> nf720eed9
  n8de19b79 --> nc36d10e1
  n8de19b79 --> n3dd75958
  n8de19b79 --> n01af8c86
  ne9fe3e59 --> n79a78224
  ne9fe3e59 --> n95b15509
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/bpc/server/busi/busi.sendgift.live-user-statistic`
- 领域判断：礼物/打赏
- README 摘要：busi.sendgift.live-user-statistic

```text
# busi.sendgift.live-user-statistic
## 包括一些用户的信息
## todo ：迁移到用户组
统计服务
```

## 静态结构画像
- 文本/代码文件数：47
- Go 文件数：39
- 文件类型分布：.go(39), .toml(4), .md(1), .yml(1), .json(1), .thrift(1)
- 顶层目录分布：src(41), conf(4)

## 关键目录
- `src`: 41 个文本/代码文件
- `conf`: 4 个文本/代码文件

## 代码分层
- 接入层文件：14 个
- 服务层文件：0 个
- 数据访问文件：0 个
- 模型文件：2 个
- 任务/定时相关文件：3 个
- RPC/IDL 相关文件：13 个

## API/路由线索
- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认

## 核心类型与方法线索
- 导出结构体：Account, Description, Popups, LiveSenderTotalMGetReq, LiveSenderTotalMGetResp, InoutReq, InoutResp, Inout, LiveSenderPointTotalMGetReq, LiveSenderPointTotalMGetResp, LivePointTotalMGetReq, LivePointTotalMGetResp, GetRankInfoReq, GetRankInfoResp, SetBillboardInnerHideReq, InnerHideResp, SetBillboardHideReq, SetBillboardHideResp, SendGiftKafkaMsg, Config, RdsDao, HideStatusResult, CtrlConfDefault, BaseRes, GameCoinAccountResp, RespUserAccountData, UserRank, UserRankResp, UserRankInout, BalanceInputData
- 导出函数/方法：GetStatisticInfo, GetUserStatistic, LiveSenderTotalMGet, Check, GetInout, LiveSenderPointTotalMGet, LivePointTotalMGet, Check, GetRankInfo, TestGetUserStatistic, Check, SetBillboardInnerHide, GetHideStatus, GetStatisticInfoInner, RankShow, Check, SetBillboardHide, Init, Init, Shutdown, Init, Shutdown, InitConfig, Init, GetRds, NewRdsDao, SetBillboardHide, SetBillboardHideForScore, SetBillboardHideForScoreGlobal, BatchGetHideStatus

## 外部依赖线索
- HTTP/外部接口: 23 处信号
- Daenerys 框架: 20 处信号
- Thrift/RPC: 10 处信号
- Redis: 5 处信号
- Kafka: 1 处信号

## 内部依赖线索
- `git.inke.cn/bpc/server/busi/busi.sendgift.live-user-statistic`: 37
- `git.inke.cn/BackendPlatform/golang/logging`: 24
- `git.inke.cn/inkelogic/daenerys/http/server`: 14
- `git.inke.cn/inkelogic/daenerys`: 6
- `git.inke.cn/bpc/server/sdk/shanyin.server.serviceinfo`: 2
- `git.inke.cn/BackendPlatform/golang/ecode`: 2
- `git.inke.cn/bpc/server/sdk/commlib`: 1
- `git.inke.cn/bpc/server/sdk/user.base.risk-core`: 1
- `git.inke.cn/bpc/server/sdk/busi.gift.billboard_base`: 1
- `git.inke.cn/inkelogic/daenerys/config/encoder`: 1
- `git.inke.cn/bpc/server/sdk/busi.privilege.experiencecard`: 1
- `git.inke.cn/bpc/server/sdk/ik`: 1

## 第三方 import 概览
- github.com(9), testing(6), bytes(4), os(3), io(2), git.apache.org(2), flag(1), syscall(1), go.uber.org(1), runtime(1)

## IDL/协议文件
- `src/client/billservice/BillService.thrift`

## 工程质量与交付
- GitLab CI：有
- golangci-lint：未发现
- 测试文件：
- `src/handler/privilege_common_test.go`
- `src/handler/statistic_info_test.go`
- `src/client/thrift_test.go`
- `src/client/user_rank_logic_test.go`
- `src/client/privilege_common_test.go`
- `src/client/red_packet_test.go`
- `src/client/user_session_test.go`

## 阅读建议
- 先读 README 和 `server/http`、`handler`、`service` 目录，确认入口 API 与核心业务流程。
- 再沿服务层方法进入 DAO/Repo/Model，确认数据表、缓存 Key、RPC 调用和异步任务。
- 若图中只出现少量节点，通常表示该项目是配置型/胶水型服务，需结合上层共享工程和部署配置继续确认。
