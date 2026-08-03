# busi.authority.management 技术图谱

## 一图技术图谱
```mermaid
flowchart LR
  naa1df2ef["Daenerys 框架"]
  n8f718eeb["GORM"]
  na05476e7["GitLab CI"]
  n7c735559["HTTP/外部接口"]
  n8aa21d2e["RPC/IDL 调用"]
  ne1114467["Redis"]
  nec98ec8f["busi.authority.management"]
  neb500a02["dao/cache_permission.go"]
  n9cc5d5d9["dao/cache_role.go"]
  nb9b1545a["dao/dao.go"]
  ncaf40d13["dao/dao_permission.go"]
  nba40eacd["dao/dao_role.go"]
  n63e74849["git.inke.cn/BackendPlatform/golang/ecode"]
  n7d7ea8b2["git.inke.cn/BackendPlatform/golang/logging"]
  na283f7b0["git.inke.cn/BackendPlatform/golang/redis"]
  nec5c5812["git.inke.cn/BackendPlatform/golang/sql"]
  n355e612f["git.inke.cn/bpc/server/busi/busi.authority.management"]
  n0d851172["git.inke.cn/inkelogic/daenerys"]
  n7bacf918["git.inke.cn/inkelogic/daenerys/http/server"]
  ne7b37ee1["golangci-lint"]
  n4c455b19["model/base.go"]
  n20a313f2["model/const.go"]
  n42177425["model/dto/Permission.go"]
  n02d80a9c["model/dto/Role.go"]
  n8f24f4cb["model/dto/RolePermission.go"]
  nfa1b8922["server/http/handler.go"]
  nf03d9c77["server/http/http.go"]
  n6dfa5257["server/http/router.go"]
  neeade751["service/service.go"]
  n295456a4["service/service_permission.go"]
  n9c14b0fe["service/service_role.go"]
  n888b7733["业务服务层"]
  n7cc1b88f["公司内部包"]
  nb682654e["外部依赖"]
  nadeed157["工程质量"]
  n8de19b79["接入层 HTTP/API"]
  n9bfbba5f["数据访问层"]
  ne9fe3e59["模型/DTO"]
  nc1d8f75a["领域: 权限/管理后台"]
  n8aa21d2e --> nf03d9c77
  nec98ec8f -- "uses" --> n8aa21d2e
  nec98ec8f -- "core" --> n888b7733
  nec98ec8f -- "imports" --> n7cc1b88f
  nec98ec8f -- "depends" --> nb682654e
  nec98ec8f -- "quality" --> nadeed157
  nec98ec8f -- "exposes" --> n8de19b79
  nec98ec8f -- "persists" --> n9bfbba5f
  nec98ec8f -- "defines" --> ne9fe3e59
  nec98ec8f -- "domain" --> nc1d8f75a
  n888b7733 --> neeade751
  n888b7733 --> n295456a4
  n888b7733 --> n9c14b0fe
  n7cc1b88f --> n63e74849
  n7cc1b88f --> n7d7ea8b2
  n7cc1b88f --> na283f7b0
  n7cc1b88f --> nec5c5812
  n7cc1b88f --> n355e612f
  n7cc1b88f --> n0d851172
  n7cc1b88f --> n7bacf918
  nb682654e --> naa1df2ef
  nb682654e --> n8f718eeb
  nb682654e --> n7c735559
  nb682654e --> ne1114467
  nadeed157 --> na05476e7
  nadeed157 --> ne7b37ee1
  n8de19b79 --> nfa1b8922
  n8de19b79 --> nf03d9c77
  n8de19b79 --> n6dfa5257
  n9bfbba5f --> neb500a02
  n9bfbba5f --> n9cc5d5d9
  n9bfbba5f --> nb9b1545a
  n9bfbba5f --> ncaf40d13
  n9bfbba5f --> nba40eacd
  ne9fe3e59 --> n4c455b19
  ne9fe3e59 --> n20a313f2
  ne9fe3e59 --> n42177425
  ne9fe3e59 --> n02d80a9c
  ne9fe3e59 --> n8f24f4cb
```

## 项目定位
- 源码路径：`/Users/dds/go/src/git.inke.cn/bpc/server/busi/busi.authority.management`
- 领域判断：权限/管理后台
- README 摘要：busi.authority.management

```text
# busi.authority.management
```

## 静态结构画像
- 文本/代码文件数：32
- Go 文件数：23
- 文件类型分布：.go(23), .toml(4), .yml(2), .md(2), .json(1)
- 顶层目录分布：model(8), app(6), dao(5), server(3), service(3), api(2), backend(1), conf(1)

## 关键目录
- `model`: 8 个文本/代码文件
- `app`: 6 个文本/代码文件
- `dao`: 5 个文本/代码文件
- `server`: 3 个文本/代码文件
- `service`: 3 个文本/代码文件
- `api`: 2 个文本/代码文件
- `backend`: 1 个文本/代码文件
- `conf`: 1 个文本/代码文件

## 代码分层
- 接入层文件：3 个
- 服务层文件：3 个
- 数据访问文件：5 个
- 模型文件：8 个
- 任务/定时相关文件：0 个
- RPC/IDL 相关文件：1 个

## API/路由线索
- 静态扫描未提取到显式路由字符串，需结合框架注册/网关配置确认

## 核心类型与方法线索
- 导出结构体：Dao, BaseResponse, Permission, RolePermission, UserRole, Role, AuthorityResp, RoleResp, PermissionReq, AuthorityReq, RoleReq, PermissionReq, AuthorityUserReq, RoleUserReq, RolePermissionReq, Service, Config
- 导出函数/方法：GetRolesCache, SetRoleCache, MSetRoleCache, GetRoleKey, GetRoles, CreateRole, GetUserRoles, AddUserRoles, GetPermissionsCache, SetPermissionCache, MSetPermissionCache, GetPermissionKey, GetPermissions, CreatePermission, GetPermissionsByRoleId, CreateRolePermission, New, Ping, Close, PermissionGet, Init, Shutdown, TableName, TableName, TableName, TableName, New, Ping, Close, GetPermissions

## 外部依赖线索
- Daenerys 框架: 6 处信号
- HTTP/外部接口: 4 处信号
- GORM: 4 处信号
- Redis: 1 处信号

## 内部依赖线索
- `git.inke.cn/bpc/server/busi/busi.authority.management`: 20
- `git.inke.cn/BackendPlatform/golang/logging`: 4
- `git.inke.cn/inkelogic/daenerys`: 4
- `git.inke.cn/inkelogic/daenerys/http/server`: 3
- `git.inke.cn/BackendPlatform/golang/redis`: 1
- `git.inke.cn/BackendPlatform/golang/sql`: 1
- `git.inke.cn/BackendPlatform/golang/ecode`: 1

## 第三方 import 概览
- os(2), flag(1), log(1), syscall(1)

## IDL/协议文件
- 未发现 proto/thrift 文件

## 工程质量与交付
- GitLab CI：有
- golangci-lint：有
- 测试文件：
- 未发现 `_test.go`

## 阅读建议
- 先读 README 和 `server/http`、`handler`、`service` 目录，确认入口 API 与核心业务流程。
- 再沿服务层方法进入 DAO/Repo/Model，确认数据表、缓存 Key、RPC 调用和异步任务。
- 若图中只出现少量节点，通常表示该项目是配置型/胶水型服务，需结合上层共享工程和部署配置继续确认。
