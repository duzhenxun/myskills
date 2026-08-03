# busi.gift.user_props_base 技术图谱

## 一图技术图谱
```mermaid
flowchart LR
  naa1df2ef["Daenerys 框架"]
  n8f718eeb["GORM"]
  na05476e7["GitLab CI"]
  n7c735559["HTTP/外部接口"]
  n51be25b0["Kafka"]
  n62a004b9["MySQL"]
  n8aa21d2e["RPC/IDL 调用"]
  ne1114467["Redis"]
  ndd2920c8["busi.gift.user_props_base"]
  ndff5ae75["dal/mysql/mysql.go"]
  n23ce3ead["dal/mysql/tb.go"]
  n8e951bae["dal/mysql/util.go"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  ne2260199["git.inke.cn/BackendPlatform/golang/trace"]
  n087ab18d["git.inke.cn/bpc/server/busi/busi.gift.user_props_base"]
  n7de617ec["git.inke.cn/bpc/server/sdk/commlib"]
  n10205f95["git.inke.cn/bpc/server/sdk/dq"]
  n0d851172["git.inke.cn/inkelogic/daenerys"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n8501d0ab["git.inke.cn/inkelogic/daenerys/proxy"]
  n2e573fd6["handler/add_prop_config.go"]
  neacee8ab["handler/add_user_prop.go"]
  n62161397["handler/add_user_prop_by_gift.go"]
  nd6693024["handler/add_users_prop_by_gift.go"]
  n9e43ce70["handler/add_users_prop_by_gift_async.go"]
  n20a313f2["model/const.go"]
  n8039464b["model/error_code.go"]
  nc31b8654["model/model.go"]
  n5a11e7c8["model/pb/prop.pb.go"]
  ne62ed39a["model/query_prop_record.go"]
  nf03d9c77["server/http/http.go"]
  n7cc1b88f["公司内部包"]
  nb682654e["外部依赖"]
  nadeed157["工程质量"]
  n8de19b79["接入层 HTTP/API"]
  n9bfbba5f["数据访问层"]
  ne9fe3e59["模型/DTO"]
  nfc56e941["领域: 礼物/打赏"]
  n8aa21d2e --> nf03d9c77
  ndd2920c8 -- "uses" --> n8aa21d2e
  ndd2920c8 -- "imports" --> n7cc1b88f
  ndd2920c8 -- "depends" --> nb682654e
  ndd2920c8 -- "quality" --> nadeed157
  ndd2920c8 -- "exposes" --> n8de19b79
  ndd2920c8 -- "persists" --> n9bfbba5f
  ndd2920c8 -- "defines" --> ne9fe3e59
  ndd2920c8 -- "domain" --> nfc56e941
  n7cc1b88f --> n7d7ea8b2
  n7cc1b88f --> ne2260199
  n7cc1b88f --> n087ab18d
  n7cc1b88f --> n7de617ec
  n7cc1b88f --> n10205f95
  n7cc1b88f --> n0d851172
  n7cc1b88f --> n7bacf918
  n7cc1b88f --> n8501d0ab
  nb682654e --> naa1df2ef
  nb682654e --> n8f718eeb
  nb682654e --> n7c735559
  nb682654e --> n51be25b0
  nb682654e --> n62a004b9
  nb682654e --> ne1114467
  nadeed157 --> na05476e7
  n8de19b79 --> n2e573fd6
  n8de19b79 --> neacee8ab
  n8de19b79 --> n62161397
  n8de19b79 --> nd6693024
  n8de19b79 --> n9e43ce70
  n9bfbba5f --> ndff5ae75
  n9bfbba5f --> n23ce3ead
  n9bfbba5f --> n8e951bae
  ne9fe3e59 --> n20a313f2
  ne9fe3e59 --> n8039464b
  ne9fe3e59 --> nc31b8654
  ne9fe3e59 --> n5a11e7c8
  ne9fe3e59 --> ne62ed39a
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/bpc/server/busi/busi.gift.user_props_base`
- 领域判断：礼物/打赏
- README 摘要：busi.gift.user_props_base

```text
# busi.gift.user_props_base
相关wiki：https://wiki.inkept.cn/pages/viewpage.action?pageId=71914166
道具库存服务
```

## 静态结构画像
- 文本/代码文件数：45
- Go 文件数：39
- 文件类型分布：.go(39), .toml(2), .md(1), .yml(1), .json(1), .proto(1)
- 顶层目录分布：handler(22), dal(7), model(6), app(4), server(2), backend(1), conf(1)

## 关键目录
- `handler`: 22 个文本/代码文件
- `dal`: 7 个文本/代码文件
- `model`: 6 个文本/代码文件
- `app`: 4 个文本/代码文件
- `server`: 2 个文本/代码文件
- `backend`: 1 个文本/代码文件
- `conf`: 1 个文本/代码文件

## 代码分层
- 接入层文件：20 个
- 服务层文件：0 个
- 数据访问文件：3 个
- 模型文件：5 个
- 任务/定时相关文件：0 个
- RPC/IDL 相关文件：1 个

## API/路由线索
- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认

## 核心类型与方法线索
- 导出结构体：AddUsersPropByGiftAsyncReq, BaseResp, StockItem, AddUsersPropByGiftReq, AddUsersPropByGiftResp, UserProp, KafkaMsg, GiftPropInfo, Stock, StockList, RdsDao, KafkaDao, PropConfig, PropRecord, PropRecordV2, UserProp, MysqlDao, Config
- 导出函数/方法：StartAddUsersPropAsync, AddUsersPropByGiftAsync, AdminQueryDetail, ConsumeUserPropByGift, GetPropRecords, QueryUserProp, UpdateUserPropsByReceivers, UpdateUserProps, RenewUserPropEndTime, SafeGiftID, CalStock, AddPropConfig, Error, Code, Message, Equal, QueryUserPropByGift, AddUserProp, AdminDelUserProp, ConsumeUserProp, GetPropTotalNum, GetPropConfig, RenewUserProp, GetConsumeSummary, AdminQueryUserProp, Init, SyncPropConfigTags, AddUserPropByGift, AddUsersPropByGift, Init

## 外部依赖线索
- Daenerys 框架: 26 处信号
- HTTP/外部接口: 21 处信号
- Kafka: 12 处信号
- MySQL: 11 处信号
- Redis: 4 处信号
- GORM: 2 处信号

## 内部依赖线索
- `git.inke.cn/bpc/server/busi/busi.gift.user_props_base`: 51
- `git.inke.cn/BackendPlatform/golang/logging`: 27
- `git.inke.cn/inkelogic/daenerys/http/server`: 20
- `git.inke.cn/bpc/server/sdk/commlib`: 6
- `git.inke.cn/BackendPlatform/golang/trace`: 4
- `git.inke.cn/bpc/server/sdk/dq`: 3
- `git.inke.cn/inkelogic/daenerys`: 3
- `git.inke.cn/inkelogic/daenerys/proxy`: 3
- `git.inke.cn/BackendPlatform/golang/safego`: 2
- `git.inke.cn/BackendPlatform/go-tools/cast`: 2
- `git.inke.cn/bpc/server/sdk/busi.gift.wall`: 1
- `git.inke.cn/bpc/server/sdk/room.action.base`: 1

## 第三方 import 概览
- github.com(18), go.uber.org(2), golang.org(2), os(2), unsafe(2), flag(1), log(1), syscall(1), io(1)

## IDL/协议文件
- `model/pb/prop.proto`

## 工程质量与交付
- GitLab CI：有
- golangci-lint：未发现
- 测试文件：
- 未发现 `_test.go`

## 阅读建议
- 先读 README 和 `server/http`、`handler`、`service` 目录，确认入口 API 与核心业务流程。
- 再沿服务层方法进入 DAO/Repo/Model，确认数据表、缓存 Key、RPC 调用和异步任务。
- 若图中只出现少量节点，通常表示该项目是配置型/胶水型服务，需结合上层共享工程和部署配置继续确认。
