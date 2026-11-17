# file-pr: 用验证证据创建/更新 PR

> **适用**：PR 正文中需要放入验证媒体公开链接（截图、录屏、附件）；或用户明确要求「file-pr / 把链接和验证结果贴进 PR」。**主导工具**：`gh` + `file-upload` 的链接。**不替代** `pr-open`：Change map、独立审查和轮次预算仍在 `pr-open` 中执行，本 playbook 只补充证据链接的收集与排版。

## 与 tstack file-pr 的对应关系

本 playbook 沿用 tstack `file-pr` 的组织：先查同分支 PR 是否已存在 → 本地 diff 对照 base → 简短、以问题为先的标题 → PR 正文说明问题与解决方式 → 真实 PR 而非草稿 → 需要评论时走 `leaving-pr-comments`。差异在于：本流程要求把 `file-upload` 的链接和验证结果写进正文的证据区，并遵守本仓库 lora-mode 的 Mermaid Change map 与风险分级。

## 步骤

1. **收集链接与验证结果。** 从 `file-upload` 的输出取本次任务上传的链接和元数据。每条链接必须对应一个真实文件、一个验证动作和实际命令结果。缺任一项时先补全，不用占位链接或过期链接。链接取自本次上传的真实返回值；无法确认来源时不写入正文。
2. **核对 PR 状态。** 查目标分支是否已有 PR；只接续 head 与当前任务分支匹配的已有 PR。标题按仓库近期合并 PR 的惯例取，简洁说明问题或收益，避免复述 diff 的文件清单。
3. **写正文。** 沿用 `pr-open.md` 的最小格式：问题与解决方式、Change map（Mermaid）、Evidence、Risk and recovery。把媒体链接放进 `Evidence` 小节，按「证据区格式」排版。正文按 `engineering-writing` 起草、`unslop` 检查；不写密钥、令牌、内网或个人链接。
4. **独立审查与创建。** 审查、轮次预算、创建与核验、临时产物清点都按 `pr-open.md` 步骤 5–6 执行。本 playbook 不另开 reviewer，也不放宽 `pr-open` 的授权边界。真实 PR 必须包含本正文中的链接，且链接在 GitHub 预览中可点击。
5. **核验。** 用 `gh pr view` 读取已保存正文，确认链接、Mermaid 图和最新 SHA 均正确。打开至少一个媒体链接确认可访问；若链接不可访问，修复或移除后再交付。无法预览时说明未验证。

## 证据区格式

在 `pr-open.md` 的 `### Evidence` 小节内，命令结果之后追加媒体链接：

````markdown
### Evidence
`<实际命令>` → <观察到的结果；行为变化时说明前后差异>

**Verification media**

#### 1. <改动名称>
Before:

![before](<file-upload 返回的图片 url>)（temp，90 天）

After:

![after](<file-upload 返回的图片 url>)（temp，90 天）

#### 2. <下一项改动>
Before: ![before](<url>)（temp，90 天）
After: ![after](<url>)（temp，90 天）

Recording: [<文件名>](<url>)（temp，90 天）
````

排版规则：

- 截图必须用 `![alt](url)` 内嵌。禁止只写 `[before](url)`；普通链接只显示蓝字，不会渲染图片。
- 每项改动使用四级标题。每组图片独占段落，不在表格中放图片；表格会把大截图压成小缩略图，无法一目了然。
- 图片前后各留一个空行；`Before:` 和 `After:` 单独成行。这样 GitHub 才会渲染大图。
- 录屏优先上传 MP4 (H.264 + AAC)。GitHub 评论中的远程视频链接不保证内联播放；写可点击链接，并说明保留时长。不要把“可能播放”写成“已内联播放”。
- 每一行写明媒体类型、对应验证动作、链接和保留策略。顺序与验证执行顺序一致；窄屏与宽屏截图、动效录屏分别列出。
- 只列本次任务真实产生并上传的媒体；不列用户未授权公开的文件。
- `temp` 链接标注 90 天；`release` 链接标注长期。
- 链接缺失或上传受阻时，该行写「未上传：<原因>」，不隐藏失败状态。

## 仅更新现有 PR 正文

用户只要把链接和验证结果补进已有 PR 时不改代码：读取最新 body、head 和 diff，核实要补的链接真实有效，只更新 `Evidence` 段并保留其余准确内容。按 `pr-open.md` 的「仅更新现有 PR 正文」路径执行；不创建分支或 PR、不做代码 review、不运行无关测试。

## 移交

需要继续看 CI 或评论 → `pr-babysit.md`。媒体链接过期需重传 → 回到 `file-upload`。
