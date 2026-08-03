# busi.basic.clientproxy 技术图谱

## 一图技术图谱
```mermaid
flowchart LR
  naa1df2ef["Daenerys 框架"]
  n7c735559["HTTP/外部接口"]
  n51be25b0["Kafka"]
  n8aa21d2e["RPC/IDL 调用"]
  n532e4d73["busi.basic.clientproxy"]
  nb9b1545a["dao/dao.go"]
  n63e74849["git.inke.cn/BackendPlatform/golang/ecode"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  nc0b15f0d["git.inke.cn/bpc/server/busi/busi.basic.clientproxy"]
  n0d851172["git.inke.cn/inkelogic/daenerys"]
  n0cea5f4d["git.inke.cn/inkelogic/daenerys/http/client"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  nd6b35b9f["git.inke.cn/inkelogic/daenerys/plugins/http"]
  n8077df92["manager/manager.go"]
  nc31b8654["model/model.go"]
  nfa1b8922["server/http/handler.go"]
  nf03d9c77["server/http/http.go"]
  n6dfa5257["server/http/router.go"]
  neeade751["service/service.go"]
  n888b7733["业务服务层"]
  n7cc1b88f["公司内部包"]
  nb682654e["外部依赖"]
  n8de19b79["接入层 HTTP/API"]
  n9bfbba5f["数据访问层"]
  ne9fe3e59["模型/DTO"]
  n71831234["领域: 基础服务"]
  n8aa21d2e --> n8077df92
  n8aa21d2e --> nf03d9c77
  n532e4d73 -- "uses" --> n8aa21d2e
  n532e4d73 -- "core" --> n888b7733
  n532e4d73 -- "imports" --> n7cc1b88f
  n532e4d73 -- "depends" --> nb682654e
  n532e4d73 -- "exposes" --> n8de19b79
  n532e4d73 -- "persists" --> n9bfbba5f
  n532e4d73 -- "defines" --> ne9fe3e59
  n532e4d73 -- "domain" --> n71831234
  n888b7733 --> neeade751
  n7cc1b88f --> n63e74849
  n7cc1b88f --> n7d7ea8b2
  n7cc1b88f --> nc0b15f0d
  n7cc1b88f --> n0d851172
  n7cc1b88f --> n0cea5f4d
  n7cc1b88f --> n7bacf918
  n7cc1b88f --> nd6b35b9f
  nb682654e --> naa1df2ef
  nb682654e --> n7c735559
  nb682654e --> n51be25b0
  n8de19b79 --> nfa1b8922
  n8de19b79 --> nf03d9c77
  n8de19b79 --> n6dfa5257
  n9bfbba5f --> nb9b1545a
  ne9fe3e59 --> nc31b8654
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/bpc/server/busi/busi.basic.clientproxy`
- 领域判断：基础服务
- README 摘要：busi.basic.clientproxy

```text
# busi.basic.clientproxy
## 项目简介
## 配置说明
## CHANGELOG
```

## 静态结构画像
- 文本/代码文件数：16
- Go 文件数：11
- 文件类型分布：.go(11), .md(2), .toml(2), .json(1)
- 顶层目录分布：app(4), server(3), manager(2), api(2), dao(1), model(1), service(1), conf(1)

## 关键目录
- `app`: 4 个文本/代码文件
- `server`: 3 个文本/代码文件
- `manager`: 2 个文本/代码文件
- `api`: 2 个文本/代码文件
- `dao`: 1 个文本/代码文件
- `model`: 1 个文本/代码文件
- `service`: 1 个文本/代码文件
- `conf`: 1 个文本/代码文件

## 代码分层
- 接入层文件：3 个
- 服务层文件：1 个
- 数据访问文件：1 个
- 模型文件：1 个
- 任务/定时相关文件：0 个
- RPC/IDL 相关文件：2 个

## API/路由线索
- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认

## 核心类型与方法线索
- 导出结构体：Dao, Manager, BaseResponse, Model, Service, Config
- 导出函数/方法：New, Ping, Close, Init, Shutdown, Push, New, Ping, Close, New, Ping, Close, Push, Init

## 外部依赖线索
- Daenerys 框架: 8 处信号
- HTTP/外部接口: 6 处信号
- Kafka: 1 处信号

## 内部依赖线索
- `git.inke.cn/bpc/server/busi/busi.basic.clientproxy`: 10
- `git.inke.cn/inkelogic/daenerys`: 4
- `git.inke.cn/BackendPlatform/golang/logging`: 3
- `git.inke.cn/inkelogic/daenerys/http/server`: 3
- `git.inke.cn/BackendPlatform/golang/ecode`: 2
- `git.inke.cn/inkelogic/daenerys/http/client`: 2
- `git.inke.cn/inkelogic/daenerys/plugins/http`: 1

## 第三方 import 概览
- os(2), bytes(2), flag(1), log(1), syscall(1), io(1)

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
