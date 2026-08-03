# busi.basic.smartrobot 技术图谱

## 一图技术图谱
```mermaid
flowchart LR
  naa1df2ef["Daenerys 框架"]
  n7c735559["HTTP/外部接口"]
  n51be25b0["Kafka"]
  n8aa21d2e["RPC/IDL 调用"]
  ne1114467["Redis"]
  nb9c84100["busi.basic.smartrobot"]
  nb9b1545a["dao/dao.go"]
  n61c084cc["dao/redis_dao.go"]
  nbfa5311d["git.inke.cn/BackendPlatform/go-tools/cast"]
  n63e74849["git.inke.cn/BackendPlatform/golang/ecode"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  nd6a47a81["git.inke.cn/bpc/server/busi/busi.basic.smartrobot"]
  n7de617ec["git.inke.cn/bpc/server/sdk/commlib"]
  n0d851172["git.inke.cn/inkelogic/daenerys"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n961ac33a["git.inke.cn/inkelogic/rpc-go"]
  n8077df92["manager/manager.go"]
  nc31b8654["model/model.go"]
  n4b0407a8["model/response_struct.go"]
  nfa1b8922["server/http/handler.go"]
  nf03d9c77["server/http/http.go"]
  n2bd9acfa["server/http/robot_callback.go"]
  n7cd406e3["server/http/robot_callback_test.go"]
  n6dfa5257["server/http/router.go"]
  n645e04df["service/dingding_srv.go"]
  n31d992b8["service/dingding_work_resp_srv/DingDingMarkDown.go"]
  nc6020aa5["service/dingding_work_resp_srv/DingDingText.go"]
  n28c51c9e["service/dingding_work_resp_srv/GetParamInterface.go"]
  na45f8c51["service/req_scene_srv/req_scenes/dt_scene/DtScene.go"]
  nfbee6997["service/req_scene_srv/req_scenes/help_scene/HelpScene.go"]
  nd78e28d8["service/req_scene_srv/req_scenes/room_scene/RoomScene.go"]
  n43d5acba["service/req_scene_srv/req_scenes/user_scene/UserScene.go"]
  n888b7733["业务服务层"]
  n7cc1b88f["公司内部包"]
  nb682654e["外部依赖"]
  nadeed157["工程质量"]
  n8de19b79["接入层 HTTP/API"]
  n9bfbba5f["数据访问层"]
  ne9fe3e59["模型/DTO"]
  ned98e090["测试文件 4 个"]
  n71831234["领域: 基础服务"]
  n8aa21d2e --> n61c084cc
  n8aa21d2e --> n8077df92
  n8aa21d2e --> nf03d9c77
  n8aa21d2e --> na45f8c51
  n8aa21d2e --> n43d5acba
  nb9c84100 -- "uses" --> n8aa21d2e
  nb9c84100 -- "core" --> n888b7733
  nb9c84100 -- "imports" --> n7cc1b88f
  nb9c84100 -- "depends" --> nb682654e
  nb9c84100 -- "quality" --> nadeed157
  nb9c84100 -- "exposes" --> n8de19b79
  nb9c84100 -- "persists" --> n9bfbba5f
  nb9c84100 -- "defines" --> ne9fe3e59
  nb9c84100 -- "domain" --> n71831234
  n888b7733 --> n645e04df
  n888b7733 --> n31d992b8
  n888b7733 --> nc6020aa5
  n888b7733 --> n28c51c9e
  n888b7733 --> na45f8c51
  n888b7733 --> nfbee6997
  n888b7733 --> nd78e28d8
  n7cc1b88f --> nbfa5311d
  n7cc1b88f --> n63e74849
  n7cc1b88f --> n7d7ea8b2
  n7cc1b88f --> nd6a47a81
  n7cc1b88f --> n7de617ec
  n7cc1b88f --> n0d851172
  n7cc1b88f --> n7bacf918
  n7cc1b88f --> n961ac33a
  nb682654e --> naa1df2ef
  nb682654e --> n7c735559
  nb682654e --> n51be25b0
  nb682654e --> ne1114467
  nadeed157 --> ned98e090
  n8de19b79 --> nfa1b8922
  n8de19b79 --> nf03d9c77
  n8de19b79 --> n2bd9acfa
  n8de19b79 --> n7cd406e3
  n8de19b79 --> n6dfa5257
  n9bfbba5f --> nb9b1545a
  n9bfbba5f --> n61c084cc
  ne9fe3e59 --> nc31b8654
  ne9fe3e59 --> n4b0407a8
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/bpc/server/busi/busi.basic.smartrobot`
- 领域判断：基础服务
- README 摘要：busi.basic.pc-p"***REDACTED***"

```text
# busi.basic.pc-p"***REDACTED***"
## 项目简介
## 配置说明
## CHANGELOG
```

## 静态结构画像
- 文本/代码文件数：57
- Go 文件数：50
- 文件类型分布：.go(50), .toml(3), .md(2), .json(2)
- 顶层目录分布：internal(12), service(11), server(7), app(6), utils(5), api(3), constants(2), dao(2), tests(2), model(2)

## 关键目录
- `internal`: 12 个文本/代码文件
- `service`: 11 个文本/代码文件
- `server`: 7 个文本/代码文件
- `app`: 6 个文本/代码文件
- `utils`: 5 个文本/代码文件
- `api`: 3 个文本/代码文件
- `constants`: 2 个文本/代码文件
- `dao`: 2 个文本/代码文件
- `tests`: 2 个文本/代码文件
- `model`: 2 个文本/代码文件
- `monitor`: 1 个文本/代码文件
- `docs`: 1 个文本/代码文件

## 代码分层
- 接入层文件：7 个
- 服务层文件：11 个
- 数据访问文件：2 个
- 模型文件：2 个
- 任务/定时相关文件：0 个
- RPC/IDL 相关文件：6 个

## API/路由线索
- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认

## 核心类型与方法线索
- 导出结构体：ReporterImpl, PathInfo, ProxyInfo, ProxyConfig, Dao, LogInfo, SessionManager, MessageHandler, CustomerService, Storage, SQLProxyFactory, SQLProxyForHTTP, SQLProxyForRedis, Session, Atom, SessionResp, Manager, Model, DingDingCallback, ReqActionInfo, RespActionDesc, RespSceneInfo, ApiIndexReq, BaseResponse, UserRoleInfo, UserLimitInfo, DeviceList, Service, DingDingMarkDownMsg, DingDingTextMsg
- 导出函数/方法：Report, Init, GetProxyInfoByPath, GetErr, RedisInit, GetRedis, RedisSetNxEx, RedisSetTabKey, RedisExists, New, Ping, Close, TestSid, PKCS5Padding, PKCS5UnPadding, DesDecrypt, DesEncrypt, TestName, TestRevertsid, TestDes, NewSessionManager, StartSession, GetCurrentSessionID, UpdateSessionTime, DeleteSession, NewMessageHandler, HandleMessage, InitializeCustomerService, InitializeCustomerService, NewCustomerService

## 外部依赖线索
- HTTP/外部接口: 18 处信号
- Daenerys 框架: 13 处信号
- Redis: 5 处信号
- Kafka: 1 处信号

## 内部依赖线索
- `git.inke.cn/bpc/server/busi/busi.basic.smartrobot`: 59
- `git.inke.cn/BackendPlatform/golang/logging`: 12
- `git.inke.cn/inkelogic/daenerys/http/server`: 7
- `git.inke.cn/inkelogic/daenerys`: 4
- `git.inke.cn/inkelogic/rpc-go`: 4
- `git.inke.cn/BackendPlatform/go-tools/cast`: 3
- `git.inke.cn/bpc/server/sdk/commlib`: 2
- `git.inke.cn/BackendPlatform/golang/ecode`: 2
- `git.inke.cn/inkelogic/daenerys/http/client`: 2
- `git.inke.cn/BackendPlatform/golang/trace`: 1
- `git.inke.cn/bpc/server/sdk/dingtoken`: 1
- `git.inke.cn/BackendPlatform/golang/redis`: 1

## 第三方 import 概览
- crypto(12), io(6), github.com(6), bytes(4), testing(4), os(3), mosn.io(1), flag(1), log(1), syscall(1)

## IDL/协议文件
- 未发现 proto/thrift 文件

## 工程质量与交付
- GitLab CI：未发现
- golangci-lint：未发现
- 测试文件：
- `tests/sid_test.go`
- `tests/phone_rsa_test.go`
- `server/http/robot_callback_test.go`
- `utils/requestUtils_test.go`

## 阅读建议
- 先读 README 和 `server/http`、`handler`、`service` 目录，确认入口 API 与核心业务流程。
- 再沿服务层方法进入 DAO/Repo/Model，确认数据表、缓存 Key、RPC 调用和异步任务。
- 若图中只出现少量节点，通常表示该项目是配置型/胶水型服务，需结合上层共享工程和部署配置继续确认。
