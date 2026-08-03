# busi.gift.billboard 技术图谱

## 一图技术图谱
```mermaid
flowchart LR
  n8f718eeb["GORM"]
  na05476e7["GitLab CI"]
  n7c735559["HTTP/外部接口"]
  n62a004b9["MySQL"]
  n8aa21d2e["RPC/IDL 调用"]
  ne1114467["Redis"]
  n4e96cf40["Thrift/RPC"]
  n248c384b["busi.gift.billboard"]
  nbfa5311d["git.inke.cn/BackendPlatform/go-tools/cast"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  na283f7b0["git.inke.cn/BackendPlatform/golang/redis"]
  ne2260199["git.inke.cn/BackendPlatform/golang/trace"]
  n71417069["git.inke.cn/BackendPlatform/golang/utils"]
  nb2b3e324["git.inke.cn/bpc/server/busi/busi.gift.billboard"]
  n4b12342d["git.inke.cn/bpc/server/sdk/user.subprofile.logic"]
  n961ac33a["git.inke.cn/inkelogic/rpc-go"]
  ne7b37ee1["golangci-lint"]
  n5a8f6730["src/api/statistic_info.go"]
  ne0e61aa0["src/billservice/Bill-consts.go"]
  nc03120c8["src/billservice/Bill.go"]
  n2fffb814["src/billservice/GoUnusedProtection__.go"]
  n08784306["src/cron/init.go"]
  nf4cfa0db["src/cron/super_gun.go"]
  n79ee049c["src/main.go"]
  n79a78224["src/model/config.go"]
  n833cb016["src/model/consts.go"]
  nf595388d["src/model/errors.go"]
  n18503eef["src/model/model.go"]
  n36736d1a["src/module/redis.go"]
  n8266c9ea["src/service/init.go"]
  n888b7733["业务服务层"]
  n8d81b440["任务/定时处理"]
  n7cc1b88f["公司内部包"]
  nb682654e["外部依赖"]
  nadeed157["工程质量"]
  n8de19b79["接入层 HTTP/API"]
  ne9fe3e59["模型/DTO"]
  n60c5380b["领域: 充值/计费支撑"]
  nfc56e941["领域: 礼物/打赏"]
  n8aa21d2e --> n5a8f6730
  n8aa21d2e --> ne0e61aa0
  n8aa21d2e --> nc03120c8
  n8aa21d2e --> n2fffb814
  n8aa21d2e --> n79ee049c
  n248c384b -- "uses" --> n8aa21d2e
  n248c384b -- "core" --> n888b7733
  n248c384b -- "schedules" --> n8d81b440
  n248c384b -- "imports" --> n7cc1b88f
  n248c384b -- "depends" --> nb682654e
  n248c384b -- "quality" --> nadeed157
  n248c384b -- "exposes" --> n8de19b79
  n248c384b -- "defines" --> ne9fe3e59
  n248c384b -- "domain" --> n60c5380b
  n248c384b -- "domain" --> nfc56e941
  n888b7733 --> n8266c9ea
  n8d81b440 --> n08784306
  n8d81b440 --> nf4cfa0db
  n8d81b440 --> n79ee049c
  n8d81b440 --> n833cb016
  n8d81b440 --> n36736d1a
  n7cc1b88f --> nbfa5311d
  n7cc1b88f --> n7d7ea8b2
  n7cc1b88f --> na283f7b0
  n7cc1b88f --> ne2260199
  n7cc1b88f --> n71417069
  n7cc1b88f --> nb2b3e324
  n7cc1b88f --> n4b12342d
  n7cc1b88f --> n961ac33a
  nb682654e --> n8f718eeb
  nb682654e --> n7c735559
  nb682654e --> n62a004b9
  nb682654e --> ne1114467
  nb682654e --> n4e96cf40
  nadeed157 --> na05476e7
  nadeed157 --> ne7b37ee1
  n8de19b79 --> n8266c9ea
  ne9fe3e59 --> n79a78224
  ne9fe3e59 --> n833cb016
  ne9fe3e59 --> nf595388d
  ne9fe3e59 --> n18503eef
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/bpc/server/busi/busi.gift.billboard`
- 领域判断：礼物/打赏, 充值/计费支撑
- README 摘要：无标题

```text
未发现 README 或 README 内容为空
```

## 静态结构画像
- 文本/代码文件数：64
- Go 文件数：57
- 文件类型分布：.go(57), .toml(3), .yml(2), .json(1), .thrift(1)
- 顶层目录分布：src(59), conf(3)

## 关键目录
- `src`: 59 个文本/代码文件
- `conf`: 3 个文本/代码文件

## 代码分层
- 接入层文件：1 个
- 服务层文件：1 个
- 数据访问文件：0 个
- 模型文件：4 个
- 任务/定时相关文件：5 个
- RPC/IDL 相关文件：18 个

## API/路由线索
- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认

## 核心类型与方法线索
- 导出结构体：AllContribution, HideBillBoardAdd, BaseDayBillBoard, MonthBillBoard, ContributorNumDayBillBoard, MysteryHideGet, AllBillBoard, BaseMonthBillBoard, InoutDayBillBoard, HideBillBoardDelete, BaseAllBillBoard, ContributionInfo, BaseLatestBillboardResp, InoutWeekBillBoard, BaseWeekBillBoard, DayContribution, MyThrift, WeekBillBoard, HideBillBoardGet, HideBillBoardGetResp, DayBillBoard, RedisPrefixProxy, PipelineProxy, BillThriftException, BillContent, GiftContent, SilverContent, SeqResult_, BillResult_, BalanceContent
- 导出函数/方法：Init, ProcessType, Process, IsPyramidAnchor, Init, ProcessType, Process, Init, ProcessType, Process, Init, ProcessType, Process, InitLocalCache, LocalCacheGetLiveIDByUID, LocalCacheSetLiveID, Init, ProcessType, Process, Init, ProcessType, Process, AddMedal, Init, ProcessType, Process, Init, ProcessType, Process, Init

## 外部依赖线索
- HTTP/外部接口: 25 处信号
- Redis: 12 处信号
- Thrift/RPC: 7 处信号
- GORM: 2 处信号
- MySQL: 1 处信号

## 内部依赖线索
- `git.inke.cn/bpc/server/busi/busi.gift.billboard`: 80
- `git.inke.cn/BackendPlatform/golang/logging`: 39
- `git.inke.cn/inkelogic/rpc-go`: 12
- `git.inke.cn/BackendPlatform/golang/redis`: 10
- `git.inke.cn/BackendPlatform/golang/utils`: 6
- `git.inke.cn/BackendPlatform/go-tools/cast`: 5
- `git.inke.cn/BackendPlatform/golang/trace`: 4
- `git.inke.cn/bpc/server/sdk/user.subprofile.logic`: 2
- `git.inke.cn/bpc/server/sdk/commconst`: 2
- `git.inke.cn/bpc/server/sdk/commlib`: 2
- `git.inke.cn/bpc/server/sdk/user.account.common_config`: 2
- `git.inke.cn/BackendPlatform/go-tools/req`: 2

## 第三方 import 概览
- golang.org(37), github.com(7), go.uber.org(4), bytes(3), reflect(2), git.apache.org(2), flag(1), os(1), io(1), database(1)

## IDL/协议文件
- `src/billservice/BillService.thrift`

## 工程质量与交付
- GitLab CI：有
- golangci-lint：有
- 测试文件：
- 未发现 `_test.go`

## 阅读建议
- 先读 README 和 `server/http`、`handler`、`service` 目录，确认入口 API 与核心业务流程。
- 再沿服务层方法进入 DAO/Repo/Model，确认数据表、缓存 Key、RPC 调用和异步任务。
- 若图中只出现少量节点，通常表示该项目是配置型/胶水型服务，需结合上层共享工程和部署配置继续确认。
