# busi.giftwall.live-resource 技术图谱

## 一图技术图谱
```mermaid
flowchart LR
  n239eb0f4["busi.giftwall.live-resource"]
  nfc56e941["领域: 礼物/打赏"]
  n239eb0f4 -- "domain" --> nfc56e941
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/bpc/server/busi/busi.giftwall.live-resource`
- 领域判断：礼物/打赏
- README 摘要：live_resource

```text
# live_resource
```

## 静态结构画像
- 文本/代码文件数：24
- Go 文件数：0
- 文件类型分布：.ini(16), .json(3), .toml(3), .md(1), .proto(1)
- 顶层目录分布：etc(21), src(2)

## 关键目录
- `etc`: 21 个文本/代码文件
- `src`: 2 个文本/代码文件

## 代码分层
- 接入层文件：0 个
- 服务层文件：0 个
- 数据访问文件：0 个
- 模型文件：0 个
- 任务/定时相关文件：0 个
- RPC/IDL 相关文件：0 个

## API/路由线索
- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认

## 核心类型与方法线索
- 导出结构体：未提取到导出结构体
- 导出函数/方法：未提取到导出函数/方法

## 外部依赖线索
- 未发现明显中间件信号

## 内部依赖线索
- 未发现显著公司内部 import

## 第三方 import 概览
- 主要为标准库/内部包

## IDL/协议文件
- `src/protobuf/resource.proto`

## 工程质量与交付
- GitLab CI：未发现
- golangci-lint：未发现
- 测试文件：
- 未发现 `_test.go`

## 阅读建议
- 先读 README 和 `server/http`、`handler`、`service` 目录，确认入口 API 与核心业务流程。
- 再沿服务层方法进入 DAO/Repo/Model，确认数据表、缓存 Key、RPC 调用和异步任务。
- 若图中只出现少量节点，通常表示该项目是配置型/胶水型服务，需结合上层共享工程和部署配置继续确认。
