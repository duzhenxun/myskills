# busi.basic.commonpush 技术图谱

## 一图技术图谱
```mermaid
flowchart LR
  naa1df2ef["Daenerys 框架"]
  n45e23a16["Elasticsearch"]
  na05476e7["GitLab CI"]
  n7c735559["HTTP/外部接口"]
  n51be25b0["Kafka"]
  n8aa21d2e["RPC/IDL 调用"]
  ne1114467["Redis"]
  nd3cffdee["app/main.go"]
  n2b9935c2["busi.basic.commonpush"]
  n1a1f3e7a["daemon/daemon.go"]
  nb9b1545a["dao/dao.go"]
  nbfa5311d["git.inke.cn/BackendPlatform/go-tools/cast"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  nf5692187["git.inke.cn/bpc/server/busi/busi.basic.commonpush"]
  n7de617ec["git.inke.cn/bpc/server/sdk/commlib"]
  n58d5ea77["git.inke.cn/bpc/server/sdk/shanyin.server.serviceinfo"]
  n0d851172["git.inke.cn/inkelogic/daenerys"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n961ac33a["git.inke.cn/inkelogic/rpc-go"]
  n8077df92["manager/manager.go"]
  nc31b8654["model/model.go"]
  nbf35d2bc["model/redis_model/redis_model.go"]
  n2f0b062a["model/structs/structs.go"]
  nfa1b8922["server/http/handler.go"]
  nf03d9c77["server/http/http.go"]
  n6dfa5257["server/http/router.go"]
  ne4c912bb["server/http/send_push.go"]
  neeade751["service/service.go"]
  n182495e8["utils/ruquestUtils.go"]
  n888b7733["业务服务层"]
  n8d81b440["任务/定时处理"]
  n7cc1b88f["公司内部包"]
  nb682654e["外部依赖"]
  nadeed157["工程质量"]
  n8de19b79["接入层 HTTP/API"]
  n9bfbba5f["数据访问层"]
  ne9fe3e59["模型/DTO"]
  n5daeef3f["测试文件 1 个"]
  n71831234["领域: 基础服务"]
  n8aa21d2e --> n8077df92
  n8aa21d2e --> nbf35d2bc
  n8aa21d2e --> nf03d9c77
  n8aa21d2e --> n182495e8
  n2b9935c2 -- "uses" --> n8aa21d2e
  n2b9935c2 -- "core" --> n888b7733
  n2b9935c2 -- "schedules" --> n8d81b440
  n2b9935c2 -- "imports" --> n7cc1b88f
  n2b9935c2 -- "depends" --> nb682654e
  n2b9935c2 -- "quality" --> nadeed157
  n2b9935c2 -- "exposes" --> n8de19b79
  n2b9935c2 -- "persists" --> n9bfbba5f
  n2b9935c2 -- "defines" --> ne9fe3e59
  n2b9935c2 -- "domain" --> n71831234
  n888b7733 --> neeade751
  n8d81b440 --> nd3cffdee
  n8d81b440 --> n1a1f3e7a
  n8d81b440 --> neeade751
  n7cc1b88f --> nbfa5311d
  n7cc1b88f --> n7d7ea8b2
  n7cc1b88f --> nf5692187
  n7cc1b88f --> n7de617ec
  n7cc1b88f --> n58d5ea77
  n7cc1b88f --> n0d851172
  n7cc1b88f --> n7bacf918
  n7cc1b88f --> n961ac33a
  nb682654e --> naa1df2ef
  nb682654e --> n45e23a16
  nb682654e --> n7c735559
  nb682654e --> n51be25b0
  nb682654e --> ne1114467
  nadeed157 --> na05476e7
  nadeed157 --> n5daeef3f
  n8de19b79 --> nfa1b8922
  n8de19b79 --> nf03d9c77
  n8de19b79 --> n6dfa5257
  n8de19b79 --> ne4c912bb
  n9bfbba5f --> nb9b1545a
  ne9fe3e59 --> nc31b8654
  ne9fe3e59 --> nbf35d2bc
  ne9fe3e59 --> n2f0b062a
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/bpc/server/busi/busi.basic.commonpush`
- 领域判断：基础服务
- README 摘要：busi.basic.pc-p"***REDACTED***"

```text
# busi.basic.pc-p"***REDACTED***"
## 项目简介
## 配置说明
## CHANGELOG
aaaa
```

## 静态结构画像
- 文本/代码文件数：29
- Go 文件数：22
- 文件类型分布：.go(22), .md(2), .toml(2), .json(2), .yml(1)
- 顶层目录分布：app(4), server(4), utils(4), model(3), api(3), constants(2), manager(2), dao(1), docs(1), daemon(1)

## 关键目录
- `app`: 4 个文本/代码文件
- `server`: 4 个文本/代码文件
- `utils`: 4 个文本/代码文件
- `model`: 3 个文本/代码文件
- `api`: 3 个文本/代码文件
- `constants`: 2 个文本/代码文件
- `manager`: 2 个文本/代码文件
- `dao`: 1 个文本/代码文件
- `docs`: 1 个文本/代码文件
- `daemon`: 1 个文本/代码文件
- `service`: 1 个文本/代码文件
- `conf`: 1 个文本/代码文件

## 代码分层
- 接入层文件：4 个
- 服务层文件：1 个
- 数据访问文件：1 个
- 模型文件：3 个
- 任务/定时相关文件：3 个
- RPC/IDL 相关文件：4 个

## API/路由线索
- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认

## 核心类型与方法线索
- 导出结构体：Dao, SendType, SessionResp, Manager, Model, Atom, LiveStaticAtom, BaseResponse, SendPushResponse, Service, Config
- 导出函数/方法：GetErr, New, Ping, Close, GetRequestBody, JSON, Init, Shutdown, SendPush, SendPushOneTest, TestDingSign, CheckSession, CheckSessionRequest, CanPcPkInviteAccept, CanPcPkMatch, ReverseSidFunc, GetHeader, RSAEncrypt, RSADecrypt, DecodeQuery, StrToMd5, RsaDecrypt, GetUUID, HTTPGet, HTTPPost, DingDingEncodeSign, DecodeBody, New, Ping, Close

## 外部依赖线索
- HTTP/外部接口: 10 处信号
- Daenerys 框架: 7 处信号
- Redis: 4 处信号
- Elasticsearch: 2 处信号
- Kafka: 1 处信号

## 内部依赖线索
- `git.inke.cn/bpc/server/busi/busi.basic.commonpush`: 25
- `git.inke.cn/BackendPlatform/golang/logging`: 10
- `git.inke.cn/inkelogic/daenerys/http/server`: 4
- `git.inke.cn/inkelogic/daenerys`: 3
- `git.inke.cn/bpc/server/sdk/shanyin.server.serviceinfo`: 2
- `git.inke.cn/bpc/server/sdk/commlib`: 2
- `git.inke.cn/inkelogic/rpc-go`: 2
- `git.inke.cn/BackendPlatform/go-tools/cast`: 2
- `git.inke.cn/BackendPlatform/golang/redis`: 2
- `git.inke.cn/BackendPlatform/golang/safego`: 2
- `git.inke.cn/BackendPlatform/golang/ecode`: 2
- `git.inke.cn/inkelogic/daenerys/plugins/http`: 1

## 第三方 import 概览
- crypto(6), os(4), github.com(4), io(3), log(2), flag(1), syscall(1), testing(1), bytes(1)

## IDL/协议文件
- 未发现 proto/thrift 文件

## 工程质量与交付
- GitLab CI：有
- golangci-lint：未发现
- 测试文件：
- `utils/requestUtils_test.go`

## 阅读建议
- 先读 README 和 `server/http`、`handler`、`service` 目录，确认入口 API 与核心业务流程。
- 再沿服务层方法进入 DAO/Repo/Model，确认数据表、缓存 Key、RPC 调用和异步任务。
- 若图中只出现少量节点，通常表示该项目是配置型/胶水型服务，需结合上层共享工程和部署配置继续确认。
