---
name: lora-mode
description: lora 的个人开发总控模式，管多文件开发、调试与多环节串联——新建或改造前端/后端功能、修 bug 与排查、技术调查、配图-发布-归档流水线：先进本模式选 playbook，再按 playbook 调度具体 skill。单一交付物、≤2 个文件、不动共享结构的任务（教学页、单件 PPT、单页发布、单条视频策划、出图、简历）默认直连对应 skill、不进本模式；≥3 个文件或动共享结构的开发任务必须进本模式（档位按规模分级判）。用户说"lora-mode""lora 模式""按你的流程跑"时必须使用。
---

# lora-mode — 个人开发总控

lora-mode 是任务入口：判定任务类型与规模 → 路由 → 按档位执行。playbook 是任务型流程（分几步、每步谁做、怎么验收），skill 是工人；全部 skill 的位置见"分工速查"。

## 使用规则

1. **先路由**：按任务路由表选最贴合的 playbook。M/L 档整篇读取 playbook，把步骤原样建成 todo 逐条执行，不合并不改名；S 档只调度对应 skill 或直接干活，不读 playbook。两个 playbook 都沾边时选更接近最终交付物的，todo 首行注明理由。
2. **按步骤加载 skill**：步骤指名的 skill 必须真正加载后再动工，不凭印象替代其行为。skill 与 playbook 冲突以 skill 为准；skill、playbook 与"硬边界"冲突以硬边界为准。
3. **粘性与假设**：同范围新消息继续按当前 playbook 走，不需用户重复点名；没有完全匹配就选最近的，todo 首条声明"按 X 近似处理"。
4. **按移交走**：playbook 声明"下一步移交"时（ui-design 选定 → web-feature；web-feature、static-site-release → publish；teaching-page → publish；deck、video 收尾 → notion 归档可选），只带产物与验收状态，不重开计划。

## 任务路由表

| 任务特征 | playbook |
|---|---|
| 新建或改造前端 / 全栈 Web 功能、页面 | `playbooks/web-feature.md` |
| 后端服务、API、脚本与工具的开发 | `playbooks/backend-feature.md` |
| 设计方向探索、多风格对比、界面评审 | `playbooks/ui-design.md` |
| 截图还原、视觉精修、像素级对齐 | `playbooks/visual-refinement.md` |
| bug、报错、崩溃、行为不符、性能回退、"为什么" | `playbooks/bug-fix.md` |
| 抛弃型原型：只为便宜地定设计/行为决策 | `playbooks/prototype.md` |
| 教学/讲解/演示类自包含 HTML（串联发布/配图/归档或点名时） | `playbooks/teaching-page.md` |
| 单页 HTML 要公开链接，或把站点发出去（串联上游改造或点名时） | `playbooks/publish.md` |
| 已上线静态站的体验改造、审计与发布 | `playbooks/static-site-release.md` |
| 演示文稿、幻灯、海报、信息图（点名时） | `playbooks/deck.md` |
| 短视频策划到多平台草稿分发（点名时） | `playbooks/video.md` |
| 写新 SKILL.md 或改进现有 skill（用户点名时） | `playbooks/skill-authoring.md` |
| 只读调查、技术选型、"这是怎么做到的" | `playbooks/investigation.md` |
| 接手、恢复、继续之前的工作 | `playbooks/session-pickup.md` |
| 长任务需要无人值守跑完 | `playbooks/autonomous-run.md` |
| 复盘、迭代技能体系、把重复工作沉淀成 skill（说"复盘/沉淀/迭代技能"时） | `playbooks/reflect.md` |

**单 skill 直连规则（v0.5.1 裁决，v0.5.2 修边界，v0.5.5 补调查下限）**：单 skill 能直接完成的交付默认直连、不进本模式——教学页→teaching-html-story-deck、单页发布→html-stable-publish、单件 PPT→open-ppt、单条视频策划→samuel-video-coach、简历→chinese-ai-resume、出图→lora-visual/generate-image。**直连的判据是任务涉及面，不是有没有 skill 沾边**：单一交付物、≤2 个文件、不动共享结构 → 直连；≥3 个文件或动公共组件/共享样式 → 必须进本模式（哪怕最终只有一个 skill 干活）。需要串联下游（配图、发布、归档）或调试排查时也走 playbook。调查/选型类不按文件数判直连（不产文件）：一两问的结论型小问答直接答；需仓库侦察、外部核实或产出对比建议的成规模调查走 investigation。

**路由行（不设 playbook，直接调度对应 skill）**：Notion 读写 → notion；找现成开源方案 → github-gem-seeker。

同说"为什么"：行为异常、报错的为什么归 `bug-fix`；选型与机制的为什么归 `investigation`。

接手与调查的界线：要接着往下做的（哪怕先花一步盘点现状）归 `session-pickup`；纯只读弄懂机制、产出只是结论的归 `investigation`。

以上都不沾的请求不套本模式，直接干活。

## 规模分级（路由后 10 秒判级，写进 todo 首行；争议宁大勿小）

| 档 | 触发 | 怎么走 |
|---|---|---|
| **S** | 单文件、≤约 100 行改动、无新依赖、不公开发布；含小 bug 修 | 不读 playbook 与 lora-mode 的 references（常开 skill 自己的内部流程与参考仍按其纪律走）。四步：明确验收 → 实现（bug 先最小复现、红→绿）→ 自测（主路径 + 1 个边界）→ 交付。红→绿用内联断言命令即可，不落测试文件（用户要测试资产才写）；S 档不建 todo，判级写在交付首行。证据最少 3 行：改了什么 + 1 条真实运行输出 + 明确未做项。对抗审查降为行内三维点查：外部输入、错误路径、状态诚实。 |
| **M** | 多文件小改（含微共享改动，如共享 nav 加链接）、本地界面或页面、常规功能 | 整读 playbook 走七步骨架；对抗审查用下方"行内自查卡"，不整读协议；references 只读命中小节。 |
| **L** | 公开发布、生产部署、多模块或新依赖、动共享结构且对共享结构本身的改动 >约 20 行、改变多页的现有行为（新增页面、新增链接不算）、无人值守长任务 | 完整七步：整读 playbook + 整读 review-protocol 做隔离审查（可派子代理时）+ quality-gates 全矩阵。轮次预算：截图/QA 类循环最多两轮（发现 → 修复 → 复截即止），不为打磨无限循环；审查子代理只喂协议的"隔离边界"与"强制审查维度"两节。 |

**升级锚点**：执行中发现超出当前档位的情况（文件数超预期、要新依赖、共享结构大改、涉及公开）——升一档并在 todo 注明；初次判级按分级表本身。publish、公开发布类永不进 S 档。

**锚点口径**：">20 行"只数对共享文件/公共组件本身的增删改；新建页面、往共享结构加一个链接不算共享结构大改，也不算"改变多页行为"。纯新增能力代码（不修改既有共享行为）同样不计入该行数，按常规档位判。反例：两页 nav 各加一个链接（共享结构改动 2 行）＝ M 档。

**M 档行内自查卡**（替代整读 review-protocol）：隔离纪律——不读需求/计划/Git 历史/既有测试，只看当前代码与运行产物。点查六维：外部输入与边界态、错误路径、状态诚实（无假成功）、回归面（共享状态/公共组件）、安全与凭据、产物完整。发现问题记 R-xx（证据、影响、置信度）；真实问题修根因后复验。

## 七步通用骨架（M/L 档执行）

识别现状 → 核实事实 → 先出计划 → 最小实施 → 验收 → 隔离对抗审查 → 按证据交付

- 各 playbook 把每步填具体；**"验收"和"按证据交付"任何档位不得跳过**。
- L 档对抗审查见 `references/review-protocol.md`；派不了子代理时按其"降级规则"行内自查。

## 常开纪律（任何档位都生效）

- **unslop**：所有用户可见文字——回复、说明、UI 文案、标题与封面文案——交付前按 unslop 过一遍；成段交付物（README、策划案、报告正文）正式加载 unslop 全文核对，一句话回复按其要点即可。
- **debug**：一旦出现"行为与预期不符"，无论执行到哪一步，先停下按 debug 纪律复现，再决定是否继续原流程。

## 硬边界（任何档位不得越过）

- 不可逆外发操作——真实部署、生产发布、公开发布网页、付费资源、代点最终发布按钮——必须取得用户在**本次任务中**的明确确认；此前的授权不传递。
- 除非用户明确要求，不创建 Pull Request；本地提交（commit）也只在用户要求或仓库惯例明确允许时做。
- 不伪造证据：未执行的检查不得写成通过；截图必须是真实运行产物；AI 生成图片必须标注，不得充当运行证据。
- 凭据只从环境变量或用户指定来源读取，绝不写入产物、仓库或命令行参数。
- 对抗审查者保持零上下文：不读用户需求、计划、Git 历史、既有测试。

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
| 常开纪律 | unslop / debug | 用户可见文字交付前过 unslop；行为异常随时由 debug 接管 |
| playbook 主导 | oil-frontend、oil-ui、static-site-experience-release、teaching-html-story-deck、open-ppt、samuel-video-coach + video-publisher、html-stable-publish、skill-creator | 各自主导的步骤见对应 playbook 文件首行 |
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
| `references/web/quality-gates.md` | L 档整读；M 档只读"证据矩阵"节；S 档不读。 |
| `references/web/design-motion.md` | 界面、主题、动效、无障碍改动时读命中节。 |
| `references/web/common-pitfalls.md` | 对比度、主题、缓存、触发状态取证等坑出现时读。 |
| `references/web/stack-selection.md` | Web 新项目选型时。 |

## 示例

"给我的博客首页加个目录" → web-feature（M 档）：读仓库 → 核实文档 → 小计划 → oil-frontend 实现 → 真实浏览器截图 → 行内自查卡 → 证据交付。
"写个把 CSV 转 JSON 的小工具" → backend-feature（S 档）：不读 playbook，明确验收 → 实现 → 自测主路径+边界 → 3 行证据交付。

> lora-mode 把"完成"定义为：真实运行、经过验证、没有假状态；把"快"定义为决策便宜，而不是验证打折。
