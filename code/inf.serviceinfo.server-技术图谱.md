# inf.serviceinfo.server 技术图谱

## 一图技术图谱
```mermaid
flowchart LR
  naa1df2ef["Daenerys 框架"]
  n8f718eeb["GORM"]
  n7c735559["HTTP/外部接口"]
  n51be25b0["Kafka"]
  n8aa21d2e["RPC/IDL 调用"]
  nb9b1545a["dao/dao.go"]
  n22e438b1["dao/model.go"]
  n9cfbf4bf["dao/sql.go"]
  n63e74849["git.inke.cn/BackendPlatform/golang/ecode"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  n2bce3bba["git.inke.cn/bpc/server/busi/inf.serviceinfo.server"]
  n0d851172["git.inke.cn/inkelogic/daenerys"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n8501d0ab["git.inke.cn/inkelogic/daenerys/proxy"]
  n86564f77["git.inke.cn/tpc/inf/metrics"]
  nac656e61["inf.serviceinfo.server"]
  n8077df92["manager/manager.go"]
  nc31b8654["model/model.go"]
  nfa1b8922["server/http/handler.go"]
  nf03d9c77["server/http/http.go"]
  nc6a345d7["server/http/response.go"]
  n6dfa5257["server/http/router.go"]
  nc79c2e2a["server/http/valid.go"]
  n387bb58d["service/backend.go"]
  neeade751["service/service.go"]
  n888b7733["业务服务层"]
  n8d81b440["任务/定时处理"]
  n7cc1b88f["公司内部包"]
  nb682654e["外部依赖"]
  n8de19b79["接入层 HTTP/API"]
  n9bfbba5f["数据访问层"]
  ne9fe3e59["模型/DTO"]
  n71831234["领域: 基础服务"]
  n8aa21d2e --> n8077df92
  n8aa21d2e --> nf03d9c77
  nac656e61 -- "uses" --> n8aa21d2e
  nac656e61 -- "core" --> n888b7733
  nac656e61 -- "schedules" --> n8d81b440
  nac656e61 -- "imports" --> n7cc1b88f
  nac656e61 -- "depends" --> nb682654e
  nac656e61 -- "exposes" --> n8de19b79
  nac656e61 -- "persists" --> n9bfbba5f
  nac656e61 -- "defines" --> ne9fe3e59
  nac656e61 -- "domain" --> n71831234
  n888b7733 --> n387bb58d
  n888b7733 --> neeade751
  n8d81b440 --> neeade751
  n7cc1b88f --> n63e74849
  n7cc1b88f --> n7d7ea8b2
  n7cc1b88f --> n2bce3bba
  n7cc1b88f --> n0d851172
  n7cc1b88f --> n7bacf918
  n7cc1b88f --> n8501d0ab
  n7cc1b88f --> n86564f77
  nb682654e --> naa1df2ef
  nb682654e --> n8f718eeb
  nb682654e --> n7c735559
  nb682654e --> n51be25b0
  n8de19b79 --> nfa1b8922
  n8de19b79 --> nf03d9c77
  n8de19b79 --> nc6a345d7
  n8de19b79 --> n6dfa5257
  n8de19b79 --> nc79c2e2a
  n9bfbba5f --> nb9b1545a
  n9bfbba5f --> n22e438b1
  n9bfbba5f --> n9cfbf4bf
  ne9fe3e59 --> nc31b8654
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/bpc/server/busi/inf.serviceinfo.server`
- 领域判断：基础服务
- README 摘要：inf.serviceinfo.server

```text
# inf.serviceinfo.server
## 项目简介
## 配置说明
## CHANGELOG
```

## 静态结构画像
- 文本/代码文件数：24
- Go 文件数：15
- 文件类型分布：.go(15), .toml(5), .md(2), .json(2)
- 顶层目录分布：app(7), server(5), dao(3), api(2), service(2), Godeps(1), manager(1), model(1), conf(1)

## 关键目录
- `app`: 7 个文本/代码文件
- `server`: 5 个文本/代码文件
- `dao`: 3 个文本/代码文件
- `api`: 2 个文本/代码文件
- `service`: 2 个文本/代码文件
- `Godeps`: 1 个文本/代码文件
- `manager`: 1 个文本/代码文件
- `model`: 1 个文本/代码文件
- `conf`: 1 个文本/代码文件

## 代码分层
- 接入层文件：5 个
- 服务层文件：2 个
- 数据访问文件：3 个
- 模型文件：1 个
- 任务/定时相关文件：1 个
- RPC/IDL 相关文件：2 个

## API/路由线索
- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认

## 核心类型与方法线索
- 导出结构体：ServiceInfoTable, ServiceInfo, Dao, Manager, Model, Atom, Location, VerifyRequest, VerifyStatus, VerifyResponse, ReviewData, AddRequest, BaseResponse, DelRequest, ListRequest, UpdateRequest, ServiceInfo, ServiceInfoResp, Service, Config
- 导出函数/方法：New, Ping, LoadAllReview, Close, AddServiceInfo, DelServiceInfo, UpdateServiceInfo, UpdateServiceInfoByLc, ListServiceInfo, JSONResponse, Init, Shutdown, New, IsUSAWhiteUser, GetLocation, Ping, Close, CreateAppleSandboxLc, DeleteAppleSandboxLc, PublishAppleSandboxLc, AddServiceInfo, DelServiceInfo, ListServiceInfo, UpdateServiceInfo, UpdateServiceInfoByLc, New, Verify, Ping, Close, Init

## 外部依赖线索
- Daenerys 框架: 9 处信号
- HTTP/外部接口: 7 处信号
- GORM: 3 处信号
- Kafka: 1 处信号

## 内部依赖线索
- `git.inke.cn/bpc/server/busi/inf.serviceinfo.server`: 23
- `git.inke.cn/BackendPlatform/golang/logging`: 7
- `git.inke.cn/inkelogic/daenerys/http/server`: 4
- `git.inke.cn/inkelogic/daenerys`: 3
- `git.inke.cn/BackendPlatform/golang/ecode`: 3
- `git.inke.cn/inkelogic/daenerys/proxy`: 2
- `git.inke.cn/tpc/inf/metrics`: 1

## 第三方 import 概览
- github.com(4), os(2), flag(1), log(1), syscall(1)

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
