> **草稿（v0.3 开发为核，未安装）**：这是 `skills/lora-mode/SKILL.md` 的正文草稿，供审查。
> v0.2 → v0.3：按反馈"lora-mode 主要就是开发（分前端、后端），核心是开发流程（调试等）"——description 重写为开发触发面；纯后端/桌面/移动端不再排除，新增 backend-feature 薄 playbook；deck、video 移出主触发面（点名时才进入）；playbook 共 15 个。
> 批准后：去掉本行说明，将正文（自 frontmatter 起）落盘为 `skills/lora-mode/SKILL.md`。

---
name: lora-mode
description: lora 的个人开发总控模式，覆盖前后端与全栈开发的核心流程——新建或改造项目与功能、编码实现、调试与修 bug、技术调查与选型、验收与发布上线。凡涉及写代码、改代码、排查问题或发布的任务，包括前端界面、后端服务、API、脚本工具、自包含 HTML 页面，都先进本模式选 playbook，再按 playbook 调度具体 skill；前端的设计、实现、视觉精修、发布另有具体 playbook。用户说"lora-mode""lora 模式""按你的流程跑"时必须使用。单个 skill 能直接完成的小请求（出一张图、查一次 Notion、读个页面、改一句话）不套本模式；演示文稿、短视频、简历等非开发交付默认直接路由对应 skill，用户点名走流程时才进入本模式。
---

# lora-mode — 个人开发总控

lora-mode 是任务入口，不是实现手册。它只做三件事：**判定任务类型、选中并整篇读取对应 playbook、按 playbook 调度具体 skill 执行**。跳过 playbook 直接动手是错误用法。

**playbook 与 skill 的关系**：playbook 是任务型流程，定义"分几步、每步谁来做、怎么验收"；skill 是工人，在被调度的步骤里干活。没有 skill 需要专属 playbook——全部 skill 的位置见"分工速查"。

## 使用规则

1. **先路由，后动手。** 按"任务路由表"选出最贴合的 playbook，读取整个 playbook 文件后再开始工作。两个 playbook 都沾边时，选更接近最终交付物的那个，并在 todo 里注明选择理由。
2. **把 playbook 变成 todo。** 读完 playbook 后，把它的步骤原样建成 todo 列表，逐条执行、逐条勾掉；不合并、不改名、不省略（playbook 自己声明可合并/跳过的除外）。
3. **按步骤加载 skill。** 步骤指明用某个 skill 时，必须真正加载后再动工，不得凭印象替代其行为。skill 与 playbook 冲突时以 skill 为准；skill、playbook 与本文件"硬边界"冲突时，以硬边界为准。
4. **保持粘性。** 对话跨多轮时，新消息仍属同一 playbook 范围就继续按它走，不需要用户重复点名；任务范围变了才重新路由并说明。
5. **路由不了就声明假设。** 没有完全匹配的 playbook 或路由行时，选最近的一个，在 todo 首条声明"按 X 近似处理"。
6. **按移交走。** playbook 结尾声明"下一步移交"时（ui-design 选定方向 → web-feature；web-feature、static-site-release → publish；teaching-page → publish；deck、video 收尾 → notion 归档可选），只移交产物与验收状态，不重开计划。

## 七步通用骨架（所有 playbook 继承）

识别现状 → 核实事实 → 先出计划 → 最小实施 → 验收 → 隔离对抗审查 → 按证据交付

- 各 playbook 负责把每步填具体："识别现状"在 web-feature 里是读仓库约定与依赖，在 deck 里是读输入材料与目的，在 bug-fix 里是最小复现。
- 小任务可由 playbook 声明合并或跳过审批式步骤（计划、对抗审查）；**"验收"和"按证据交付"任何 playbook 不得跳过**。
- 对抗审查的完整协议见 `references/review-protocol.md`。

## 任务路由表

| 任务特征 | playbook |
|---|---|
| 新建或改造前端 / 全栈 Web 功能、页面 | `playbooks/web-feature.md` |
| 后端服务、API、脚本与工具的开发 | `playbooks/backend-feature.md` |
| 设计方向探索、多风格对比、界面评审 | `playbooks/ui-design.md` |
| 截图还原、视觉精修、像素级对齐 | `playbooks/visual-refinement.md` |
| bug、报错、崩溃、行为不符、性能回退、"为什么" | `playbooks/bug-fix.md` |
| 抛弃型原型：只为便宜地定设计/行为决策 | `playbooks/prototype.md` |
| 教学/讲解/演示类自包含 HTML | `playbooks/teaching-page.md` |
| 单页 HTML 要公开链接，或把站点发出去 | `playbooks/publish.md` |
| 已上线静态站的体验改造、审计与发布 | `playbooks/static-site-release.md` |
| 演示文稿、幻灯、海报、信息图（点名时） | `playbooks/deck.md` |
| 短视频策划到多平台草稿分发（点名时） | `playbooks/video.md` |
| 写新 SKILL.md 或改进现有 skill（用户点名时） | `playbooks/skill-authoring.md` |
| 只读调查、技术选型、"这是怎么做到的" | `playbooks/investigation.md` |
| 接手、恢复、继续之前的工作 | `playbooks/session-pickup.md` |
| 长任务需要无人值守跑完 | `playbooks/autonomous-run.md` |

deck、video 默认不进本模式：单件 PPT 直接调度 open-ppt，单条视频策划直接调度 samuel-video-coach；只有需要串联配图、发布、归档等下游步骤时才走对应 playbook。

**路由行（不设 playbook，直接调度对应 skill）**：简历 → chinese-ai-resume；Notion 读写 → notion；找现成开源方案 → github-gem-seeker；lora/Mochi 角色图 → lora-visual；普通位图 → generate-image。

## 常开纪律（任何 playbook 内都生效）

- **unslop**：所有用户可见文字——回复、说明、UI 文案、标题与封面文案——交付前按 unslop 过一遍。
- **debug**：一旦出现"行为与预期不符"，无论执行到哪个 playbook 的哪一步，先停下按 debug 纪律复现，再决定是否继续原流程。

## 硬边界（任何 playbook 不得越过）

- 不可逆外发操作——真实部署、生产发布、公开发布网页、付费资源、代点最终发布按钮——必须取得用户在**本次任务中**的明确确认；此前的授权不传递。
- 除非用户明确要求，不创建 Pull Request；本地提交（commit）也只在用户要求或仓库惯例明确允许时做。
- 不伪造证据：未执行的检查不得写成通过；截图必须是真实运行产物；AI 生成图片必须标注，不得充当运行证据。
- 凭据只从环境变量或用户指定来源读取，绝不写入产物、仓库或命令行参数。
- 对抗审查者保持零上下文：不读用户需求、计划、Git 历史、既有测试（`references/review-protocol.md`）。

## 原则索引

按需应用；与 playbook 冲突时以 playbook 为准：

1. **最小正确变更** —— 一切实现。能不加就不加，能删就删；相邻问题记录在案，不顺手修。不引入不存在的抽象。
2. **真实产物证明** —— 任何"完成"之前。完成只认运行产物：真实构建/测试输出、浏览器里实际点过、校验脚本通过、前后截图。代码读起来对不算对。
3. **根因优先** —— 一切异常。先复现、再假设、在根因处修（→ debug）；机制不明的"好了"不算好。
4. **数据形状先行** —— 写逻辑之前。先写下状态与数据结构（字段、转换、边界态），再写实现。
5. **状态诚实** —— 一切界面与产物。加载/成功/已保存/在线必须有底层事实支撑；禁止假成功 UI 与假数据。
6. **先比较后动手** —— 设计类决策。并排 2–3 个方案让用户选（oil-ui 对比页、open-ppt 设计方向）；决策便宜的先做 prototype。
7. **体验优先** —— 交付前。少而完整胜过多而粗糙；每次交付前做一次减法。
8. **上下文卫生** —— 长任务、大范围搜索。批量读取交给子代理，主线程只留结论与决策。
9. **不阻塞人** —— 全程。可逆决定直接做并留痕；只有硬边界才停下问。
10. **杠杆优先** —— 同样的事第三次出现。做成脚本、skill 或 playbook，不再靠口头重复。
11. **教训进结构** —— 复盘时。反复出现的坑写进对应 skill、references 或 debug 的 lessons，而不是记在心里。
12. **证据化沟通** —— 每次交付。回复以事实开头：做了什么、怎么验证的、明确没做什么；不虚构链接与数字。

## 分工速查（全部 skill 的位置）

| 档位 | skill | 在哪干活 |
|---|---|---|
| 常开纪律 | unslop | 所有用户可见文字交付前过一遍 |
| 常开纪律 | debug | 行为异常时随时接管；根因纪律与 lessons 沉淀 |
| playbook 主导 | oil-frontend | web-feature / visual-refinement / bug-fix 的实现步骤 |
| playbook 主导 | oil-ui | ui-design 主导；web-feature 设计先行；visual-refinement 设计判断 |
| playbook 主导 | static-site-experience-release | static-site-release 全程 |
| playbook 主导 | teaching-html-story-deck | teaching-page 主导 |
| playbook 主导 | open-ppt | deck 主导（PPTD→pptx 双产物、视觉 QA） |
| playbook 主导 | samuel-video-coach | video 前半：选题、脚本、分镜、封面文案 |
| playbook 主导 | video-publisher | video 后半：四平台草稿分发，停在最终发布按钮前 |
| playbook 主导 | html-stable-publish | publish（单页）主导；teaching-page 的发布出口 |
| playbook 主导 | skill-creator | skill-authoring 主导 |
| 步骤 / 路由行 | lora-visual | 需要 lora/Mochi 角色一致性的图；deck、video、teaching-page 的配图步骤 |
| 步骤 / 路由行 | generate-image | 普通位图后端；lora-visual 的底层；deck/video 封面素材；生成后回读检查 |
| 步骤 / 路由行 | github-gem-seeker | investigation 的找方案步骤；也可直接路由 |
| 步骤 / 路由行 | notion | 各 playbook 收尾归档（可选）；日常读写直接路由 |
| 路由行 | chinese-ai-resume | 简历任务直接调度，不套长流程 |
| 交付步骤 | github:commit / github:pr | 仅用户要求时提交/建 PR |
| 平台能力 | browser-use:control-browser / web-gui-tester | Web 家族的浏览器实测与黑盒测试 |
| 平台能力 | playwright-cli | 备选浏览器自动化 |
| 平台能力 | Explore / general-purpose 子代理 | 只读侦察、隔离对抗审查（见"子代理与并行"） |
| 平台能力 | 官方 docx / xlsx / pdf / pptx skill | 读、改各类文档；做 PPT 仍默认 open-ppt |

注：browser-use、playwright-cli、skill-creator、github:*、官方文档 skill 是平台侧能力；本仓库 skill 经 skills CLI 分发到其他 agent 工具时，这几行按目标工具替换。

## 子代理与并行

- 只读侦察（多文件、多目录）→ Explore 子代理：让它回结论，不回文件内容。
- 隔离对抗审查 → 新开 general-purpose 子代理，只给代码快照与可运行产物，不给需求/计划/历史（review-protocol）。
- Web 界面的视觉验收用浏览器真实截图（窄屏+宽屏）；渲染类 visual-judge 子代理只用于 pptx/docx/xlsx/pdf 等渲染交付物。
- 长命令（构建、批量生成、导出）→ 后台运行，主线程继续别的步骤。
- 多子代理编排（dynamic workflows）只在用户明确要求"workflow"时使用。
- 子代理没有本对话记忆：派活 prompt 必须自包含——任务、绝对路径、期望产物、边界。

## 交付

每轮交付按"交付摘要"汇报：已完成、计划与范围、验证证据、审查核验、限制、发布状态。通用要求只有一条：**证据必须是真实产物**——真实命令输出、真实截图/录屏、真实校验脚本结果；"检查未发现问题"不是证据。各 playbook 定义自己的证据形态（Web：前后截图与视口；deck：导出图 QA；video：check-package/verify 输出）。

## 参考文件导航（核心仅一份）

| 文件 | 何时读取 |
|---|---|
| `references/review-protocol.md` | 每轮实现或修复后执行隔离对抗审查；强制。 |

Web 专属 references（quality-gates、design-motion、common-pitfalls、stack-selection）不在本目录，由 web-feature 家族的 playbook 按需引用。

## 示例

例 1（Web 链）："给我的博客首页加个目录" → `web-feature`：
① 读仓库确认栈与约定 → ② 核实框架文档 → ③ 出计划（目录放哪、锚点滚动、移动端折叠、验收项）→ ④ 小改动不启 oil-ui 全流程，记录原因 → ⑤ oil-frontend 实现最小变更 → ⑥ 浏览器窄宽屏截图验收 → ⑦ 隔离对抗审查 → ⑧ 证据化交付。

例 2（内容链）："把这篇笔记做成短视频发抖音和B站" → `video`：
① samuel-video-coach：选题盘点 → 故事发动机 → 逐字口播 → 逐镜头分镜（校验脚本通过）→ ② generate-image：出封面素材 → ③ video-publisher：check-package 校验 → 并行上传四平台 → 草稿停在最终发布按钮前 → ④ 可选 notion 归档选题。全程文案过 unslop。

> lora-mode 把"完成"定义为：以最小必要变更交付真实运行、经过验证、可维护且没有假状态的成果；把"快"定义为决策便宜（原型、并排方案），而不是验证打折。
