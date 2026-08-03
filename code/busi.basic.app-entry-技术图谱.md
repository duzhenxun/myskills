# busi.basic.app-entry 技术图谱

## 一图技术图谱
```mermaid
flowchart LR
  naa1df2ef["Daenerys 框架"]
  na05476e7["GitLab CI"]
  n7c735559["HTTP/外部接口"]
  n51be25b0["Kafka"]
  n62a004b9["MySQL"]
  n8aa21d2e["RPC/IDL 调用"]
  ne1114467["Redis"]
  n7bf2a377["busi.basic.app-entry"]
  n75a82090["client/util.go"]
  nb9b1545a["dao/dao.go"]
  n63e74849["git.inke.cn/BackendPlatform/golang/ecode"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  na283f7b0["git.inke.cn/BackendPlatform/golang/redis"]
  nec5c5812["git.inke.cn/BackendPlatform/golang/sql"]
  n5d08dfd4["git.inke.cn/bpc/server/busi/busi.basic.app-entry"]
  n0d851172["git.inke.cn/inkelogic/daenerys"]
  n0cea5f4d["git.inke.cn/inkelogic/daenerys/http/client"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  n785fa441["handler/attraction.go"]
  n58781a3a["handler/entry_switch.go"]
  n733725f5["handler/main_test.go"]
  naf59ebef["handler/util.go"]
  n2500e56d["model/code.go"]
  nc31b8654["model/model.go"]
  nf03d9c77["server/http/http.go"]
  n8d81b440["任务/定时处理"]
  n7cc1b88f["公司内部包"]
  nb682654e["外部依赖"]
  nadeed157["工程质量"]
  n8de19b79["接入层 HTTP/API"]
  n9bfbba5f["数据访问层"]
  ne9fe3e59["模型/DTO"]
  n61bcdcb7["测试文件 5 个"]
  n71831234["领域: 基础服务"]
  n8aa21d2e --> n75a82090
  n8aa21d2e --> n733725f5
  n8aa21d2e --> nf03d9c77
  n7bf2a377 -- "uses" --> n8aa21d2e
  n7bf2a377 -- "schedules" --> n8d81b440
  n7bf2a377 -- "imports" --> n7cc1b88f
  n7bf2a377 -- "depends" --> nb682654e
  n7bf2a377 -- "quality" --> nadeed157
  n7bf2a377 -- "exposes" --> n8de19b79
  n7bf2a377 -- "persists" --> n9bfbba5f
  n7bf2a377 -- "defines" --> ne9fe3e59
  n7bf2a377 -- "domain" --> n71831234
  n8d81b440 --> n58781a3a
  n7cc1b88f --> n63e74849
  n7cc1b88f --> n7d7ea8b2
  n7cc1b88f --> na283f7b0
  n7cc1b88f --> nec5c5812
  n7cc1b88f --> n5d08dfd4
  n7cc1b88f --> n0d851172
  n7cc1b88f --> n0cea5f4d
  n7cc1b88f --> n7bacf918
  nb682654e --> naa1df2ef
  nb682654e --> n7c735559
  nb682654e --> n51be25b0
  nb682654e --> n62a004b9
  nb682654e --> ne1114467
  nadeed157 --> na05476e7
  nadeed157 --> n61bcdcb7
  n8de19b79 --> n785fa441
  n8de19b79 --> n58781a3a
  n8de19b79 --> n733725f5
  n8de19b79 --> naf59ebef
  n8de19b79 --> nc31b8654
  n9bfbba5f --> nb9b1545a
  ne9fe3e59 --> n2500e56d
  ne9fe3e59 --> nc31b8654
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/bpc/server/busi/busi.basic.app-entry`
- 领域判断：基础服务
- README 摘要：busi.basic.app-entry

```text
# busi.basic.app-entry
```

## 静态结构画像
- 文本/代码文件数：28
- Go 文件数：19
- 文件类型分布：.go(19), .json(4), .toml(3), .md(1), .yml(1)
- 顶层目录分布：handler(9), app(8), client(3), server(2), model(2), dao(1), conf(1)

## 关键目录
- `handler`: 9 个文本/代码文件
- `app`: 8 个文本/代码文件
- `client`: 3 个文本/代码文件
- `server`: 2 个文本/代码文件
- `model`: 2 个文本/代码文件
- `dao`: 1 个文本/代码文件
- `conf`: 1 个文本/代码文件

## 代码分层
- 接入层文件：7 个
- 服务层文件：0 个
- 数据访问文件：1 个
- 模型文件：2 个
- 任务/定时相关文件：1 个
- RPC/IDL 相关文件：3 个

## API/路由线索
- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认

## 核心类型与方法线索
- 导出结构体：EntrySwitchReqAtom, EntrySwitchReq, EntrySwitchResp, AttractionReq, Dao, Context, Config, CheckBigWithDrawResp, CheckModelWithDrawResp, BaseRes, FirstChargeCheckResp, FirstChargeRewardResp, ChargeReward, ChargePageShowResp
- 导出函数/方法：EntrySwitch, Init, TestHandlerbindResp, Attraction, TestHandlercheckAB, TestHandlercheckConfig, TestHandlercalCvValue, TestHandlerAttraction, TestHandlerEntrySwitch, TestHandlerappEntrySwitch, TestMain, New, Ping, Close, Init, Shutdown, NewContext, Init, CheckBigWithDraw, CheckModelWithDraw, HTTPGet, HTTPPost, FirstChargeCheck

## 外部依赖线索
- HTTP/外部接口: 11 处信号
- Daenerys 框架: 10 处信号
- Redis: 2 处信号
- MySQL: 1 处信号
- Kafka: 1 处信号

## 内部依赖线索
- `git.inke.cn/bpc/server/busi/busi.basic.app-entry`: 14
- `git.inke.cn/inkelogic/daenerys/http/server`: 6
- `git.inke.cn/BackendPlatform/golang/logging`: 5
- `git.inke.cn/inkelogic/daenerys`: 5
- `git.inke.cn/BackendPlatform/golang/ecode`: 2
- `git.inke.cn/inkelogic/daenerys/http/client`: 2
- `git.inke.cn/BackendPlatform/golang/redis`: 1
- `git.inke.cn/BackendPlatform/golang/sql`: 1
- `git.inke.cn/BackendPlatform/golang/kafka`: 1
- `git.inke.cn/BackendPlatform/golang/trace`: 1

## 第三方 import 概览
- testing(5), github.com(4), os(2), io(1), flag(1), log(1), syscall(1), bytes(1), runtime(1)

## IDL/协议文件
- 未发现 proto/thrift 文件

## 工程质量与交付
- GitLab CI：有
- golangci-lint：未发现
- 测试文件：
- `handler/util_test.go`
- `handler/logic_test.go`
- `handler/attraction_test.go`
- `handler/entry_switch_test.go`
- `handler/main_test.go`

## 阅读建议
- 先读 README 和 `server/http`、`handler`、`service` 目录，确认入口 API 与核心业务流程。
- 再沿服务层方法进入 DAO/Repo/Model，确认数据表、缓存 Key、RPC 调用和异步任务。
- 若图中只出现少量节点，通常表示该项目是配置型/胶水型服务，需结合上层共享工程和部署配置继续确认。
