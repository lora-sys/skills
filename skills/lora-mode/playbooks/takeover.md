# takeover — 接手既有工作

> 适用：用户要求接手他人的 PR、分支或 Agent 线程。当前用户自己的任务恢复走 `session-pickup.md`。复用现有分诊、PR review、PR open 和 babysit 流程，不复制它们的细节。

## 步骤

1. **读取来源与当前状态。** PR 记录 URL、base/head、仓库、分支、作者、最新 SHA、检查和 review 线程。分支检查提交、上游和未提交改动。Agent 线程读取原始请求、后续用户纠正、交接内容与结果；交接摘要只是线索，须回到实际代码和最新状态核实。平台提供线程读取工具时使用它；不能读取来源时先索取可核实的链接或摘要。
2. **重建目标。** 写下原始目标、验收条件、已完成工作、未解决 findings 和未经验证的部分。外部 Issue 用 `issue-triage.md`；已有 PR 的需求与规范审查用 `pr-review.md`。区分用户明确说过的目标与 Agent 推测。
3. **核对是否仍值得继续。** 读取最新 base、source head 和完整 diff；检查主干后续改动、相关已合并或开放 PR、当前架构和真实行为。验证原始失败或关键工作流。无冲突不能证明实现仍适用；发现目标已实现、被取代或已失效时记录证据。
4. **先选处置方式，再改代码。**
   - **Continue**：目标仍有效，已有实现符合当前架构。沿用相关工作并完成剩余验收。
   - **Rework**：目标仍有效，但实现需要改变。保留有用证据，在隔离 topic branch 重做必要部分。
   - **Superseded**：主干已有等效或更好的实现，或目标不再成立。停止修改并报告证据；不擅自关闭 Issue 或 PR。

   分支归属与处置：
   - 他人拥有的 source branch 默认只读。需要新代码时，在本任务自有隔离分支基于目标主干修复，创建以目标主干为 base 的 replacement PR，带上必要来源改动并链接原 PR；full-send 可完成并合并这个 task-owned PR。
   - 不要把贡献者 source branch 设为 stacked PR 的 base，因为合并会写入该分支。只有用户明确要求更新 source branch 时，才可追加普通提交；不得改写其历史。Full-send 本身不授权向贡献者分支 push 或在来源 PR 留评论。
   - 若用户明确要求合并已命名的 source PR 本身且它满足全部门槛，可按 full-send 合并；无需写 source branch，合并会关闭该 PR。若合并 task-owned replacement PR，来源 PR 保持打开，除非用户另行授权关闭。
   - 不要因安全的 task-owned PR 生命周期再请求逐步确认，也不要建议用来源 PR 评论替代自有分支修复。先核实 source/base/head 最新关系，保留应继承的提交与署名；只有缺少真实仓库或必要源代码时才报告具体阻塞。
5. **实现和验证。** 只完成原目标需要的改动；按 `references/pr-review-policy.md` 分配验证与 review 深度。修改代码时运行相关检查和原始场景复现，更新 PR 正文中与最新 Head 对应的 Mermaid 图。需要创建或更新 PR 时移交 `pr-open.md`；需要等待 CI 或处理 review 时移交 `pr-babysit.md`。
6. **保留署名。** 尽量保留原提交与已验证的 author / co-author trailers。把自己的修复作为新提交。若创建 replacement PR，在描述中链接来源 PR 并说明沿用了什么、重做了什么。不要猜测邮箱、模型身份或贡献者归属。
7. **遵守写入边界。** 接手本身只授权本地继续工作。Push、评论、PR 更新/关闭、合并和部署仍按 `SKILL.md` 的授权边界执行；必要 rebase 的 `--force-with-lease` 仅可用于本任务自有分支。
8. **汇报接手结果。** 说明来源、处置方式、继承与重做的工作、验证证据、署名处理和剩余决定。没有运行的检查明确标为未运行。

## 结束条件

- **Continue / Rework**：原目标已通过相关验收，PR 后续工作按对应 playbook 完成，或有明确阻塞原因。
- **Superseded**：给出取代它的代码或 PR 证据，不修改或关闭来源。

## 移交

PR 创建或更新 → `pr-open.md`；开放 PR 跟进 → `pr-babysit.md`；当前会话恢复 → `session-pickup.md`。
