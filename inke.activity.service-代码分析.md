# inke.activity.service 代码分析

分析对象：`/Users/dds/go/src/git.inke.cn/opd/activitys/inke.activity.service`

分析时间：2026-06-04

## 1. 项目定位

`inke.activity.service` 是映客活动业务 Go 服务，承载运营活动相关的 API、Kafka 消费、Cron 脚本、榜单、任务、互动、商城、发奖和后台工具能力。

项目具有典型“活动平台型单体服务”特征：公共能力集中在 `service/`、`dao/`、`manager/`、`model/`，具体活动按目录复制模板并接入 HTTP、Kafka、Cron。

README 中明确说明项目为“映客活动 Go 服务”，并给出活动目录组织方式：`README.md:3-8`、`README.md:14-63`。

## 2. 技术栈

- 语言：Go。
- 构建方式：未发现 `go.mod`，更像 GOPATH 或内部构建体系。
- 服务框架：内部 `daenerys`。
- HTTP 路由：`git.inke.cn/inkelogic/daenerys/http/server`，通过 `GROUP`、`GET` 等方式注册。
- 数据库：MySQL，通过 `proxy.InitSQL` 初始化多个库。
- 缓存：Redis，通过 `proxy.InitRedis` 初始化。
- 消息队列：Kafka，通过 `proxy.InitKafkaConsumer` 初始化大量 Consumer。
- 定时任务：`github.com/robfig/cron`。
- JSON：`json-iterator/go`、`bitly/go-simplejson`。
- 日志：`git.inke.cn/BackendPlatform/golang/logging`。
- 外部服务访问：集中封装在 `manager/`，通过内部 HTTP 客户端访问用户、SSO、金融、钉钉、风控、游戏、活动 PHP 服务等。

## 3. 目录结构

核心目录如下：

- `act/`：所有活动业务代码。活动通常包含 `route.go`、`server.go`、`service.go`、`model.go`、`backend.go`、`kafka.go`、`cron.go`、`internal.go`。
- `app/main/`：服务入口，包括 `service_api`、`service_cron_a`、`service_cron_b`、`service_cron_s`、`gen_code`。
- `conf/`：全局配置解析与活动 JSON 配置加载。
- `dao/`：MySQL、Redis、Kafka Consumer 初始化与通用数据访问。
- `service/`：跨活动通用业务能力，如榜单、任务、互动、发奖、商城、用户、直播、资源奖励等。
- `manager/`：外部服务访问封装。
- `model/`：公共请求响应结构、Kafka 消息结构、DB 表模型、活动配置、任务、榜单等。
- `server/http/`：HTTP Server 初始化与总路由聚合。
- `server/cron/`：Cron 服务和 Kafka 消费服务。
- `docs/`：项目文档、活动开发场景规范和常用代码文档。
- `.agent/skills/` 与 `.aiassistant/rules/`：AI Agent 和 IDE 辅助规则。
- `AGENTS.md`、`CLAUDE.md`：面向 AI 代理的项目约束。

## 4. 服务入口

项目包含多个主进程入口。

### 4.1 API 服务

入口：`app/main/service_api/main.go`

启动流程：

1. 读取配置并初始化 `daenerys`。
2. `conf.Init()` 解析基础 TOML 配置。
3. `conf.InitActConfig(cfg)` 加载活动 JSON 配置。
4. `act.Init(cfg)` 初始化全局 `Dao`、`Mgr`、`Srv`。
5. 初始化大数据日志与金币服务。
6. `service.New(cfg)` 创建通用服务实例。
7. `server/http.Init(srv, cfg)` 启动 HTTP 服务。
8. 等待系统信号退出。

### 4.2 Cron A 服务

入口：`app/main/service_cron_a/main.go`

用途：日常活动 Kafka 消费与部分 Cron。启动配置、活动上下文、大数据、金币服务后，启动 `service_cron_a.NewCron` 和 `StartConsumeKafkaMsg`。

### 4.3 Cron B 服务

入口：`app/main/service_cron_b/main.go`

用途：定时脚本服务，常用于榜单奖励、结算类任务。

### 4.4 Cron S 服务

入口：`app/main/service_cron_s/main.go`

用途：大型赛事或特殊活动 Kafka 消费与 Cron。

## 5. HTTP 路由设计

HTTP 初始化位于 `server/http/http.go`：

- `daenerys.HTTPServer()` 获取 HTTP Server。
- 使用 namespace 插件。
- 开发环境开启简单 CORS。
- 调用 `initRoute(httpServer)` 注册路由。
- 通过 goroutine 启动 HTTP Server。

总路由聚合位于 `server/http/router.go`。当前实际启用的是长期在线、游戏和按负责人拆分的路由：`initRouteLong`、`initRouteGame`、`initRouteDzx`、`initRouteLhy`、`initRouteCcy`。年份路由 `initRoute2022/2023/2024/2025` 当前被注释。

活动内部路由通常遵循模板：

- 对外 API：`/api/act/{folder}/{conf}/`。
- 对内 API：`/api/internal/{folder}/{conf}/`，通常带 `act.CheckSsoTicket`。
- 免 ticket 内部接口：用于测试、修复、回调等特殊场景。

URL 拼接逻辑在 `service/service.go:248-264`：通过 `moduleName` 拆分出活动目录和配置名。

## 6. 核心模块分析

### 6.1 act 全局上下文

文件：`act/base.go`

`act` 包提供全局变量：

- `act.Conf`
- `act.Dao`
- `act.Mgr`
- `act.Srv`

`act.Init` 会分别创建 `dao.New(c)`、`manager.New(c)`、`service.New(c)`。活动代码可直接使用这些全局对象访问公共能力。

`CheckSsoTicket` 是后台接口 SSO 校验中间件，负责从 query/header 读取 ticket、调用 `Mgr.IsValidSsoTicket`、写入上下文用户信息，并记录后台操作大数据日志。

### 6.2 conf 活动配置加载

文件：`conf/activitys.go`

全局活动配置缓存：

- `GlobalActInfoConfig`：活动完整 JSON 字节。
- `GlobalActBaseInfoConfig`：活动基础配置。
- `GlobalActDateList`：按开始日期索引活动。

加载流程：

1. 读取 `server/http` 下所有 Go 文件。
2. 从 import 块中提取 `act20` 开头的活动包名。
3. 递归读取活动配置 JSON。
4. 解析活动开始、结束时间。
5. 将配置写入全局 map。

维护风险：`readDir` 中在判断“路由引用或 90 天内”之前已经执行 `jsonFiles[key] = byteValue`，因此 README 中描述的“只加载近 90 天或被路由引用配置”的过滤逻辑可能未真正生效。相关位置：`conf/activitys.go:121-142`。

### 6.3 dao 数据访问层

文件：`dao/dao.go`

`Dao` 聚合了数据库、Redis 和 Kafka Consumer：

- MySQL：`DbActivityH`、`DbBocWebdevBi`、`DbBaseProduct`、`DbBocWebdevAladdin`、`DbUserTitle`、`DbAppConfig`。
- Redis：`Redis`、`RedisXunBao`。
- Kafka：送礼、道具礼物、进出房、充值、开播、公聊、关注、PK、连麦、客户端埋点、守护添加通知等大量 Consumer。

Redis key 规范在 `dao/redis_cache.go`：

- 公共 key：`INKE:ENV:{env}:{suffix}`。
- 活动 key：`INKE:ENV:{env}:{kPrefix}:{suffix}`。
- `k_prefix` 通常来自活动 JSON。

榜单通用 ZSet 操作在 `dao/redis_zset.go`，包含设置分数、获取分数、分页榜单、全量榜单等能力。

### 6.4 service 通用服务层

文件：`service/service.go`

`Service` 聚合 `dao.Dao` 和 `manager.Manager`，提供跨活动公共能力：

- 活动配置读取：`GetActConf`、`GetActInfoByte`、`GetActBaseInfo`、`GetActTimeConf`。
- 请求用户初始化：`InitUid` 从 query 中读取 `uid`、`aid`、`sid`。
- 登录校验：`IsSessionValid`，非生产可对白名单用户跳过 session 校验。
- Cron 时间判断：`CheckCronTime`，活动结束 10 分钟后不再运行。
- 活动 API/Admin URL 拼接：`GetActApiUrl`、`GetActAdminUrl`。
- 用户数据日志：`SetUserDataLog`。
- Web 广播缓存：`SetWebBroadcast`、`GetWebBroadcast`。

### 6.5 manager 外部依赖封装

文件：`manager/manager.go`

`manager` 封装大量外部服务客户端，包括 API Gateway、用户登录/session/profile、SSO、钉钉、BaseProduct、大数据/ES、金融/充值、风控、短信、CRM、连麦、活动 PHP 服务、游戏服务、Zego、百度 API 等。

这种集中封装有利于活动业务复用外部能力，但也让 `manager` 成为外部依赖变化的集中风险点。

## 7. 主要业务能力

### 7.1 活动基础配置与请求模型

公共模型集中在 `model/`，如 `model/base_model.go` 定义：

- `BaseParamsReq`：uid、sid、aid、moduleName。
- `ActIndexInfoResp`：活动基础返回。
- `ActTime`：活动时间。
- `ActBaseInfo`：活动基础配置，包括 `k_prefix`、`module_name`、`act_name`、`act_url`、`act_time`、`gift_ids`、`ding_conf`。

### 7.2 榜单

榜单主要基于 Redis ZSet：

- 通用 Redis 操作：`dao/redis_zset.go`。
- 通用榜单服务：`service/rank_base.go`、`service/partRank.go`。
- 榜单模型：`model/modelRank/rank_base.go`。

活动榜单通常定义 Redis key，再调用通用 DAO/Service 完成积分写入、分页查询、用户排名查询和奖励结算。

### 7.3 用户任务与主播任务

通用用户任务在 `service/user_task.go`，能力包括：

- 从活动 JSON 读取任务配置。
- 获取最后一关。
- 根据积分获取当前关卡或循环任务进度。
- 根据 `taskKey` 获取任务定义。

项目规范要求任务类分数、数量、计数在 member 超过 1 时优先使用 `act.Dao.SetZSetScore`。

### 7.4 互动

核心实现：`service/draw_prize.go`

`DrawPrize` 处理互动主流程：读取奖池配置、随机奖励、记录奖池总次数和用户中奖次数、检查奖励上限、用户上限、大盘亏损、轮次限制，必要时重选奖励，并异步记录日志。

相关能力还包括：

- 奖池缓存：`DrawPrizePoolCache`。
- 中奖异步队列：`DrawInfoProducer`。
- 防刷锁：`DrawPrizeLock`。
- 互动记录查询：`GetDrawPrizeLog`。

项目规范统一术语为“互动”，避免“抽奖/玩法”等同义词混用。

### 7.5 商城与兑换

核心文件：`service/exchange_shop.go`

能力包括：

- `AddExchangeShopLog`：写兑换记录到 `db_activity_h`。
- `GetExchangeShopLog`：分页查询兑换记录。

相关模型在 `model/exchange_shop.go`。

### 7.6 发奖与资源奖励

相关文件：

- `service/resource_prize.go`
- `service/prize_info.go`
- `service/draw_prize_gen.go`
- `manager/task_resource.go`

项目规范要求奖励下发优先复用统一链路：`sendPrize -> formatPrize -> ResourcePrize`。

## 8. Kafka 与 Cron 架构

### 8.1 Kafka Consumer 初始化

Kafka Consumer 全部在 `dao/dao.go` 中初始化，覆盖送礼、充值、进出房、公聊、关注、PK、连麦、客户端埋点、守护通知等事件。

### 8.2 Cron A Kafka 启动

文件：`server/cron/service_cron_a/kafka.go`

`StartConsumeKafkaMsg` 以 goroutine 启动大量消费者，如送礼、道具礼物、进出房、充值、公聊、关注、客户端公共事件、守护添加通知等。

### 8.3 送礼 Kafka 示例

文件：`server/cron/service_cron_a/kafka_1_gift.go`

典型流程：

1. 限制并发处理。
2. 解析 `model.GiftEventMsg`。
3. 修正直播类型和团播类型。
4. 按 `BillId` 做短期幂等。
5. 灰度环境做白名单过滤。
6. 调用长期活动和具体活动的 `Backend.GiftHandle`。

维护风险：该文件极长，历史活动大量注释和启用混杂，手动启停成本高，冲突风险高。

### 8.4 Cron 注册

Cron A 位于 `server/cron/service_cron_a/cron.go`，使用秒级 cron。活动 Cron 通常由 `Backend.Cron(c *cron.Cron)` 注册任务，并通过 `CheckCronTime` 避免活动结束后继续运行。

## 9. 活动开发模式

标准活动目录通常包含：

- `model.go`：`ModuleName`、Redis key、配置 key、常量。
- `route.go`：对外 API、对内后台 API、免 ticket 内部接口。
- `server.go`：HTTP handler，负责参数读取、登录/时间/资格校验、响应 JSON。
- `service.go`：活动业务逻辑。
- `kafka.go` 或 `backend.go`：Kafka 事件处理，如 `GiftHandle`、`RechargeHandle`。
- `cron.go`：活动定时任务。
- `internal.go`：后台测试、修复、工具接口。

项目内已有开发规范：

- 所有活动开发先查 `docs/activity-dev-scenarios.md`。
- 按场景打开 `docs/activity-scenarios/` 下对应文档。
- 变更遵循链路：过滤 -> 计算 -> 发奖 -> 日志。
- 新活动优先复用模板，不重复造轮子。
- Kafka 消费先做活动时间、房型、资源过滤，再做积分与发奖。
- 任务与奖励需考虑幂等。
- `c.JSON` 返回最外层使用小驼峰。

## 10. 文档与 AI Agent 规则

项目对 AI 辅助开发已有较完整规范：

- `AGENTS.md`：统一项目约束，要求活动开发必须先识别场景并查阅对应文档。
- `CLAUDE.md`：Claude 类 Agent 指南，指定主知识来源和输出偏好。
- `.agent/skills/`：Cursor/Agent skill 入口。
- `.aiassistant/rules/`：GoLand AI Assistant 规则。
- `docs/activity-dev-scenarios.md`：活动开发触发词索引。
- `docs/activity-scenarios/`：具体场景开发流程。

这些文档已经把活动开发流程标准化，是后续维护和生成代码时应优先读取的资料。

## 11. 数据存储与外部依赖

### 11.1 MySQL

主要数据库包括：

- `db_inke_activity_h`
- `db_boc_webdev_bi`
- `db_base_product`
- `db_boc_webdev_aladdin`
- `db_user_title`
- `db_app_config`

用途包括活动记录、兑换记录、奖池、后台配置、用户头衔、基础商品等。

### 11.2 Redis

Redis 用于：

- 榜单 ZSet。
- 任务积分和次数。
- 活动锁。
- 互动奖池计数。
- 用户数据日志 List。
- 广播 List。
- 活动 server time。
- 白名单、隐榜、临时 CSV 导入数据。

### 11.3 Kafka

Kafka 是活动实时计算和任务推进的核心来源。活动根据送礼、充值、进出房、关注、PK、客户端行为等事件进行积分、任务、发奖和日志处理。

### 11.4 外部 HTTP 服务

外部依赖集中在 `manager/`，包括用户、SSO、金融、风控、钉钉、游戏、活动 PHP 服务等。活动代码通常不直接操作底层 HTTP 客户端，而是通过 manager 封装方法复用。

## 12. 主要风险与维护点

### 12.1 明文配置风险

`app/config/service-api.toml` 中存在数据库、Redis 等连接配置和敏感信息。建议后续迁移到配置中心或密钥管理系统，避免敏感信息进入仓库。

### 12.2 活动配置过滤逻辑疑似失效

`conf/activitys.go` 的注释和 README 表示要只加载近 90 天或路由引用的活动配置，但代码在判断前已无条件写入 `jsonFiles[key] = byteValue`。这可能导致过期未引用配置仍被加载，削弱启动优化效果。

### 12.3 路由/Kafka/Cron 手动维护成本高

当前路由、Kafka、Cron 注册大量依赖手工 import、手工调用和注释切换。风险包括：

- 忘记注册路由或 Kafka Handle。
- 活动下线后忘记注释导致无效消费。
- 历史活动注释和复用活动混杂，冲突频繁。
- 编译依赖大量活动包。

### 12.4 运行目录假设较强

`conf/activitys.go` 中 `getActCodePath` 通过当前工作目录向上 3 级推导仓库根路径。如果部署目录、二进制位置或运行目录变化，可能找不到 `server/http`。

### 12.5 Close/Ping 为空实现

`dao.Close`、`dao.Ping`、`manager.Close` 等目前多为空实现。如果底层资源需要显式释放或健康检查，当前实现可能无法及时发现连接异常或释放资源。

### 12.6 幂等锁粒度需按业务复核

送礼 Kafka 用 `BillId` 做短期 NX 锁适合过滤短时间重复消费，但 Kafka 重放或补数据跨越锁过期时间时，活动内部仍需独立保证幂等。

### 12.7 自动化测试覆盖有限

项目大量业务依赖 Redis、MySQL、Kafka 和外部服务，自动化测试覆盖看起来有限。高风险链路如发奖、互动、榜单结算应补充最小化集成测试或可重放自测工具。

## 13. 建议

1. 敏感配置迁移到配置中心或密钥管理系统。
2. 修正或确认 `conf/activitys.go` 的活动配置过滤逻辑。
3. 将路由、Kafka、Cron 注册逐步改为生成式或配置化管理。
4. 强化活动模板、生成脚本和场景文档的一致性。
5. 对发奖、互动、榜单结算等高风险链路补充最小化集成测试。
6. 对 Kafka 消费链路建立统一幂等策略，避免只依赖短期锁。
7. 为 `Dao`、`Manager` 增加真实健康检查和资源释放逻辑。

## 14. 总结

`inke.activity.service` 公共能力完整，覆盖活动 API、Kafka、Cron、榜单、任务、互动、商城、发奖、后台工具等核心场景。它的优势是模板化和复用能力强，能够快速承接大量活动需求；主要挑战是多年历史活动沉淀导致路由、Kafka、Cron 手动维护文件膨胀，以及配置和幂等链路存在维护风险。

后续维护时，应优先遵循 `AGENTS.md`、`CLAUDE.md`、`docs/activity-dev-scenarios.md` 和 `docs/activity-scenarios/` 中的活动开发规范，避免绕过既有模板和统一链路。
