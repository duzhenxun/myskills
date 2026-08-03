# busi.basic.survey 技术图谱

## 一图技术图谱
```mermaid
flowchart LR
  naa1df2ef["Daenerys 框架"]
  n8f718eeb["GORM"]
  n7c735559["HTTP/外部接口"]
  n51be25b0["Kafka"]
  n8aa21d2e["RPC/IDL 调用"]
  n5f882c3e["busi.basic.survey"]
  nb9b1545a["dao/dao.go"]
  n910f3129["dao/db/answer_info.go"]
  nf4036072["dao/db/db.go"]
  n76f54392["dao/db/question_info.go"]
  nd0468837["dao/db/survey_info.go"]
  n63e74849["git.inke.cn/BackendPlatform/golang/ecode"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  nec5c5812["git.inke.cn/BackendPlatform/golang/sql"]
  n7681bfc4["git.inke.cn/bpc/server/busi/busi.basic.survey"]
  n0d851172["git.inke.cn/inkelogic/daenerys"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  nd6b35b9f["git.inke.cn/inkelogic/daenerys/plugins/http"]
  n8501d0ab["git.inke.cn/inkelogic/daenerys/proxy"]
  n8077df92["manager/manager.go"]
  nc31b8654["model/model.go"]
  nfa1b8922["server/http/handler.go"]
  nf03d9c77["server/http/http.go"]
  n6dfa5257["server/http/router.go"]
  n426e0eef["service/index.go"]
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
  n8aa21d2e --> n426e0eef
  n5f882c3e -- "uses" --> n8aa21d2e
  n5f882c3e -- "core" --> n888b7733
  n5f882c3e -- "imports" --> n7cc1b88f
  n5f882c3e -- "depends" --> nb682654e
  n5f882c3e -- "exposes" --> n8de19b79
  n5f882c3e -- "persists" --> n9bfbba5f
  n5f882c3e -- "defines" --> ne9fe3e59
  n5f882c3e -- "domain" --> n71831234
  n888b7733 --> n426e0eef
  n888b7733 --> neeade751
  n7cc1b88f --> n63e74849
  n7cc1b88f --> n7d7ea8b2
  n7cc1b88f --> nec5c5812
  n7cc1b88f --> n7681bfc4
  n7cc1b88f --> n0d851172
  n7cc1b88f --> n7bacf918
  n7cc1b88f --> nd6b35b9f
  n7cc1b88f --> n8501d0ab
  nb682654e --> naa1df2ef
  nb682654e --> n8f718eeb
  nb682654e --> n7c735559
  nb682654e --> n51be25b0
  n8de19b79 --> nfa1b8922
  n8de19b79 --> nf03d9c77
  n8de19b79 --> n6dfa5257
  n8de19b79 --> n426e0eef
  n9bfbba5f --> nb9b1545a
  n9bfbba5f --> n910f3129
  n9bfbba5f --> nf4036072
  n9bfbba5f --> n76f54392
  n9bfbba5f --> nd0468837
  ne9fe3e59 --> nc31b8654
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/bpc/server/busi/busi.basic.survey`
- 领域判断：基础服务
- README 摘要：busi.basic.survey

```text
# busi.basic.survey
## 项目简介
## 配置说明
## CHANGELOG
```

## 静态结构画像
- 文本/代码文件数：21
- Go 文件数：16
- 文件类型分布：.go(16), .md(2), .toml(2), .json(1)
- 顶层目录分布：dao(5), app(4), server(3), manager(2), api(2), service(2), model(1), conf(1)

## 关键目录
- `dao`: 5 个文本/代码文件
- `app`: 4 个文本/代码文件
- `server`: 3 个文本/代码文件
- `manager`: 2 个文本/代码文件
- `api`: 2 个文本/代码文件
- `service`: 2 个文本/代码文件
- `model`: 1 个文本/代码文件
- `conf`: 1 个文本/代码文件

## 代码分层
- 接入层文件：4 个
- 服务层文件：2 个
- 数据访问文件：5 个
- 模型文件：1 个
- 任务/定时相关文件：0 个
- RPC/IDL 相关文件：3 个

## API/路由线索
- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认

## 核心类型与方法线索
- 导出结构体：Dao, Manager, Kafka, Model, AnswerRequest, AnswerContent, SchemaResponse, Option, Schema, SurveyInfo, QuestionInfo, AnswerInfo, FormKafka, Service, Config
- 导出函数/方法：New, Ping, Close, GetQuestionInfoInstance, GetQuestionInfo, GetAnswerInfoInstance, Create, AnsWerFind, NewDB, GetSurveyInfoInstance, GetSurveyInfo, Init, Shutdown, New, Ping, Close, NewKafka, AsyncSendMsg, Summit, Schema, Export, New, Ping, Close, Init

## 外部依赖线索
- Daenerys 框架: 8 处信号
- HTTP/外部接口: 7 处信号
- Kafka: 4 处信号
- GORM: 2 处信号

## 内部依赖线索
- `git.inke.cn/bpc/server/busi/busi.basic.survey`: 21
- `git.inke.cn/BackendPlatform/golang/logging`: 6
- `git.inke.cn/inkelogic/daenerys/http/server`: 4
- `git.inke.cn/inkelogic/daenerys`: 3
- `git.inke.cn/BackendPlatform/golang/sql`: 3
- `git.inke.cn/inkelogic/daenerys/plugins/http`: 1
- `git.inke.cn/inkelogic/daenerys/proxy`: 1
- `git.inke.cn/BackendPlatform/golang/ecode`: 1
- `git.inke.cn/inkelogic/rpc-go`: 1

## 第三方 import 概览
- github.com(3), os(2), flag(1), log(1), syscall(1), io(1), bytes(1)

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
