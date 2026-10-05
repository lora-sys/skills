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
| [`open-ppt`](skills/open-ppt/) | PPTD 格式的演示文稿创建、编辑与 PPTX/图片导出 | 幻灯片、PPT/PPTX、海报、infographic、教学演示 |
| [`samuel-video-coach`](skills/samuel-video-coach/) | Samuel 风格的短视频导演 Skill：分镜、台词、拍摄指导、AI 过渡与共鸣设计 | 抖音、TikTok、Reels、Shorts、Bilibili、YouTube 前期策划 |
| [`generate-image`](skills/generate-image/) | 使用七牛云 Modelink（GPT Image 2 / Gemini）生成或编辑图片 | 文生图、图编辑、多图合成、风格迁移、海报封面插画、透明底素材 |
| [`static-site-experience-release`](skills/static-site-experience-release/) | 静态个人站体验审查、交互精修、质量验证与 GitHub Pages 发布 | Astro / 静态作品集、博客、GitHub Pages 上线前验收 |
| [`html-stable-publish`](skills/html-stable-publish/) | 使用 Postplan 发布和更新 HTML draft | 需要发布单页 HTML 或静态页面，并获得可访问的 draft 链接 |
| [`chinese-ai-resume`](skills/chinese-ai-resume/) | 中文 AI Agent / LLM / 全栈简历的事实核验与 ATS 交付 | 由 GitHub 项目、经历和证据生成或修订中文简历 |
| [`github-gem-seeker`](skills/github-gem-seeker/) | 从 GitHub 寻找成熟开源方案 | 下载、格式转换、媒体处理、归档、爬取、CLI 等成熟问题 |
| [`web-development-team-playbook`](skills/web-development-team-playbook/) | Web 项目改造、审查、验收和发布门禁 | 网站、Web 应用、前端或全栈项目的团队级交付流程 |
| [`teaching-html-story-deck`](skills/teaching-html-story-deck/) | 单文件互动教学故事卡与讲解页 | 技术讲解、产品 walkthrough、课程页、架构可视化、录屏演示 |
| [`lora-visual`](skills/lora-visual/) | 统一的 lora 风格解释图与透明角色插画 | 概念图、工作流、对比图、Hero 配图和可复用角色素材 |
| [`unslop`](skills/unslop/) | 去除 AI 腔并增加自然的人类表达 | 文案、说明、博客、技术内容和沟通文本润色 |
| [`video-publisher`](skills/video-publisher/) | 多平台视频草稿自动化（小红书、抖音、Bilibili、微信视频号），默认停在发布前 | 视频上传、标题标签、原创声明、封面、发布前验收 |
| [`notion`](skills/notion/) | 通过官方 `ntn` CLI 操作 Notion 工作空间 | 读、搜、建、改 Notion 页面，查询数据源，上传文件，运行 Notion Workers |
| [`debug`](skills/debug/) | 根因修复纪律：复现→二分定位（git bisect / 路径中点观测 / pstack 栈采样）→假设→验证→最小修复，附真实教训库 | 修 bug、测试失败、接口不通、行为不符预期、性能回退、进程卡死挂起等一切排查场景 |

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
| `teaching-html-story-deck` | lora-sys 创建，MIT；原始许可文件保留于技能目录。 |
| `lora-visual` | 改编自 [oil-oil/oil-visual](https://github.com/oil-oil/oil-visual)，MIT；上游版权与许可见技能目录内的 `THIRD_PARTY_NOTICES.md`。 |
| `unslop` | 源自 [Cursor Plugins pstack/unslop](https://github.com/cursor/plugins/tree/main/pstack/skills/unslop)，作者 Lauren Tan，MIT；上游许可文件保留于技能目录。 |
| 其余技能 | 由 lora-sys 策展并作为本个人工作流集合的一部分维护。 |
| `notion` | 包装官方 [Notion CLI (`ntn`)](https://github.com/makenotion/notion-cli)，MIT；上游版权与许可见技能目录内的 `THIRD_PARTY_NOTICES.md`。 |
| `generate-image` | lora-sys 创建，MIT；改编自 [K-Dense-AI/claude-scientific-writer](https://github.com/K-Dense-AI/claude-scientific-writer) 的 `generate-image` skill（MIT），后端由 OpenRouter 换为七牛云 Modelink。 |
| `open-ppt` | lora-sys 创建，MIT；基于 PPTD 格式 + 浏览器端 WASM PPTX 写入器。 |
| `samuel-video-coach` | lora-sys 创建，MIT；改编自 Samuel 短视频导演方法论。 |
| `video-publisher` | 改编自 [oil-oil/video-publisher-skill](https://github.com/oil-oil/video-publisher-skill)，MIT；上游版权与许可见技能目录内的 `LICENSE`。 |

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
- **检测漂移**：任何一条同步之前，先看差异再动手：

```bash
# 找出两边不一致的技能
for s in skills/*/; do
  name=$(basename "$s")
  diff -rq "$s" "$HOME/.agents/skills/$name" >/dev/null 2>&1 || echo "DRIFT: $name"
done
```

规则：`skills/<skill-name>/SKILL.md` 在目录顶层、目录名与 frontmatter `name` 一致；提交前不允许有 `__pycache__/` 等未清理产物；同步时永远先 diff、确认差异来源（是仓库新改动还是安装副本的临时修改），再决定方向。
