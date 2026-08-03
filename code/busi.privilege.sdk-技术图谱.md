# busi.privilege.sdk 技术图谱

## 一图技术图谱
```mermaid
flowchart LR
  n7c735559["HTTP/外部接口"]
  n8aa21d2e["RPC/IDL 调用"]
  nd7cb63c5["busi.privilege.sdk"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  n320ab41e["git.inke.cn/bpc/server/busi/busi.privilege.base"]
  n961ac33a["git.inke.cn/inkelogic/rpc-go"]
  n2a2ffc87["src/sdk/agg/rpc.go"]
  n70c85682["src/sdk/fansclub/rpc.go"]
  n7cc1b88f["公司内部包"]
  nb682654e["外部依赖"]
  nfb754e86["领域: 权益/特权"]
  n8aa21d2e --> n2a2ffc87
  n8aa21d2e --> n70c85682
  nd7cb63c5 -- "uses" --> n8aa21d2e
  nd7cb63c5 -- "imports" --> n7cc1b88f
  nd7cb63c5 -- "depends" --> nb682654e
  nd7cb63c5 -- "domain" --> nfb754e86
  n7cc1b88f --> n7d7ea8b2
  n7cc1b88f --> n320ab41e
  n7cc1b88f --> n961ac33a
  nb682654e --> n7c735559
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/bpc/server/busi/busi.privilege.sdk`
- 领域判断：权益/特权
- README 摘要：busi.privilege.sdk

```text
# busi.privilege.sdk
```

## 静态结构画像
- 文本/代码文件数：5
- Go 文件数：4
- 文件类型分布：.go(4), .md(1)
- 顶层目录分布：src(4)

## 关键目录
- `src`: 4 个文本/代码文件

## 代码分层
- 接入层文件：0 个
- 服务层文件：0 个
- 数据访问文件：0 个
- 模型文件：0 个
- 任务/定时相关文件：0 个
- RPC/IDL 相关文件：2 个

## API/路由线索
- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认

## 核心类型与方法线索
- 导出结构体：未提取到导出结构体
- 导出函数/方法：ShowBatch, GetFansClubInfo, GetCommanderInfo

## 外部依赖线索
- HTTP/外部接口: 2 处信号

## 内部依赖线索
- `git.inke.cn/bpc/server/busi/busi.privilege.base`: 3
- `git.inke.cn/BackendPlatform/golang/logging`: 2
- `git.inke.cn/inkelogic/rpc-go`: 2

## 第三方 import 概览
- 主要为标准库/内部包

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
