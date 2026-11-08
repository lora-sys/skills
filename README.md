<p align="center">
  <img src="./assets/readme/hero.png" width="100%" alt="Lora Skills，可安装、可复用的个人 Agent Skills 集合">
</p>

一个由 **lora-sys** 维护的个人 Agent Skills 集合，面向个人作品集、AI 工程、内容表达、静态站发布与开源工具工作流。每个技能都是一个包含 `SKILL.md` 的独立目录，可通过 [`skills`](https://github.com/vercel-labs/skills) CLI 安装到 Codex、Claude Code、Cursor 等支持 Agent Skills 的工具中。

## 安装

先列出本仓库可用技能：

```bash
npx skills add lora-sys/skills --list
```

安装一个技能到当前项目的 Codex：

```bash
npx skills add lora-sys/skills \
  --skill static-site-experience-release \
  --agent codex
```

全局安装全部技能到 Codex：

```bash
npx skills add lora-sys/skills \
  --skill '*' \
  --agent codex \
  --global \
  --yes
```

`skills` 会把 Codex 的项目级技能安装到 `.agents/skills/`，或通过 `--global` 安装到 `~/.codex/skills/`。安装后可检查：

```bash
npx skills list --global --agent codex
```

## Skills

| Skill | 用途 | 适用场景 |
|---|---|---|
| [`lora-mode`](skills/lora-mode/) | 全流程工程路由器：按目标选路由，覆盖开发、调试、审查、PR/Issue 生命周期与合并清理 | 前后端研发、目标评测、自主闭环、PR 接手与跟进、注释清理（no-comment/comment-review） |
| [`review-loop`](skills/review-loop/) | 限轮数的独立代码审查循环，优先使用低成本模型，修复实质缺陷后再审 | 多轮独立复审、修复后复查 |
| [`modernize`](skills/modernize/) | 评估旧 PR 价值并给出 MODERNIZE、REWORK 或 CLOSE 建议 | 更新、rebase 或评估分叉已久的历史 PR |
| [`council`](skills/council/) | 并行收集三个独立 Provider 的只读评审意见并核实汇总分歧 | 明确要求跨模型评审或多方会诊 |
| [`leaving-pr-comments`](skills/leaving-pr-comments/) | 规范代表用户提交到 GitHub 的评论、回复与代理归属标识 | 撰写或发布 PR / Issue 评论与 review 回复 |
| [`create-formal-verification-skill`](skills/create-formal-verification-skill/) | 为高风险行为生成项目本地形式化验证模型与可复跑技能 | 并发、状态机、重试或常规测试难覆盖的协议与关键不变量 |
| [`maintain-formal-verification-skill`](skills/maintain-formal-verification-skill/) | 代码变更命中已有验证覆盖时，核对源码映射并维护模型 | 重构或修改已有形式化验证覆盖的代码 |
| [`statechart`](skills/statechart/) | 用 TLC 检查 TLA+ 状态机模型，输出最短违规路径与 Mermaid 状态图 | 状态迁移分析、协议检查、用状态路径解释 Bug |
| [`remote-dev`](skills/remote-dev/) | 在已配置的远端开发机执行依赖安装、测试与服务检查 | 明确要求远端验证或本地环境不具备运行条件 |
| [`engineering-writing`](skills/engineering-writing/) | 证据化工程写作规范，含英文 STE 启发式检查 | 起草或修改 PR / Issue 正文、技术文档与评审意见 |
| [`presentation-builder`](skills/presentation-builder/) | 创建与编辑 PPTD 项目，导出本地 PPTX 与图片 | 演示文稿、幻灯片、海报、信息图设计与生成 |
| [`short-video-director`](skills/short-video-director/) | 叙事类短视频前期策划：故事内核、分镜脚本、拍摄指导与剪辑地图 | 技术讲解、产品演示与自媒体短视频前期设计 |
| [`generate-image`](skills/generate-image/) | 调用七牛云 Modelink（GPT Image 2 / Gemini）生成、编辑或合成位图 | 文生图、图像修改、风格迁移、海报插画与配图 |
| [`static-site-experience-release`](skills/static-site-experience-release/) | 基于分支工作流的静态站体验审查、交互精调与发布验收 | 个人站、作品集、博客与 GitHub Pages 上线交付 |
| [`html-communication`](skills/html-communication/) | 通过 Postplan 发布或更新自包含 HTML 草稿并返回链接 | 在线分享 HTML 报告、教学页、交互图表或静态演示 |
| [`chinese-ai-resume`](skills/chinese-ai-resume/) | 基于真实项目与工程证据生成中文 ATS 友好的单页简历 | AI Agent、LLM 应用与全栈岗位的简历创建或精修 |
| [`github-gem-seeker`](skills/github-gem-seeker/) | 在 GitHub 检索高星成熟开源方案，避免重复造轮子 | 格式转换、媒体处理、爬虫、归档与 CLI 工具选型 |
| [`interactive-teaching-page`](skills/interactive-teaching-page/) | 生成自包含交互式教学 HTML 页面（故事叙事、内嵌 SVG、演示备注） | 技术知识点讲解、架构可视化与产品 Walkthrough |
| [`lora-visual`](skills/lora-visual/) | 生成统一风格的解释图与透明背景角色插画 | 概念图、架构图、对比图、Hero 插图与素材制作 |
| [`unslop`](skills/unslop/) | 去除文本中的 AI 套话与冗余表达，还原直接自然的人类文风 | 文案、说明、博客、技术内容和沟通文本润色 |
| [`video-publisher`](skills/video-publisher/) | 多平台视频草稿准备与上传自动化，发布前由人工确认 | 小红书、抖音、B 站、视频号的视频与文案草稿发布 |
| [`notion`](skills/notion/) | 通过官方 ntn CLI 操作 Notion 工作区 | 读写页面、检索内容、管理数据库、上传文件与运行 Worker |
| [`debug`](skills/debug/) | 根因定位与最小修复纪律：二分排查、假设验证、拒绝表面掩盖 | 排查 Bug、崩溃卡死、测试失败、接口异常与性能回退 |
| [`oil-frontend`](skills/oil-frontend/) | 前端工程实现规范：界面、交互、状态数据流与组件组织 | 前端功能实现、组件重构与代码级交互交付（不负责主视觉设计） |
| [`oil-ui`](skills/oil-ui/) | UI 视觉设计规范：设计方向探索、同屏多风格对比与视觉层级精修 | 新界面设计、风格探索、截图还原与视觉评审 |

## Codex 安装提示词

将下面这段提示词粘贴到 Codex 中，即可让它安装所有 Lora Skills：

```text
请通过 Skills CLI 将 lora-sys/skills 中的全部技能全局安装到 Codex。
执行：
npx skills add lora-sys/skills --skill '*' --agent codex --global --yes

完成后执行：
npx skills list --global --agent codex

请列出已安装的技能名称；若某一步失败，请保留错误输出并说明需要的权限或依赖。不要修改其他项目文件。
```

也可直接使用仓库内的 [`docs/CODEX_INSTALL_PROMPT.md`](docs/CODEX_INSTALL_PROMPT.md)。

## 目录结构

```text
lora-skills/
├── README.md
├── LICENSE
├── docs/
│   └── CODEX_INSTALL_PROMPT.md
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        └── optional scripts/, references/, assets/, templates/
```

Skills CLI 会发现 `skills/<skill-name>/SKILL.md`。每个 `SKILL.md` 的目录名、frontmatter `name` 与安装时使用的 `--skill` 名称保持一致。

## 来源与许可证

本仓库的集合元数据与自有技能以 MIT 许可证发布。技能可能携带自己的许可证或上游归属，使用时应以对应技能目录中的 `LICENSE` 为准。

| Skill | 来源与归属 |
|---|---|
| `interactive-teaching-page` | lora-sys 创建，MIT；原始许可文件保留于技能目录。 |
| `lora-visual` | 改编自 [oil-oil/oil-visual](https://github.com/oil-oil/oil-visual)，MIT；上游版权与许可见技能目录内的 `THIRD_PARTY_NOTICES.md`。 |
| `unslop` | 源自 [Cursor Plugins pstack/unslop](https://github.com/cursor/plugins/tree/main/pstack/skills/unslop)，作者 Lauren Tan，MIT；上游许可文件保留于技能目录。 |
| `lora-mode` | lora-sys 维护；接手流程参考 [t3dotgg/tstack takeover](https://github.com/t3dotgg/tstack/blob/main/skills/takeover/SKILL.md)，注释审查、盲测、变更影响验证和重复问题的结构化修复参考 [backnotprop/pstack](https://github.com/backnotprop/pstack)，均按本仓库流程与授权边界改写。 |
| `modernize` / `council` / `leaving-pr-comments` | 改编自 [t3dotgg/tstack](https://github.com/t3dotgg/tstack/tree/1085050f3baed1ac724caa4a8166145fb2ac88af/skills)，MIT；各技能目录保留上游 LICENSE，流程按 lora-mode 的审查、授权与 PR 规则改写。 |
| 其余技能 | 由 lora-sys 策展并作为本个人工作流集合的一部分维护。 |
| `notion` | 包装官方 [Notion CLI (`ntn`)](https://github.com/makenotion/notion-cli)，MIT；上游版权与许可见技能目录内的 `THIRD_PARTY_NOTICES.md`。 |
| `generate-image` | lora-sys 创建，MIT；改编自 [K-Dense-AI/claude-scientific-writer](https://github.com/K-Dense-AI/claude-scientific-writer) 的 `generate-image` skill（MIT），后端由 OpenRouter 换为七牛云 Modelink。 |
| `presentation-builder` | lora-sys 创建，MIT；基于 PPTD 格式 + 浏览器端 WASM PPTX 写入器。 |
| `short-video-director` | lora-sys 创建，MIT；改编自 Samuel 短视频导演方法论。 |
| `video-publisher` | 改编自 [oil-oil/video-publisher-skill](https://github.com/oil-oil/video-publisher-skill)，MIT；上游版权与许可见技能目录内的 `LICENSE`。 |
| `create-formal-verification-skill` / `statechart` | 源自 [Cursor Plugins pstack](https://github.com/cursor/plugins/tree/4dd1d05818d19792e7cd6e818f1667f95f7e1dbe/pstack/skills)，作者 Lauren Tan，MIT；版权与许可见各技能目录中的 `LICENSE`；形式化验证的破坏性复测限定在临时副本；`statechart` 含本地工具路径、整数精度、区间内存与安装授权保护。 |
| `oil-frontend` | 源自 [oil-oil/oil-frontend](https://github.com/oil-oil/oil-frontend)，MIT；以镜像方式跟踪上游，每日自动同步。 |
| `oil-ui` | 源自 [oil-oil/oil-ui](https://github.com/oil-oil/oil-ui)，MIT；以镜像方式跟踪上游，每日自动同步。 |

## 维护

添加技能时，将目录置于 `skills/<skill-name>/`，确保其中包含带有有效 YAML frontmatter 的 `SKILL.md`。提交前运行：

```bash
npx skills add . --list
```

不要把测试截图、临时构建产物、真实密钥、私有数据或用户文件放进仓库。对于带脚本的技能，请在 README 或技能正文中说明其执行边界和验证方法。

### 仓库 ↔ 本机安装的同步约定

本仓库是所有技能的**唯一事实来源**；本机安装副本位于 `~/.agents/skills/<skill-name>/`（ZCode / Claude Code 等都从这里发现技能）。两个方向各有规则：

- **发布（仓库 → 安装）**：仓库里的修改完成后，把技能目录同步到安装位置。整目录覆盖即可（skills CLI 的 `npx skills add . --skill <name>` 也会做同样的事）。
- **回写（安装 → 仓库）**：在会话中直接修改了某个已安装技能（修 bug、改 description 等）之后，必须把改动写回仓库，否则下次发布就会把修复覆盖掉。做法：先 diff 找出漂移，再把确认过的文件拷回仓库。
- **上游镜像（`oil-frontend` / `oil-ui`）**：这两个目录是 [oil-oil](https://github.com/oil-oil) 上游的镜像，由 [`.github/workflows/sync-oil.yml`](.github/workflows/sync-oil.yml) 每日自动同步并整目录覆盖——**不要手改这两个目录**，手改会被下次同步覆盖；上游更新后，本机安装副本重新安装即可（`npx skills add lora-sys/skills --global`）或按发布流程同步。
- **检测漂移**：任何一条同步之前，先看差异再动手：

```bash
# 找出两边不一致的技能
for s in skills/*/; do
  name=$(basename "$s")
  diff -rq "$s" "$HOME/.agents/skills/$name" >/dev/null 2>&1 || echo "DRIFT: $name"
done
```

规则：`skills/<skill-name>/SKILL.md` 在目录顶层、目录名与 frontmatter `name` 一致；提交前不允许有 `__pycache__/` 等未清理产物；同步时永远先 diff、确认差异来源（是仓库新改动还是安装副本的临时修改），再决定方向。
