# web-development-team-playbook 内容审计（lora-mode 通用化 · 待审查）

> 背景反馈（2026-10-06）：lora-mode 不是 Web 开发手册，而是**通用总控模式**——它组织的 skill 不限于开发类；多做一些 playbook 把各条链路串起来。
> 因此本文件逐节处置原手册内容：**留**（泛化后进 lora-mode 核心）/ **挪**（下沉到具体 playbook 或 reference）/ **删**（已有 skill 覆盖，或范围不符）。
> 你确认后我出 lora-mode SKILL.md **v0.2（通用版）** + 全部 playbook 文件。

## 一、SKILL.md 正文逐节审计

| # | 原文内容（要点） | 处置 | 去向 / 理由 |
|---|---|---|---|
| 0 | frontmatter description（"团队级 Web 开发手册"触发面） | **删·重写** | 通用化后触发面整体重写；"团队级"身份退役 |
| 1 | "仅作为强制交付流程：先理解 → 计划 → 实施 → 验证 → 隔离审查 → 交付" | **留（泛化）** | 升格为 lora-mode 通用执行骨架（见第三节"七步骨架"） |
| 2 | 不为新技术迁移稳定架构；不被要求不扩大任务 | **留（泛化）** | 已并入原则 1「最小正确变更」；架构迁移警告下沉 web-feature |
| 3 | 优先复用成熟工具/上游模式；不重写标准能力（聊天 UI、Canvas、流式） | **拆** | 前半句 → 骨架/原则通用化；聊天 UI、Canvas、流式等产品型 Web 例子 → 删（你的产出以静态站/单页为主） |
| 4 | 不加不存在的抽象；显式状态转换；隔离第三方差异；Canvas 高频交互可响应 | **拆** | 抽象警告 → 并入原则 1；状态转换/第三方隔离/Canvas → oil-frontend 的 references 已覆盖前端实现纪律 → 删 |
| 5 | 工作流① 识别任务和现状 | **留（泛化）** | 骨架第 1 步 |
| 6 | 工作流② 确认技术事实（查官方文档，不凭记忆） | **留（泛化）** | 骨架第 2 步 |
| 7 | 工作流③ 先输出计划（目标/非目标、页面组件、状态、风险、验收、部署） | **留·拆** | 骨架第 3 步；"页面/组件/部署状态"等 Web 字段下沉 web-feature 计划模板 |
| 8 | 工作流④ 实施最小正确变更 | **留（泛化）** | 骨架第 4 步 |
| 9 | 工作流⑤ 质量验收（读 quality-gates.md） | **留·拆** | 骨架第 5 步 = 验收；quality-gates.md 本身下沉 web-feature |
| 10 | 工作流⑥ 隔离对抗审查（读 review-protocol.md） | **留（泛化）** | 骨架第 6 步；review-protocol.md 措辞泛化后成为 lora-mode 通用 reference |
| 11 | 工作流⑦ 按证据交付 | **留（泛化）** | 骨架第 7 步 + 交付模板 |
| 12 | 技术选型表（Next.js / Vite / TanStack Start / Router / Query / Table / R3F / Effect）+ Vite+ 优先规则 | **删或下沉（待定）** | 纯 Web 栈决策，与通用模式无关。A：下沉 `web-feature/references/`；B：直接删。**倾向 B**——除非你确认在用 TanStack/Effect/Vite+ 这套 |
| 13 | 实现标准·类型与输入（防 any、验证外部输入） | **删** | 前端实现纪律由 oil-frontend 承接，不在通用手册重复 |
| 14 | 实现标准·状态诚实（spinner/成功/在线不造假） | **留（泛化）** | 已是 lora-mode 原则 5 |
| 15 | 实现标准·注释与可维护性 | **删** | 与平台内建规则重复（注释只解释意图/约束/非直观行为） |
| 16 | 实现标准·可用性与响应式（读 design-motion.md） | **挪** | design-motion.md 下沉为 web-feature、visual-refinement 共用 reference |
| 17 | 实现标准·用户可见变更证据（前后截图/录屏） | **留（泛化）** | 并入骨架第 7 步：任何用户可见交付物都要证据 |
| 18 | 实现标准·媒体资产（大文件不进构建目录） | **删** | generate-image / lora-visual / html-stable-publish 各自已有资产与发布约束 |
| 19 | Git、PR 纪律（遵循仓库约定；不擅自建 PR） | **留（泛化）** | 已并入 lora-mode 硬边界 |
| 20 | 自动审查结论当主张核验，不为取悦机器人改正确代码 | **留（泛化）** | 并入骨架第 6 步核验规则 |
| 21 | 部署/发布门禁：不可逆操作需本次明确确认；细节按项目定不写死 | **留（泛化）** | 已并入硬边界（覆盖所有外发：网页发布、视频平台草稿确认、Notion 破坏性编辑…） |
| 22 | 参考文件导航表 | **改** | 随各 reference 处置更新（见第二节） |
| 23 | 禁止事项 7 条 | **拆** | 6 条已被骨架/原则/硬边界吸收；"透明背景对比度、不可达导航"两条下沉 web reference；"假成功 UI"已在原则 5 |
| 24 | 尾注："快速完成"的定义 | **留（已改写）** | lora-mode v0.1 草稿尾注已是泛化版 |

**一句话总结：原手册真正通用的是"必做工作流 7 步 + 不可逆确认 + 不伪造证据 + 对抗审查"这一套纪律（约占正文一半）；另一半（选型表、TS/注释/媒体资产、Canvas/流式例子、SEO/响应式细节）是 Web 专属，下沉或删除。**

## 二、references/ 5 个文件的处置

| 文件 | 内容 | 处置 | 去向 |
|---|---|---|---|
| quality-gates.md | 8 道门禁顺序 + 证据矩阵 + 交付摘要模板 | **拆** | 通用精神（真实命令、证据矩阵思想、交付模板、"没发现问题不是证据"）进 lora-mode 核心交付节；8 道门禁矩阵是 Web 的 → 下沉 `web-feature/references/quality-gates.md` |
| review-protocol.md | 零上下文隔离审查协议 + 强制维度表 | **留（泛化）** | 改为 `lora-mode/references/review-protocol.md`："Web 实现"→"实现"；维度表中路由/响应式等 Web 专属行标注适用范围，其余通用保留 |
| stack-selection.md | Web 框架选型决策表 + Vite+ 规则 | **删或下沉（待定）** | 同正文第 12 条，等你拍板 |
| design-motion.md | 视觉/布局/响应式/导航/动效/无障碍标准 | **下沉** | web-feature 与 visual-refinement 共用 reference |
| common-pitfalls.md | 前端实现常见坑（对比度、主题语义色、SVG 背景…） | **下沉** | `web-feature/references/` |

## 三、通用化后的 lora-mode 结构（v0.2 提案）

### 七步通用骨架（所有 playbook 继承，源自原手册"必做工作流"）

识别现状 → 核实事实 → 先出计划 → 最小实施 → 验收 → 隔离对抗审查 → 按证据交付

每步的具体动作由各 playbook 填充；小任务可由 playbook 声明合并/跳过其中审批式步骤。

### playbook 地图（17 个，三个家族）

**开发类（8，即 v0.1 已有的 Web 部分）**
web-feature / ui-design / visual-refinement / prototype / bug-fix / investigation / static-site-release / publish

**内容创作类（6，新增——回应"skills 不一定非得跟开发相关"）**
- **deck** —— 演示/海报/信息图：open-ppt（PPTD→pptx 双产物、视觉 QA）⇄ lora-visual、generate-image 配图，文案过 unslop
- **video** —— 短视频全链：samuel-video-coach 策划 → generate-image 封面素材 → video-publisher 四平台草稿（停在最终发布按钮前）→ 可选 notion 归档
- **visual-asset** —— 图像资产：lora/Mochi 角色图走 lora-visual，普通图走 generate-image；生成后必须回读检查
- **teaching-page** —— teaching-html-story-deck →（需要角色图时 lora-visual）→ html-stable-publish
- **resume** —— chinese-ai-resume（事实核验 + ATS 交付）
- **knowledge** —— 记录/沉淀：notion；也可作为其他 playbook 的收尾步骤

**元类（3）**
skill-authoring / session-pickup / autonomous-run

### 串联规则（playbook 之间的交接）

- 每个 playbook 结尾声明"下一步移交"：ui-design 选定方向 → web-feature；web-feature 完成 → publish / static-site-release；teaching-page → publish；deck、video 收尾 → knowledge 归档（可选）。
- 交接只移交产物与验收状态，不重开计划。

### 触发面调整（通用化的代价与对策）

- description 从"Web 开发"改为"多步交付型任务的通用总控"；**单 skill 能直接完成的小请求（读个页面、改一句话、出一张图）不套模式**，避免与 open-ppt / samuel-video-coach / generate-image / notion 等自动触发打架。

## 四、需要你拍板的 4 件事

1. **stack-selection.md 的命运**：A 下沉为 web reference（你在用 TanStack/Effect/Vite+ 这套）/ B 直接删（Web 产出主要是静态站与单页 HTML）。我倾向 B。
2. **playbook 地图**：17 个有没有多/少？resume、knowledge 这类单 skill 流要独立 playbook，还是只做路由行？
3. **触发面写法**：确认"通用总控 + 小任务不套模式"这个边界。
4. **内容创作链要不要纳入 lora-mode 触发**：v0.1 的写法是"非 Web 交付直接路由、不套模式"；你这次的反馈听起来是要"管起来"。我按"管"画了地图，确认一下。

## 五、拍板记录（2026-10-06）

1. stack-selection.md → **A**：保留，下沉为 `web-feature/references/stack-selection.md`。
2. resume、knowledge、visual-asset → **路由行**，不设独立 playbook；playbook 总数 17 → 14（开发 8 + 内容 2 + 元类 3 + ……）即：web-feature、ui-design、visual-refinement、prototype、bug-fix、static-site-release、publish、teaching-page、deck、video、skill-authoring、investigation、session-pickup、autonomous-run。
3. 触发面 → 按"通用总控 + 单 skill 小请求不套模式"写入 v0.2，使用中可调。
4. 内容创作链 → 默认纳入：deck、video 留作 playbook（真·多 skill 链），其余降为路由行；不好用再删。

v0.2 已落盘：`docs/drafts/lora-mode-SKILL-draft.md`。

## 六、二次反馈（2026-10-06，v0.3）

反馈："这个描述不是很好——lora-mode 主要就是开发，分前端、后端，前端有具体的 playbook；核心是开发流程，调试等。"

处置：
1. description 重写为**开发触发面**：写代码/改代码/排查/发布才触发；演示文稿、短视频、简历移出主触发面，点名时才进入。
2. **后端不再排除**：删除"纯后端/API、桌面、移动端不使用"；新增 `backend-feature.md` 薄 playbook（七步骨架去掉 UI 步骤，实现 + 测试 + debug 为主）。playbook 总数 15。
3. deck、video 保留 playbook 但标注"点名时"，正文说明其默认直接调度 open-ppt / samuel-video-coach。

## 七、实测记录（2026-10-06，15/15 通过）

15 个 playbook 各由一个独立子代理实测（真实沙箱、真实运行产物）：

| playbook | 结果 | 要点与催生的修复 |
|---|---|---|
| visual-refinement | ✅ | 真改样式+双视口前后对比图；催生 review-protocol 降级规则、截图通道降级 |
| web-feature | ✅ | 无人点名自然触发 lora-mode→web-feature；真实验证边界值/键盘/reduced-motion；催生缓存与触发状态取证补充 |
| backend-feature | ✅ | 6 条真实运行输出；对抗审查抓到 GBK 解码裸崩并修复；修 investigation 路标 |
| ui-design | ✅ | 真建 4 卡对比页+双视口截图；发现 oil-ui 双装冲突（环境问题） |
| bug-fix | ✅ | 壳/内核分层按设计工作；先红后绿挖出"静默错值"根因；补教训沉淀降级+测试形态 |
| prototype | ✅ | 可点原型+决策记录；补结论落点 decision-record.md |
| teaching-page | ✅ | validate_deck 11/11；审查抓到 reduced-motion 叠页真 bug |
| publish | ✅ | 硬边界精确拦截：preflight 真跑、连 whoami 都不执行、命令与问题备好 |
| static-site-release | ✅ | 真审计抓 P0；Lighthouse 抓到自引入的对比度回归改到 100；识破缓存假证据；补零构建预览定义 |
| deck | ✅路由 | 按规则未进 playbook（单件直调 open-ppt），设计行为；暴露 open-ppt 导出链缺口，已写入 deck.md 已知缺口 |
| video | ✅ | 分镜校验通过、unslop 真改文案、check-package 正确报 onboarding 未完成；补 onboarding 顺序/封面规格/确认机制 |
| skill-authoring | ✅ | skill-creator 真主导；pypdf 实测页序/拒绝/--force；补子代理逐条组织+跨工具说明 |
| investigation | ✅ | 全程零修改；诚实结论+真实来源链；补"为什么"路由消歧、Explore 降级、gem-seeker 分工 |
| session-pickup | ✅ | 双证据重建现场，真续作 4 条路径实测；补无应答场景+小 diff 压缩 |
| autonomous-run | ✅ | 决策留痕+真实验收，无画蛇添足；补审查条件对齐 |

环境发现（待用户处理）：
1. oil-ui 在 .zcode/skills 与 .agents/skills 双份同名，Skill 工具拒调——建议去重。
2. open-ppt 导出链依赖的 open-ppt-skill npm 包在 npmjs/镜像均 404——open-ppt 需自带 editor/WASM 或提供降级路径。
3. browser-use 的 node_repl 通道在子代理环境不可用，playwright-cli+系统 Edge 可用——已写入降级链。

原 web-development-team-playbook 已退役：references 迁入 lora-mode/references/web/，纪律升格为骨架/硬边界/原则，README 行已删，git 历史可恢复。
