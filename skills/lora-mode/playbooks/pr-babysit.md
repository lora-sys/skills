# pr-babysit — 跟进开放的 Pull Request

> **适用**：处理已开 PR 的冲突、CI、review 和 bot 评论，并等待到 ready gate 或阻塞。**主导工具**：`gh` 与宿主事件 watcher。

## 步骤

1. **准备上下文。** 独立跟进或恢复会话时加载 `references/change-impact.md` 和 `references/pr-review-policy.md`；在同一 full mode 链里复用已读内容。读取 PR 状态、base/head 和正文中的最新 Change map Mermaid 图。队列状态单独读取 GraphQL `isInMergeQueue`，不要根据 `mergeStateStatus` 或 REST `mergeable_state` 推断：
   ```bash
   pr_node_id="$(gh pr view "$pr_number" --json id --jq .id)"
   gh api graphql -F id="$pr_node_id" -f query='query($id: ID!) { node(id: $id) { ... on PullRequest { isInMergeQueue } } }' -q .data.node.isInMergeQueue
   ```
   Full-stop 只处理 head 与本任务分支匹配的 PR。Full-stop 在任何 PR 写入前都要取消已有的 queue 和 auto-merge：先读状态；若已入队，先用 PR node ID 调用 `gh api graphql -F id="$pr_node_id" -f query='mutation($id: ID!) { dequeuePullRequest(input: {id: $id}) { clientMutationId } }'` 并用同一 `isInMergeQueue` 查询核实退出队列；随后若 `autoMergeRequest` 仍存在，运行 `gh pr merge "$pr_number" --disable-auto` 并核实其已清除。顺序不可颠倒：PR 仍在队列时，`gh pr merge --disable-auto` 可能返回成功但不清除队列或 auto-merge。

   **Full-send 处理已有 queue / auto-merge：** 只有所有 Agent 侧 merge gate 都满足，或 GitHub 明确强制阻止剩余门槛未满足时，才可保留现有自动合并状态。若必需 approval 不在当前 head，检查旧 head 是否有 GitHub 仍可能计入的 approval。规则没有启用 `dismiss_stale_reviews` 或无法确认时，旧 approval 可能让 GitHub 越过 lora-mode 的当前-head gate；即使没有待处理代码或 PR 正文改动，也必须先 dequeue，再运行 `gh pr merge "$pr_number" --disable-auto`，分别核实 `isInMergeQueue=false` 和 `autoMergeRequest=null`，然后保存检查点等待当前 head approval。只有 GitHub 明确 dismiss 旧 approval，且其他 Agent gate 都已满足时，才可保留 queue / auto-merge 等待 review 事件。若只剩必需检查仍在运行，当前 head approval 和其他 Agent gate 已满足，且 GitHub 规则强制该检查通过后才能合并，才可保留自动合并状态。

   最新 gate 满足后按仓库流程合并或入队。普通 babysit 不改 auto-merge / queue。任何模式无法核实当前状态时都停止写入并报告。
2. **按优先级处理。** 合并冲突 → CI 失败 → 人工 review → bot 评论。只处理最新 push 之后的新检查和评论；先按 `references/pr-review-policy.md` 核实证据与风险，再分类动手。
3. **区分评论。** 只修 diff 引入或加重且有证据的缺陷；过滤纯风格意见、重复项和未验证猜测。机械修正可直接处理；设计判断、歧义和安全发现先停下，不猜作者意图。回复按 `engineering-writing` 写，并过 `unslop`。`full-stop` / `full-send` 可在本任务 PR 上发布修复说明或带证据的驳回理由；普通 babysit 只交评论草稿，除非用户明确要求发布。提示性 bot 不构成单独等待条件。
4. **每次 push 前后核对。** Full-stop 首次写入、每次 push 和交还人审前都重读远端状态，确认 auto-merge 关闭且 PR 不在 merge queue；不得安排未来合并。push 后更新 head SHA、正文中的 Change map Mermaid 图和受影响检查结果，并确认正文对应最新改动。只有 PR 已有关联 Postplan 或本任务包含明确代码审查报告时才更新 HTML；按 `html-communication` 默认更新公开 draft，并在上传前检查新内容是否含敏感信息。
5. **复验改动。** 只有代码、配置或测试行为改变时才运行受影响的检查或复现；纯 PR 正文、图或格式修正只核对最新 SHA、Mermaid 正文和远端渲染。不为绿 CI 修改断言来隐藏行为差异。
6. **事件式等待。** 每个 PR 只用一个宿主 watcher，由当前主线程拥有。若任务需要等 CI 或其他必需门槛，且没有现成 watcher、平台也提供 watcher，在授权范围内启动一次；启动后让当前运行让出，不轮询。收到事件后重读当前状态与检查点，只继续未完成项，不重复已完成的外部副作用。Full-stop 可以等待 CI 达到人审就绪，但不等待人类 approval：其他门槛都通过后交人审并停止 watcher。Full-send 对缺失的必需 GitHub approval 保持 watcher；被唤醒后重读 PR、review、checks、保护规则和 head，继续 merge gate。仓库要求 approval 时，必须确认至少一个计入门槛的 `APPROVED` review 对应当前 head SHA。若当前 head 缺少 approval，而旧 review 可能仍被 GitHub 计入，等待前必须按步骤 1 退出 queue、关闭 auto-merge；不能只写检查点后让现有自动合并继续运行。只有 GitHub 明确 dismiss stale reviews 且其他 Agent gate 全通过时，才可保留自动合并状态等待事件。确认 merged 后才算完成。没有 watcher 时留下检查点并说明阻塞，不写轮询或 sleep 脚本。
7. **限定循环并判断就绪。** 使用 `pr-open.md` 中与本任务共用的 review / fix 轮次预算；需要新设计决策或未授权的写入时停止。人审就绪要求：无冲突且基于最新 base、最新 head 的必需检查通过、没有未解决的 blocking finding 或 change request、Change map 与 head 一致。Full-stop 达到此状态就交人审，不合并；full-send 还必须满足仓库要求的 review、分支保护和队列门槛，不能把缺少必需 approval 当成完成。仓库要求 approval 时，必须有计入门槛且 `commit_id` 等于当前 head SHA 的通过 review；`reviewDecision=APPROVED` 本身不足以证明审查覆盖了当前 head。High 风险需要明确的人类合并授权；用户明确授权本 PR 的 full-send 满足此门，但不能替代仓库要求的 GitHub review。无队列时按仓库 merge method 合并；启用队列时按宿主流程入队并等待最终合并事件。每次合并前刷新远端状态；任何模式都不得绕过分支保护。
8. **汇报现场。** 简要列出 PR 链接、CI、最新 SHA、Change map 和 review 结论；只逐项说明未解决 finding 与重要取舍，不复述无关评论。交付前清点本任务创建的截图、日志、验证目录和工作树；清理确认过期的临时产物，写明仍保留的证据用途，归属不明的文件标为未确认。
9. **合并后移交清理。** 确认 merged 后把分支/worktree/Issue/文档/产物清理交给 `post-merge-cleanup.md`，不在本 playbook 内顺手做远端删除或关闭 Issue。

## 禁止事项

不 force-push 共享分支、不用 `--no-verify`、不把失败检查标为非必须、不因 `full-stop` 合并 PR、不为 full-stop 安排 auto-merge、不在未获授权时关闭 Issue 或删除远端分支（已获授权的合并后清理按 `post-merge-cleanup.md` 执行）。仅 `full-send` 明确授权在 merge gate 通过后合并；必要 rebase 只可对本任务自有分支使用 `--force-with-lease`。更新已发布的 Postplan 时按 `html-communication` 默认更新；无法判断哪些内容可公开时不上传，先交付安全的本地新版，再就公开范围提出具体澄清。
