# busi.giftwall.live-resource-go 技术图谱

## 一图技术图谱
```mermaid
flowchart LR
  naa1df2ef["Daenerys 框架"]
  n7c735559["HTTP/外部接口"]
  n51be25b0["Kafka"]
  n8aa21d2e["RPC/IDL 调用"]
  ne1114467["Redis"]
  nfacd1ae1["busi.giftwall.live-resource-go"]
  nb9b1545a["dao/dao.go"]
  n17aa4db9["dao/redis.go"]
  nbfa5311d["git.inke.cn/BackendPlatform/go-tools/cast"]
  n63e74849["git.inke.cn/BackendPlatform/golang/ecode"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  n14b7f193["git.inke.cn/BackendPlatform/golang/safego"]
  ne4dbd1aa["git.inke.cn/bpc/server/busi/busi.giftwall.live-resource-go"]
  n7de617ec["git.inke.cn/bpc/server/sdk/commlib"]
  n0d851172["git.inke.cn/inkelogic/daenerys"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n8077df92["manager/manager.go"]
  nc31b8654["model/model.go"]
  n5a7e04f2["model/pb/resource.pb.go"]
  nfa1b8922["server/http/handler.go"]
  nfa9f5272["server/http/handler_api_resource.go"]
  nd15a7e8f["server/http/handler_difftest.go"]
  nf03d9c77["server/http/http.go"]
  n6dfa5257["server/http/router.go"]
  n387bb58d["service/backend.go"]
  neeade751["service/service.go"]
  nc6f9dcbc["service/service_api_resource.go"]
  n888b7733["业务服务层"]
  n8d81b440["任务/定时处理"]
  n7cc1b88f["公司内部包"]
  nb682654e["外部依赖"]
  n8de19b79["接入层 HTTP/API"]
  n9bfbba5f["数据访问层"]
  ne9fe3e59["模型/DTO"]
  nfc56e941["领域: 礼物/打赏"]
  n8aa21d2e --> n8077df92
  n8aa21d2e --> nf03d9c77
  nfacd1ae1 -- "uses" --> n8aa21d2e
  nfacd1ae1 -- "core" --> n888b7733
  nfacd1ae1 -- "schedules" --> n8d81b440
  nfacd1ae1 -- "imports" --> n7cc1b88f
  nfacd1ae1 -- "depends" --> nb682654e
  nfacd1ae1 -- "exposes" --> n8de19b79
  nfacd1ae1 -- "persists" --> n9bfbba5f
  nfacd1ae1 -- "defines" --> ne9fe3e59
  nfacd1ae1 -- "domain" --> nfc56e941
  n888b7733 --> n387bb58d
  n888b7733 --> neeade751
  n888b7733 --> nc6f9dcbc
  n8d81b440 --> n17aa4db9
  n8d81b440 --> n387bb58d
  n8d81b440 --> neeade751
  n8d81b440 --> nc6f9dcbc
  n7cc1b88f --> nbfa5311d
  n7cc1b88f --> n63e74849
  n7cc1b88f --> n7d7ea8b2
  n7cc1b88f --> n14b7f193
  n7cc1b88f --> ne4dbd1aa
  n7cc1b88f --> n7de617ec
  n7cc1b88f --> n0d851172
  n7cc1b88f --> n7bacf918
  nb682654e --> naa1df2ef
  nb682654e --> n7c735559
  nb682654e --> n51be25b0
  nb682654e --> ne1114467
  n8de19b79 --> nfa1b8922
  n8de19b79 --> nfa9f5272
  n8de19b79 --> nd15a7e8f
  n8de19b79 --> nf03d9c77
  n8de19b79 --> n6dfa5257
  n9bfbba5f --> nb9b1545a
  n9bfbba5f --> n17aa4db9
  ne9fe3e59 --> nc31b8654
  ne9fe3e59 --> n5a7e04f2
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/bpc/server/busi/busi.giftwall.live-resource-go`
- 领域判断：礼物/打赏
- README 摘要：busi.giftwall.live-resource-go

```text
# busi.giftwall.live-resource-go
旧礼物墙资源服务, go重写
```

## 静态结构画像
- 文本/代码文件数：23
- Go 文件数：17
- 文件类型分布：.go(17), .md(2), .toml(2), .json(1), .proto(1)
- 顶层目录分布：server(5), app(4), model(3), service(3), dao(2), api(2), backend(1), manager(1), conf(1)

## 关键目录
- `server`: 5 个文本/代码文件
- `app`: 4 个文本/代码文件
- `model`: 3 个文本/代码文件
- `service`: 3 个文本/代码文件
- `dao`: 2 个文本/代码文件
- `api`: 2 个文本/代码文件
- `backend`: 1 个文本/代码文件
- `manager`: 1 个文本/代码文件
- `conf`: 1 个文本/代码文件

## 代码分层
- 接入层文件：5 个
- 服务层文件：3 个
- 数据访问文件：2 个
- 模型文件：2 个
- 任务/定时相关文件：4 个
- RPC/IDL 相关文件：2 个

## API/路由线索
- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认

## 核心类型与方法线索
- 导出结构体：Dao, Manager, Gift, GiftResource, GiftIcon, RankResource, VerifiedResource, Service, Config
- 导出函数/方法：GetNessGiftResourceList, GetInUseGiftResourceIds, GetGiftResourceVersion, GetGiftResource, GetBundleResource, GetGiftBundleInfo, GetFeedsGiftInfo, GetGiftInfo, GetMultiPlayerGiftInfo, GetMultiEffectGiftInfo, GetVideoRewardGiftInfo, GetGiftDftSelect, GetGameGiftDftSelect, GetVideoClipsGiftDftSelect, GetGiftUpgradeInfo, GetGameGiftInfo, GetUserGiftInfo, GetRankResourceVersion, GetRankResource, GetVerifiedResourceVersion, GetVerifiedResource, GetVirtualResourceVersion, GetVirtualResource, GetCorrespondResource, GetLikeResource, GetGiftIconInfoVersion, GetGiftIconInfo, GetCommonPicResource, New, Ping

## 外部依赖线索
- Daenerys 框架: 8 处信号
- HTTP/外部接口: 7 处信号
- Redis: 2 处信号
- Kafka: 1 处信号

## 内部依赖线索
- `git.inke.cn/bpc/server/busi/busi.giftwall.live-resource-go`: 18
- `git.inke.cn/BackendPlatform/golang/logging`: 8
- `git.inke.cn/inkelogic/daenerys/http/server`: 5
- `git.inke.cn/inkelogic/daenerys`: 4
- `git.inke.cn/BackendPlatform/go-tools/cast`: 3
- `git.inke.cn/bpc/server/sdk/commlib`: 2
- `git.inke.cn/BackendPlatform/golang/safego`: 2
- `git.inke.cn/BackendPlatform/golang/ecode`: 2
- `git.inke.cn/BackendPlatform/golang/trace`: 2
- `git.inke.cn/BackendPlatform/golang/redis`: 1
- `git.inke.cn/inkelogic/daenerys/proxy`: 1
- `git.inke.cn/inkelogic/daenerys/plugins/http`: 1

## 第三方 import 概览
- github.com(4), os(2), go.uber.org(2), flag(1), log(1), syscall(1), bytes(1), crypto(1), io(1), reflect(1)

## IDL/协议文件
- `model/pb/resource.proto`

## 工程质量与交付
- GitLab CI：未发现
- golangci-lint：未发现
- 测试文件：
- 未发现 `_test.go`

## 阅读建议
- 先读 README 和 `server/http`、`handler`、`service` 目录，确认入口 API 与核心业务流程。
- 再沿服务层方法进入 DAO/Repo/Model，确认数据表、缓存 Key、RPC 调用和异步任务。
- 若图中只出现少量节点，通常表示该项目是配置型/胶水型服务，需结合上层共享工程和部署配置继续确认。
