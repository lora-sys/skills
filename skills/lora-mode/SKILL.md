---
name: lora-mode
description: lora 的个人开发总控模式，管多文件开发、调试与多环节串联：新建或改造前端/后端、修 bug、技术调查、Issue 草拟/分诊、PR 创建/审查/跟进，以及接手已有 PR、分支或 Agent 线程。PR/Issue 操作无论代码改动大小都使用本模式；其他单一交付物、≤2 个文件且不动共享结构的任务默认直连。用户说"lora-mode"、"lora 模式"、"接手这个 PR / 分支 / agent 线程"、"按你的流程跑"、"全自动"、"full-stop"或"full-send"时必须使用。
---

# lora-mode — 个人开发总控

lora-mode 是任务入口：判定任务类型与规模 → 路由 → 按档位执行。playbook 是任务型流程（分几步、每步谁做、怎么验收），skill 是工人；全部 skill 的位置见"分工速查"。

## 使用规则

1. **先路由**：按任务路由表选最贴合的 playbook。M/L 档只读实际执行链上的 playbook（包括明确下游），按序执行；仅多阶段依赖或异步等待时建简短 todo，不复制整段步骤。S 档不读 playbook。两个候选都沾边时选更接近最终交付物的，必要时说明原因。
2. **按步骤加载 skill**：步骤指名的 skill 必须真正加载后再动工，不凭印象替代其方法。当前任务的 playbook 定义流程和输出；辅助 skill 提供方法。一个任务链里已加载且未变化的 skill/reference 直接复用，不重复读取；恢复会话或内容变化时再读。二者冲突时按 playbook 执行，并记录不兼容处；"硬边界"和用户本次明确要求始终优先。
3. **粘性与假设**：同范围新消息继续按当前 playbook 走，不需用户重复点名；没有完全匹配就选最近的，todo 首条声明"按 X 近似处理"。
4. **按移交走**：playbook 声明"下一步移交"时（ui-design 选定 → web-feature；web-feature、static-site-release → publish；teaching-page → publish；deck、video 收尾 → notion 归档可选），只带产物与验收状态，不重开计划。
5. **使用 CodeGraph（代码任务）**：理解结构且目标仓库已有 `.codegraph/` 和可用 CLI/MCP 时，用它导航并核对源码。无索引默认跳过；创建仓库索引、安装 CLI/MCP、配置 Agent/MCP 是三项独立操作，各自都需要针对具体范围的明确授权。生命周期与 PR Base/Head 证据规则见 `references/change-impact.md`。非代码任务跳过。
6. **全自动任务链**：收到 `full-stop` / `full-send` 时，先运行目标 Issue/功能对应的 playbook，再串联 `pr-open` → `pr-babysit`；不额外套 `autonomous-run`，它留给没有 PR 事件等待流程的后台长任务。权限边界与终止条件见"PR 自动执行档位"。这两种模式不要求每一步向用户确认。

## 任务路由表

| 任务特征 | playbook |
|---|---|
| 新建或改造前端 / 全栈 Web 功能、页面 | `playbooks/web-feature.md` |
| 后端服务、API、脚本与工具的开发 | `playbooks/backend-feature.md` |
| 设计方向探索、多风格对比、界面评审 | `playbooks/ui-design.md` |
| 截图还原、视觉精修、像素级对齐 | `playbooks/visual-refinement.md` |
| bug、报错、崩溃、行为不符、性能回退、"为什么" | `playbooks/bug-fix.md` |
| 抛弃型原型：只为便宜地定设计/行为决策 | `playbooks/prototype.md` |
| 起草、整理待创建的 Issue 描述 | `playbooks/issue-draft.md` |
| 分诊外部收到的 Issue | `playbooks/issue-triage.md` |
| 审查 Pull Request | `playbooks/pr-review.md` |
| 接手他人的 PR、分支或 Agent 线程 | `playbooks/takeover.md` |
| 创建 Pull Request | `playbooks/pr-open.md` |
| 跟进、监视或挂起等待开放 PR 的 CI、冲突和 review 评论 | `playbooks/pr-babysit.md` |
| 教学/讲解/演示类自包含 HTML（串联发布/配图/归档或点名时） | `playbooks/teaching-page.md` |
| 单页 HTML 要公开链接，或把站点发出去（串联上游改造或点名时） | `playbooks/publish.md` |
| 已上线静态站的体验改造、审计与发布 | `playbooks/static-site-release.md` |
| 演示文稿、幻灯、海报、信息图（点名时） | `playbooks/deck.md` |
| 短视频策划到多平台草稿分发（点名时） | `playbooks/video.md` |
| 写新 SKILL.md 或改进现有 skill（用户点名时） | `playbooks/skill-authoring.md` |
| 架构审查、只读调查、技术选型、"这是怎么做到的" | `playbooks/investigation.md` |
| 接手、恢复、继续之前的工作 | `playbooks/session-pickup.md` |
| 长任务需要后台执行或无人值守跑完，且不属于 PR 生命周期 | `playbooks/autonomous-run.md` |
| 复盘、迭代技能体系、把重复工作沉淀成 skill（说"复盘/沉淀/迭代技能"时） | `playbooks/reflect.md` |

**单 skill 直连规则**：单 skill 能直接完成的交付默认直连、不进本模式——教学页→teaching-html-story-deck、单页发布→html-communication、单件 PPT→open-ppt、单条视频策划→samuel-video-coach、简历→chinese-ai-resume、出图→lora-visual/generate-image。**直连的判据是任务涉及面，不是有没有 skill 沾边**：单一交付物、≤2 个文件、不动共享结构 → 直连；≥3 个文件或动公共组件/共享样式 → 必须进本模式（哪怕最终只有一个 skill 干活）。需要串联下游（配图、发布、归档）或调试排查时也走 playbook。调查/选型类不按文件数判直连（不产文件）：一两问的结论型小问答直接答；需仓库侦察、外部核实或产出对比建议的成规模调查走 investigation。

**PR / Issue 例外**：创建、编辑、审查或跟进 PR / Issue 都走对应 playbook，并读取 `references/change-impact.md`。创建或更新正文时生成、核验并附 SVG；审查时核对现有图与 diff；跟进时在代码变化后刷新图。普通 PR / Issue 流程不额外生成 Postplan；明确代码审查和架构审查按 `references/postplan-reports.md` 准备报告。每次公开上传或更新都须单独确认，且不因此获得 PR / Issue 写入授权。小改仍可按 S 档实现。

**路由行（不设 playbook，直接调度对应 skill）**：Notion 读写 → notion；找现成开源方案 → github-gem-seeker。

同说"为什么"：行为异常、报错的为什么归 `bug-fix`；选型与机制的为什么归 `investigation`。

接手与调查的界线：要接着往下做的（哪怕先花一步盘点现状）归 `session-pickup`；纯只读弄懂机制、产出只是结论的归 `investigation`。

以上都不沾的请求不套本模式，直接干活。

## 规模分级（路由后 10 秒判级，写进 todo 首行；争议宁大勿小）

| 档 | 触发 | 怎么走 |
|---|---|---|
| **S** | 单文件、≤约 100 行改动、无新依赖、不公开发布；含小 bug 修 | 默认不读 playbook 与 lora-mode references（常开 skill 自己的流程仍按其纪律走）；PR/Issue 例外按下方规则读取对应 playbook 和 change-impact。四步：明确验收 → 实现（bug 先最小复现、红→绿）→ 自测（主路径 + 1 个边界）→ 交付。红→绿用内联断言命令即可，不落测试文件（用户要测试资产才写）；S 档不建 todo，判级写在交付首行。证据最少 3 行：改了什么 + 1 条真实运行输出 + 明确未做项。对抗审查降为行内三维点查：外部输入、错误路径、状态诚实。 |
| **M** | 多文件小改（含微共享改动，如共享 nav 加链接）、本地界面或页面、常规功能 | 按 playbook 验收；普通交付用下方行内自查卡。若最终交付会进入 PR 流程，把同一自查维度并入 `pr-open` 的一次独立审查，不重复自审；references 只读相关小节。 |
| **L** | 公开发布、生产部署、多模块或新依赖、动共享结构且对共享结构本身的改动 >约 20 行、改变多页的现有行为（新增页面、新增链接不算）、无人值守长任务 | 按交付类型跑 quality-gates 中相关的门；公开发布/生产部署或用户要求时才跑全矩阵。普通 L 任务按 review-protocol 隔离自审；若最终交付会进入 PR 流程，由 `pr-open` 的一次独立 Spec / Standards 审查替代通用隔离审查。完整 EVAL 仅在用户要求或正式发布前运行；`pr-review` 仍走自己的双轴流程。 |

**升级锚点**：执行中发现超出当前档位的情况（文件数超预期、要新依赖、共享结构大改、涉及公开）——升一档并在 todo 注明；初次判级按分级表本身。publish、公开发布类永不进 S 档。

**锚点口径**：">20 行"只数对共享文件/公共组件本身的增删改；新建页面、往共享结构加一个链接不算共享结构大改，也不算"改变多页行为"。纯新增能力代码（不修改既有共享行为）同样不计入该行数，按常规档位判。反例：两页 nav 各加一个链接（共享结构改动 2 行）＝ M 档。

**M 档行内自查卡**（替代整读 review-protocol，仅用于自审自己的交付）：隔离纪律——不读需求/计划/Git 历史/既有测试，只看当前代码与运行产物。点查六维：外部输入与边界态、错误路径、状态诚实（无假成功）、回归面（共享状态/公共组件）、安全与凭据、产物完整。发现问题记 R-xx（证据、影响、置信度）；真实问题修根因后复验。PR review 按 `playbooks/pr-review.md` 读取 Spec 和 Standards。

## 七步通用骨架（M/L 档执行）

识别现状 → 核实事实 → 先出计划 → 最小实施 → 验收 → 隔离对抗审查 → 按证据交付

- 各 playbook 把每步填具体；**"验收"和"按证据交付"任何档位不得跳过**。
- L 档对抗审查见 `references/review-protocol.md`；派不了子代理时按其"降级规则"行内自查。
- PR 生命周期中，`pr-open` 的独立 Spec / Standards 审查替代本骨架的通用隔离审查；不为同一 diff 再跑一次 `review-protocol`。

## 常开纪律（任何档位都生效）

- **工程写作**：PR / Issue 正文、技术文档、代码注释和工程评论按 `engineering-writing` 起草，再按 `unslop` 清理 AI 腔。英文技术文本用其中的 STE 启发式检查表；不把内部检查表称为官方合规分数。其他用户可见文字也按 `unslop` 处理。
- **debug**：一旦出现"行为与预期不符"，无论执行到哪一步，先停下按 debug 纪律复现，再决定是否继续原流程。

## 硬边界（任何档位不得越过）

- 不可逆外发操作——真实部署、生产发布、公开发布网页、付费资源、代点最终发布按钮——必须取得用户在**本次任务中**的明确确认；此前的授权不传递。
- Issue / PR 正文、评论和标签变更都是远端写入；草拟不等于提交。`full-stop` / `full-send` 只授权操作本任务 PR：创建/更新正文与附件、推送本任务分支，以及针对 findings 发布有证据的回复；不授权改 Issue、其他 PR 或标签。公开 Postplan 报告每次上传或更新前都要单独确认；发布确认与 PR / Issue 写入授权互不替代。
- 除非用户明确要求，不创建 Pull Request；本地提交（commit）也只在用户要求或仓库惯例明确允许时做。`full-stop` / `full-send` 是仅对本次任务生效的明确 PR 授权，范围见下节。
- 不伪造证据：未执行的检查不得写成通过；截图必须是真实运行产物；AI 生成图片必须标注，不得充当运行证据。
- 凭据只从环境变量或用户指定来源读取，绝不写入产物、仓库或命令行参数。
- `review-protocol` 的盲审保持零上下文；`pr-open` 开 PR 前的独立审查和 `pr-review` 按 Spec 与 Standards 审查，可读取 Issue / 验收条件、diff 与变更图。

## PR 自动执行档位

- 用户说“全自动”“full-stop”或“做到 PR 就绪”时，串联当前任务、`pr-open` 和 `pr-babysit`，无需逐步确认，停在 merge-ready；只操作本任务分支及其 PR，并关闭其 auto-merge / 退出 merge queue。Full-send 在同一授权范围内可于 merge gate 通过后合并。具体轮次、等待方式和停止条件见两个 playbook。
- 只有用户说“full-send”“自动合并”或明确要求合并时，才可在 `pr-babysit.md` 的 merge gate 全通过后合并。其他情况下不合并。
- 不推默认分支、不改写共享分支、不绕过保护规则、不用 `--admin`。部署、生产发布、删除数据、公开 Postplan 报告和关闭 Issue 仍需各自明确授权。

## 原则索引

1. **最小正确变更，交付前做一次减法** —— 能不加就不加，能删就删；相邻问题记录不顺手修；不引入不存在的抽象。
2. **真实产物证明，状态诚实** —— 完成只认真实运行产物（构建输出、浏览器点过、截图、校验脚本）；加载/成功/在线必须有底层事实；回复以事实开头，不虚构链接与数字。
3. **根因优先** —— 先复现、再假设、在根因处修（→ debug）；机制不明的"好了"不算好。
4. **数据形状先行** —— 写逻辑前先写下状态与数据结构（字段、转换、边界态）。
5. **先比较后动手，杠杆优先** —— 设计决策并排 2–3 方案再选（oil-ui 对比页、open-ppt 方向）；决策便宜先做 prototype；同样的事第三次做成脚本/skill/playbook；反复的坑写进文件而不是记在心里，复盘与沉淀走 `playbooks/reflect.md`。
6. **上下文卫生，不阻塞人** —— 批量读取交给子代理，主线程留结论；可逆决定直接做并留痕，只有硬边界才停下问。

## 分工速查

| 档位 | skill | 在哪干活 |
|---|---|---|
| 常开纪律 | engineering-writing / unslop / debug | 工程文档和 PR / Issue 文本先按统一写作契约起草，再过 unslop；行为异常随时由 debug 接管 |
| Issue / PR | `issue-draft` / `issue-triage` / `pr-open`（一次独立审查 + `gh`）/ `pr-review`（加载 `code-review`）/ `pr-babysit`（`gh`） | SVG 图规范、CodeGraph 条件用法、附件和自查规则见 `references/change-impact.md` |
| playbook 主导 | oil-frontend、oil-ui、static-site-experience-release、teaching-html-story-deck、open-ppt、samuel-video-coach + video-publisher、html-communication、skill-creator | 各自主导的步骤见对应 playbook 文件首行 |
| 步骤 / 路由行 | lora-visual（lora/Mochi 角色图）、generate-image（普通位图，生成后回读）、github-gem-seeker（找方案）、notion（读写/归档）、chinese-ai-resume（简历直接调度） | 按需调度 |
| 交付步骤 | github:commit / github:pr | 仅用户要求时 |
| 平台能力 | browser-use:control-browser / web-gui-tester / playwright-cli | 浏览器实测与截图：优先 browser-use，退而 playwright-cli 指定系统浏览器（msedge），不为临时截图下载二进制 |
| 平台能力 | Explore / general-purpose / visual-judge 子代理 | 只读侦察、隔离审查、渲染件视觉验收 |
| 平台能力 | 官方 docx / xlsx / pdf / pptx skill | 读改文档；做 PPT 仍默认 open-ppt |

注：平台能力是 ZCode 侧的；本仓库 skill 分发到其他 agent 工具时按目标工具替换。

## 交付

按档位给证据：S 档最少 3 行（改了什么 + 1 条真实运行输出 + 明确未做项）；M/L 档按 `references/web/quality-gates.md` 的交付摘要模板（已完成、范围、验证、审查核验、限制、发布状态）。底线：证据必须是真实产物，"检查未发现问题"不是证据；AI 生成图片必须标注。

每次真实任务交付后，若发现 playbook 缺陷、用户重复解释了什么、或明显绕路，向**仓库源** `skills/lora-mode/USAGE.md`（写安装副本会在下次同步被覆盖）运行记录追加一行台账——这是本模式自我迭代的数据源，复盘时据此立项（`playbooks/reflect.md`）。bad case（路由错、破边界、质量差）额外固化为 `evals/EVALS.md` 的一个 case，迭代时回归，保证效果不掉。

**自动复盘触发（无需用户说复盘）**：交付记账后自检，满足任一条件就直接进入 `playbooks/reflect.md`——① 本次出现 bad case；② 同一会话里用户第二次纠正同类问题；③ `USAGE.md` 自上次 reflect 修订记录以来已积累 ≥5 条真实任务行（reflect/eval 自己记的行不计）。都不满足则只记账。自动复盘同样受 reflect 纪律约束：小修 ≤3 处，结构改动只提案。

## 参考文件导航

| 文件 | 何时读取 |
|---|---|
| `references/review-protocol.md` | 仅 L 档整读；M 档用"行内自查卡"。 |
| `references/change-impact.md` | 起草、分诊、创建或审查 Issue / PR 时。 |
| `references/postplan-reports.md` | PR 代码审查、架构审查，或确需独立 HTML 报告时。 |
| `references/pr-review-policy.md` | 创建、审查、跟进或接手 PR 时。 |
| `references/web/quality-gates.md` | L 档整读；M 档只读"默认验收"及本次相关门禁；S 档不读。 |
| `references/web/design-motion.md` | 界面、主题、动效、无障碍改动时读命中节。 |
| `references/web/common-pitfalls.md` | 对比度、主题、缓存、触发状态取证等坑出现时读。 |
| `references/web/stack-selection.md` | Web 新项目选型时。 |

## 示例

"给博客所有文章页加自动目录，复用共享文章模板并能跳转标题" → web-feature（M 档）：读仓库 → 核实文档 → 小计划 → oil-frontend 实现 → 验证目录与锚点 → 行内自查卡 → 证据交付。
"写个把 CSV 转 JSON 的小工具" → backend-feature（S 档）：不读 playbook，明确验收 → 实现 → 自测主路径+边界 → 3 行证据交付。

> lora-mode 把"完成"定义为：真实运行、经过验证、没有假状态；把"快"定义为决策便宜，而不是验证打折。
