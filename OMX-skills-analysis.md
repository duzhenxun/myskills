# OMX Skills Analysis

生成时间：2026-06-23

范围：本机当前用户技能目录 `/Users/dds/.codex/skills` 中，`SKILL.md` frontmatter 的 `description` 含 `[OMX]` 的技能。未包含 `figma`、`inke-reuse-act` 等不带 `[OMX]` 前缀的技能。

## 总览建议

| 场景 | 首选技能 | 说明 |
|---|---|---|
| 需求不清、边界不清 | `$deep-interview` | 先访谈澄清，不直接开工。 |
| 想先要方案 | `$plan` 或 `$ralplan` | 普通方案用 `$plan`；需要架构师+批判者共识用 `$ralplan`。 |
| 已有明确目标，要长期跟踪执行 | `$ultragoal` | 用 `.omx/ultragoal` 维护目标、账本、验证证据。 |
| 大任务要多 Agent 并行 | `$team` | tmux 工人、共享任务状态、邮箱协调。 |
| 单 Agent 持续推进到完成 | `$ralph` | 自循环执行并带架构验证；现在多用于明确要求的 fallback。 |
| 全自动从澄清到 QA | `$autopilot` | 严格流水线：访谈 -> 共识计划 -> 目标执行 -> review -> QA。 |
| 只分析代码，不改文件 | `$analyze` | 输出证据、推断、置信度和未知项。 |
| 代码审查 | `$code-review` | 综合 review，发现问题优先。 |
| 动态端到端/敌意测试 | `$ultraqa` | 构造 hostile scenarios，测试、修复、复验。 |
| 前端视觉对齐 | `$visual-ralph` | 截图/参考图/URL 驱动的像素对齐循环。 |
| 性能优化 | `$performance-goal` | 需要 evaluator 指标闭环的性能任务。 |
| 清理 AI 味/重构 | `$ai-slop-cleaner` | 先锁行为和计划，再小步清理。 |
| 外部资料/最佳实践 | `$best-practice-research` 或 `$autoresearch-goal` | 普通最佳实践用前者；需要教授-批判者验证闭环用后者。 |
| 管理技能/OMX 安装/状态 | `$skill`、`$omx-setup`、`$doctor`、`$hud`、`$cancel` | 本地运维类。 |

## 详细表格

| 技能 | 类型 | 做什么 | 如何使用 | 适用场景 | 不适用/注意点 | 常见组合 |
|---|---|---|---|---|---|---|
| `$ai-slop-cleaner` | 清理/重构 | 运行 anti-slop cleanup/refactor/deslop 工作流，重点删除冗余、收敛抽象、修复边界，同时保持行为不变。 | 直接说 `$ai-slop-cleaner 清理这个模块`，或在已选执行 lane 内作为 bounded helper 使用。 | AI 生成代码味重、过度抽象、重复逻辑、命名混乱、需要行为不变的整理。 | 不能跳过清理计划；覆盖不足时先补回归测试；不应借机加新依赖或大改架构。 | `$ralplan` 定计划后执行；`$code-review` 复查；`$ultraqa` 做行为验证。 |
| `$analyze` | 只读分析 | 对仓库做 read-only deep analysis，输出有证据的排名式结论，区分 evidence / inference / unknowns。 | `$analyze 为什么这里会这样？`、`investigate X`、`what's causing X`。 | 先搞清楚原因、影响面、代码关系；还不想改代码。 | 明确不改文件、不生成实现计划、不把推测当事实。 | 后接 `$ralplan` 或直接实现；复杂时可用 native subagents 辅助探索。 |
| `$ask` | 外部顾问 | 调用本地 Claude/Gemini CLI 做聚焦二次意见，并保存可复用 artifact。 | `$ask claude review this plan` 或 `$ask gemini brainstorm alternatives`。 | 需要第二意见、设计挑战、局部审查、头脑风暴。 | 依赖本机 CLI；不要在本地 CLI 缺失时静默切到远程/MCP。 | 配合 `$ralplan`、`$code-review`、`$best-practice-research`。 |
| `$autopilot` | 全自动流水线 | 严格自动链路：`$deep-interview -> $ralplan -> $ultragoal (+ $team) -> $code-review -> $ultraqa`。 | `$autopilot implement issue #42`、`autopilot build ...`、`继续` 可恢复当前 phase。 | 用户想 hands-off，从想法/issue/PRD 到已审查和 QA 的代码。 | 不适合单个小改、只解释、只 review、开放式脑暴。重流程，成本高。 | 内部串联深访、计划、目标执行、团队、review、QA。 |
| `$autoresearch` | 研究闭环 | Stateful validator-gated research loop，用 native hook 持久化状态，研究成果必须过 validator。 | `$deep-interview --autoresearch` 澄清后，再 `$autoresearch` 执行。 | 研究本身就是交付物，且需要明确验证器/合格标准。 | 不用于普通规划前资料查询；不应变成最终架构组件，除非用户要求持续研究自动化。 | 研究产物交给 `$ralplan` 作证据。 |
| `$autoresearch-goal` | 研究目标模式 | 在 Codex goal mode 上跑 durable professor-critic research workflow，不复活旧 `omx autoresearch`。 | `$autoresearch-goal 研究 X 并给出验证通过结论`。 | 需要长程、可追踪、带批判者审查的研究任务。 | 适合研究交付，不适合普通代码实现。 | 后接 `$ralplan`、`$ultragoal`。 |
| `$best-practice-research` | 官方资料/最佳实践 | 有边界的最佳实践研究包装器，优先官方/上游证据。 | `$best-practice-research React 19 form actions best practice`。 | 当前决策依赖外部 API、标准、版本行为、官方建议。 | 不替代仓库探索；本地实现关系仍需读代码。 | `$deep-interview` 遇到外部不确定性时调用；结果进入 `$ralplan`。 |
| `$cancel` | 状态清理 | 取消 active OMX mode，包括 autopilot、ralph、ultrawork、ultraqa、team、pipeline 等，并清理对应状态。 | `$cancel`；需要全清理时 `$cancel --force` 或 `$cancel --all`。 | 工作完成、用户要求停止、状态卡死、要重置某个执行模式。 | 不要在可恢复工作未处理时乱 cancel；team/ralph 有特定 post-condition。 | 配合所有长程 OMX 模式。 |
| `$code-review` | 代码审查 | 运行全面 code review，优先列 bug、风险、回归、缺失测试。 | `$code-review`、`review this branch`。 | PR 前审查、复杂改动后复查、自动流水线 review 阶段。 | 不是实现工具；发现问题后才进入修复/执行 lane。 | `$autopilot` 固定阶段；后接 `$ultraqa`。 |
| `$configure-notifications` | 通知配置 | OMX 通知统一入口，配置 Discord/Telegram/Slack、自定义 webhook/CLI、OpenClaw 等。 | `$configure-notifications` 打开配置流程。 | 想让 OMX 长任务完成/阻塞/需要输入时发通知。 | 涉及 webhook/token 时注意凭证；配置后要做验证。 | `$hud`、长程 `$team`/`$autopilot`。 |
| `$deep-interview` | 需求澄清 | 苏格拉底式访谈，带 ambiguity scoring 和边界门禁，执行前把需求澄清到可交付。 | `$deep-interview 我要做 X`；或用户说 “don't assume/别猜”。 | 目标不清、非目标不清、验收标准不清、决策边界不清。 | 每轮只问一个聚焦问题；模糊度未过门禁时不应交付执行。 | 后接 `$ralplan`、`$ultragoal`、`$autopilot`、`$autoresearch`。 |
| `$design` | 产品/设计源头 | 创建或刷新 repo-local `DESIGN.md`，作为 UI/UX/前端决策的持久 source of truth。 | `$design 为这个应用整理设计原则`。 | 产品、UI/UX、组件库、前端风格需要统一决策。 | 有视觉参考并要像素级实现时用 `$visual-ralph`；不要凭空加设计系统。 | `$visual-ralph`、前端实现、`$ralplan`。 |
| `$doctor` | OMX 诊断修复 | 诊断并修复 oh-my-codex 安装问题。 | `$doctor` 或 `$doctor 检查 omx 为什么不可用`。 | CLI、hooks、skills、runtime、状态目录异常。 | 会做本机诊断；需要区分可读检查和需要权限的修复。 | `$omx-setup`、`$skill`。 |
| `$hud` | 状态栏/HUD | 展示或配置 OMX 两层状态栏/HUD。 | `$hud`、`$hud focused`、`$hud --watch`。 | 想实时看 Codex/OMX 当前模式、队列、状态。 | HUD 是观察面，不是任务执行面。 | 长程 `$team`、`$autopilot`、`$ralph`。 |
| `$omx-setup` | 安装配置 | 按当前 CLI 行为安装和配置 oh-my-codex。 | `$omx-setup` 或 `omx setup`。 | 首次安装、升级后补齐配置、环境迁移。 | 安装/修改本机配置前要基于实际状态检查。 | `$doctor` 验证；`$skill` 管理技能。 |
| `$performance-goal` | 性能优化闭环 | 在 Codex goal mode 上运行 evaluator-gated performance optimization。 | `$performance-goal 优化列表渲染性能，指标是 ...`。 | 有明确性能指标、benchmark/evaluator、需要持续优化直到达标。 | 没有 evaluator 时不适合；不能未通过指标就标完成。 | `$ultragoal`、`$code-review`、性能测试。 |
| `$pipeline` | 流水线编排 | 可配置 pipeline orchestrator，用于把多个 stage 顺序编排。 | `$pipeline` 或由 `$autopilot` 等技能内部使用。 | 需要固定 stage 接口、状态管理、可恢复的序列化流程。 | 更偏底层编排；普通任务不用直接选它。 | `$autopilot`、自定义 OMX 工作流。 |
| `$plan` | 方案规划 | 战略规划，可带可选访谈，输出计划/权衡/测试形态。 | `$plan 先给我个方案`。 | 用户明确只想要方案、架构选择、任务拆解、风险评估。 | 不应直接进入代码执行，除非用户明确改成执行。 | `$ralplan` 是共识加强版；后接 `$ultragoal` 或 `$team`。 |
| `$prometheus-strict` | 严格澄清规划 | Clean-room interview-driven planner：Metis 澄清、Momus 挑战、Oracle 综合，再交给 `$ultragoal`/`$team`。 | `$prometheus-strict 帮我严格梳理这个需求`。 | 高风险、边界复杂、容易误解的需求，需要强对抗式澄清。 | 重流程；小任务不划算。 | 后接 `$ultragoal`、`$team`。 |
| `$ralph` | 单 Owner 持续执行 | 自引用循环直到任务完成，带 architect verification。 | `$ralph 修复这个 bug`。 | 明确、窄范围、需要一个 agent 持续推进并自检。 | 现在更适合作为明确要求的 fallback；耐久目标默认更推荐 `$ultragoal`。 | `$ralplan` 后显式选择；可接 `$code-review`。 |
| `$ralplan` | 共识计划 | `$plan --consensus` 别名，计划需 Architect + Critic 审查，输出 durable handoff。 | `$ralplan 设计一下这个功能`。 | 架构/测试形态/执行边界需要共识，不想直接开工。 | planning/execution 边界清晰：完成规划后再选执行 lane。 | 后接 `$ultragoal`、`$team`、明确要求时 `$ralph`。 |
| `$skill` | 技能管理 | 管理本地 skills：list/add/remove/search/edit/setup/scan。 | `$skill list`、`$skill search wiki`、`$skill add my-skill`。 | 查看、创建、编辑、同步、诊断本地技能。 | remove 是破坏性操作，必须确认；技能 frontmatter 要合法。 | `$doctor`、`$omx-setup`、skill authoring。 |
| `$team` | 多 Agent 协作 | tmux-based N workers，支持共享任务状态、mailbox、dispatch、生命周期控制。 | `$team implement this plan with 4 workers`。 | 多模块并行、长任务、需要工人窗格和可恢复状态。 | 有开销；小任务用 native subagents 或 solo 即可。不要把 `worker` 当普通角色直接用。 | `$ultragoal + $team`：目标账本归 leader，team 并行执行。 |
| `$ultragoal` | 持久目标执行 | 创建和执行 repo-native multi-goal plans，维护 `.omx/ultragoal/goals.json` 和 `ledger.jsonl`。 | `$ultragoal 完成这个 PRD`、`$ultragoal create-goals ...`。 | 已澄清/已规划的大任务，需要可恢复、可验证、多目标推进。 | 不要手改目标状态；不要弱化验证；动态 steering 需显式且有证据。 | `$deep-interview`/`$ralplan` 后默认执行 lane；可叠加 `$team`。 |
| `$ultraqa` | 强 QA / E2E | Adversarial dynamic e2e QA：生成敌意场景、测试、修复、报告、清理。 | `$ultraqa test this feature`。 | 功能完成后做强验证，尤其用户流、边界、回归、前端交互。 | 不替代单元测试；需要可运行环境和可验证目标。 | `$autopilot` 末段；`$code-review` 后。 |
| `$ultrawork` | 并行执行引擎 | 高吞吐 parallel execution engine。 | `$ultrawork` 或由其他模式调度。 | 明确任务可拆成多个并行执行片段，需要提高吞吐。 | 不适合目标不清；通常不作为首选入口。 | `$ralph`/`$pipeline`/其他 OMX 编排。 |
| `$visual-ralph` | 视觉实现闭环 | 面向前端 UI 的 Visual Ralph：从参考图、生成参考或 live URL 出发，用截图/像素差异迭代到匹配。 | `$visual-ralph 按这个 Figma/截图实现页面`。 | 视觉保真、前端 UI、需要截图证据和设计系统沉淀。 | 只整理设计原则用 `$design`；只比较截图也可走其视觉 verdict。 | `$design` 提供决策基础；后接浏览器验证。 |
| `$wiki` | 项目 Wiki | 在仓库 `omx_wiki` 下维护持久 markdown project wiki，支持关键词搜索和生命周期捕获。 | `$wiki search redis`、`$wiki capture ...`。 | 项目知识沉淀、跨会话上下文、决策记录。 | 这是 repo-local markdown wiki，不是公司 Confluence。 | 长期项目、`$analyze`/`$ralplan` 后沉淀。 |
| `$worker` | Team 工人协议 | Team worker protocol：ACK、mailbox、task lifecycle、任务领取/完成。 | 通常由 `$team` worker inbox 指令加载，不手动作为普通技能使用。 | 已经处于 tmux-based OMX team，某个 worker 收到任务。 | 严禁当一般子代理角色随意调用；只服务 team runtime。 | `$team` 内部协议。 |

## 使用路线图

| 你现在想做什么 | 推荐路线 |
|---|---|
| “先别改，帮我看看为什么” | `$analyze` |
| “我还没想清楚，别猜” | `$deep-interview` |
| “先给我方案/技术方案” | `$plan`；复杂架构用 `$ralplan` |
| “方案已定，持续推进到完成” | `$ultragoal` |
| “任务很大，多个模块可并行” | `$ultragoal` + `$team` |
| “直接全自动帮我从需求做到 QA” | `$autopilot` |
| “帮我 review 这批改动” | `$code-review` |
| “做一次严格验收/端到端测试” | `$ultraqa` |
| “前端按截图/URL/设计稿对齐” | `$visual-ralph` |
| “优化性能，必须有指标” | `$performance-goal` |
| “清理这坨 AI 生成代码” | `$ai-slop-cleaner` |
| “查官方最佳实践再决策” | `$best-practice-research` |
| “管理/新增/修复技能” | `$skill`、`$doctor`、`$omx-setup` |
| “停止当前长任务/清状态” | `$cancel` |

## 本次纳入的技能路径

| 技能 | 文件 |
|---|---|
| `$ai-slop-cleaner` | `/Users/dds/.codex/skills/ai-slop-cleaner/SKILL.md` |
| `$analyze` | `/Users/dds/.codex/skills/analyze/SKILL.md` |
| `$ask` | `/Users/dds/.codex/skills/ask/SKILL.md` |
| `$autopilot` | `/Users/dds/.codex/skills/autopilot/SKILL.md` |
| `$autoresearch` | `/Users/dds/.codex/skills/autoresearch/SKILL.md` |
| `$autoresearch-goal` | `/Users/dds/.codex/skills/autoresearch-goal/SKILL.md` |
| `$best-practice-research` | `/Users/dds/.codex/skills/best-practice-research/SKILL.md` |
| `$cancel` | `/Users/dds/.codex/skills/cancel/SKILL.md` |
| `$code-review` | `/Users/dds/.codex/skills/code-review/SKILL.md` |
| `$configure-notifications` | `/Users/dds/.codex/skills/configure-notifications/SKILL.md` |
| `$deep-interview` | `/Users/dds/.codex/skills/deep-interview/SKILL.md` |
| `$design` | `/Users/dds/.codex/skills/design/SKILL.md` |
| `$doctor` | `/Users/dds/.codex/skills/doctor/SKILL.md` |
| `$hud` | `/Users/dds/.codex/skills/hud/SKILL.md` |
| `$omx-setup` | `/Users/dds/.codex/skills/omx-setup/SKILL.md` |
| `$performance-goal` | `/Users/dds/.codex/skills/performance-goal/SKILL.md` |
| `$pipeline` | `/Users/dds/.codex/skills/pipeline/SKILL.md` |
| `$plan` | `/Users/dds/.codex/skills/plan/SKILL.md` |
| `$prometheus-strict` | `/Users/dds/.codex/skills/prometheus-strict/SKILL.md` |
| `$ralph` | `/Users/dds/.codex/skills/ralph/SKILL.md` |
| `$ralplan` | `/Users/dds/.codex/skills/ralplan/SKILL.md` |
| `$skill` | `/Users/dds/.codex/skills/skill/SKILL.md` |
| `$team` | `/Users/dds/.codex/skills/team/SKILL.md` |
| `$ultragoal` | `/Users/dds/.codex/skills/ultragoal/SKILL.md` |
| `$ultraqa` | `/Users/dds/.codex/skills/ultraqa/SKILL.md` |
| `$ultrawork` | `/Users/dds/.codex/skills/ultrawork/SKILL.md` |
| `$visual-ralph` | `/Users/dds/.codex/skills/visual-ralph/SKILL.md` |
| `$wiki` | `/Users/dds/.codex/skills/wiki/SKILL.md` |
| `$worker` | `/Users/dds/.codex/skills/worker/SKILL.md` |

