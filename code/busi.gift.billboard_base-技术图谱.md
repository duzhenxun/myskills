# busi.gift.billboard_base 技术图谱

## 一图技术图谱
```mermaid
flowchart LR
  naa1df2ef["Daenerys 框架"]
  n8f718eeb["GORM"]
  n7c735559["HTTP/外部接口"]
  n51be25b0["Kafka"]
  n62a004b9["MySQL"]
  n8aa21d2e["RPC/IDL 调用"]
  ne1114467["Redis"]
  n07a5360c["busi.gift.billboard_base"]
  n5e3a3f46["dao/billboard_redis.go"]
  n63696167["dao/cache/cache.go"]
  nb1c6558f["dao/impl.go"]
  n705281cd["dao/init.go"]
  n6f520a6c["dao/mysql/mysql.go"]
  nab1f79fc["dao/mysql/tb.go"]
  ncfeb579d["dao/redis_proxy.go"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  na283f7b0["git.inke.cn/BackendPlatform/golang/redis"]
  ne2260199["git.inke.cn/BackendPlatform/golang/trace"]
  n9a7fab45["git.inke.cn/bpc/server/busi/busi.gift.billboard_base"]
  n0d851172["git.inke.cn/inkelogic/daenerys"]
  naba7309c["git.inke.cn/inkelogic/daenerys/config/encoder"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n8501d0ab["git.inke.cn/inkelogic/daenerys/proxy"]
  n86f93eb8["handler/anchor_contribution_mget.go"]
  n2f24233a["handler/contribution_update.go"]
  na8882322["handler/get_billboard_hide.go"]
  nbaaf5654["handler/get_billboard_info.go"]
  nb3384b3c["handler/get_billboard_list.go"]
  n20a313f2["model/const.go"]
  n8039464b["model/error_code.go"]
  nc31b8654["model/model.go"]
  nf03d9c77["server/http/http.go"]
  n7cc1b88f["公司内部包"]
  nb682654e["外部依赖"]
  n8de19b79["接入层 HTTP/API"]
  n9bfbba5f["数据访问层"]
  ne9fe3e59["模型/DTO"]
  n60c5380b["领域: 充值/计费支撑"]
  nfc56e941["领域: 礼物/打赏"]
  n8aa21d2e --> n5e3a3f46
  n8aa21d2e --> nf03d9c77
  n07a5360c -- "uses" --> n8aa21d2e
  n07a5360c -- "imports" --> n7cc1b88f
  n07a5360c -- "depends" --> nb682654e
  n07a5360c -- "exposes" --> n8de19b79
  n07a5360c -- "persists" --> n9bfbba5f
  n07a5360c -- "defines" --> ne9fe3e59
  n07a5360c -- "domain" --> n60c5380b
  n07a5360c -- "domain" --> nfc56e941
  n7cc1b88f --> n7d7ea8b2
  n7cc1b88f --> na283f7b0
  n7cc1b88f --> ne2260199
  n7cc1b88f --> n9a7fab45
  n7cc1b88f --> n0d851172
  n7cc1b88f --> naba7309c
  n7cc1b88f --> n7bacf918
  n7cc1b88f --> n8501d0ab
  nb682654e --> naa1df2ef
  nb682654e --> n8f718eeb
  nb682654e --> n7c735559
  nb682654e --> n51be25b0
  nb682654e --> n62a004b9
  nb682654e --> ne1114467
  n8de19b79 --> n86f93eb8
  n8de19b79 --> n2f24233a
  n8de19b79 --> na8882322
  n8de19b79 --> nbaaf5654
  n8de19b79 --> nb3384b3c
  n9bfbba5f --> n5e3a3f46
  n9bfbba5f --> n63696167
  n9bfbba5f --> nb1c6558f
  n9bfbba5f --> n705281cd
  n9bfbba5f --> n6f520a6c
  n9bfbba5f --> nab1f79fc
  n9bfbba5f --> ncfeb579d
  ne9fe3e59 --> n20a313f2
  ne9fe3e59 --> n8039464b
  ne9fe3e59 --> nc31b8654
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/bpc/server/busi/busi.gift.billboard_base`
- 领域判断：礼物/打赏, 充值/计费支撑
- README 摘要：busi.gift.billboard_base

```text
# busi.gift.billboard_base
榜单基础服务, 解决环调问题
```

## 静态结构画像
- 文本/代码文件数：34
- Go 文件数：30
- 文件类型分布：.go(30), .toml(2), .md(1), .json(1)
- 顶层目录分布：handler(12), dao(8), app(4), model(3), server(2), backend(2), util(1), conf(1)

## 关键目录
- `handler`: 12 个文本/代码文件
- `dao`: 8 个文本/代码文件
- `app`: 4 个文本/代码文件
- `model`: 3 个文本/代码文件
- `server`: 2 个文本/代码文件
- `backend`: 2 个文本/代码文件
- `util`: 1 个文本/代码文件
- `conf`: 1 个文本/代码文件

## 代码分层
- 接入层文件：12 个
- 服务层文件：0 个
- 数据访问文件：8 个
- 模型文件：3 个
- 任务/定时相关文件：0 个
- RPC/IDL 相关文件：2 个

## API/路由线索
- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认

## 核心类型与方法线索
- 导出结构体：AnchorContributionMGetReq, AnchorContributionMGetResp, Manager, ContributionUpdateReq, UserContributionMGetReq, UserContributionMGetResp, RedisPrefixProxy, PipelineProxy, UserContribution, AllBillboard, AllBillboardRecord, Mysql, Kafka, UpdateCacheTrigger, Context, BillboardList, ContributionInfo, LatestBillboard, BillboardRank, LatestBillboardPage, SendPropsKafkaMsg, RoomChatKafkaMsg, SendGiftKafkaMsg, Atom, Config
- 导出函数/方法：AnchorContributionMGet, GetLatestBillboardListTop, Check, GetBillboardListInfo, Work, UpdateBillboardInfo, ContributionUpdate, GetBillboardList, Check, UserContributionMGet, GetBillboardInfo, GetHideAll, GetLatestBillboardList, Check, Init, GetBillboardHide, SpanFromContext, GetLatestTimeUnit, GetLatestTimeUnitForRedis, GetLatestTimeUnitForMysql, GetHides, InitBillboardRds, GetBillboardList, GetHideAll, GetRank, IncrRank, IncrRankIncome, GetContribution, GetLatestBillboardTop, SetLatestBillboardTop

## 外部依赖线索
- Daenerys 框架: 18 处信号
- HTTP/外部接口: 16 处信号
- MySQL: 7 处信号
- Redis: 6 处信号
- GORM: 3 处信号
- Kafka: 3 处信号

## 内部依赖线索
- `git.inke.cn/bpc/server/busi/busi.gift.billboard_base`: 44
- `git.inke.cn/BackendPlatform/golang/logging`: 18
- `git.inke.cn/inkelogic/daenerys/http/server`: 14
- `git.inke.cn/inkelogic/daenerys`: 3
- `git.inke.cn/BackendPlatform/golang/redis`: 3
- `git.inke.cn/inkelogic/daenerys/proxy`: 3
- `git.inke.cn/BackendPlatform/golang/trace`: 3
- `git.inke.cn/inkelogic/daenerys/config/encoder`: 1
- `git.inke.cn/BackendPlatform/golang/safego`: 1
- `git.inke.cn/inkelogic/rpc-go`: 1
- `git.inke.cn/BackendPlatform/go-tools/cast`: 1
- `git.inke.cn/bpc/server/sdk/commlib`: 1

## 第三方 import 概览
- github.com(7), os(2), golang.org(1), flag(1), log(1), syscall(1), go.uber.org(1), reflect(1), io(1)

## IDL/协议文件
- 未发现 proto/thrift 文件

## 工程质量与交付
- GitLab CI：未发现
- golangci-lint：未发现
- 测试文件：
- 未发现 `_test.go`

## 阅读建议
- 先读 README 和 `server/http`、`handler`、`service` 目录，确认入口 API 与核心业务流程。
- 再沿服务层方法进入 DAO/Repo/Model，确认数据表、缓存 Key、RPC 调用和异步任务。
- 若图中只出现少量节点，通常表示该项目是配置型/胶水型服务，需结合上层共享工程和部署配置继续确认。
