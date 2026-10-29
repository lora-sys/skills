# pr-babysit — 跟进开放的 Pull Request

> 继承 SKILL.md 的七步骨架与硬边界。本 playbook 在用户要求跟进、监视或等待 PR，或由 `full-stop` / `full-send` 自动串联时运行。
> **适用**：处理已开 PR 的冲突、CI、review 和 bot 评论，并等待到 ready gate 或阻塞。**主导工具**：`gh` 与宿主事件 watcher。

## 步骤

1. **准备上下文。** 独立跟进或恢复会话时加载 `references/change-impact.md` 和 `references/pr-review-policy.md`；在同一 full mode 链里复用已读内容。读取 PR 状态、base/head 和最新 Change map SVG。Full-stop 只处理 head 与本任务分支匹配的 PR；若其 auto-merge 已启用或已入 merge queue，关闭并验证后再修改。普通 babysit 不改 auto-merge / queue；无法核实当前状态时停止并报告。
2. **按优先级处理。** 合并冲突 → CI 失败 → 人工 review → bot 评论。只处理最新 push 之后的新检查和评论；先按 `references/pr-review-policy.md` 核实证据与风险，再分类动手。
3. **区分评论。** 只修 diff 引入或加重且有证据的缺陷；过滤纯风格意见、重复项和未验证猜测。机械修正可直接处理；设计判断、歧义和安全发现先停下，不猜作者意图。回复按 `engineering-writing` 写，并过 `unslop`。`full-stop` / `full-send` 可在本任务 PR 上发布修复说明或带证据的驳回理由；普通 babysit 只交评论草稿，除非用户明确要求发布。提示性 bot 不构成单独等待条件。
4. **每次 push 前后核对。** push 前再确认 Full-stop 的 auto-merge 已关闭且不在 merge queue；若设置被重新打开，先关闭并核实。push 后更新 head SHA、Change map SVG 和受影响检查结果，并确认 PR 附件对应最新改动。只有 PR 已有关联 Postplan 或本任务包含明确代码审查报告时才更新 HTML；每个公开版本都须重新确认。
5. **复验改动。** 只有代码、配置或测试行为改变时才运行受影响的检查或复现；纯 PR 正文、附件或格式修正只核对最新 SHA、SVG 和远端内容。不为绿 CI 修改断言来隐藏行为差异。
6. **事件式等待。** 每个 PR 只用一个宿主 watcher，由当前主线程拥有；收到事件后核对状态，需要处理时才继续，不发“仍在等待”的空更新。Watcher 唤醒后继续使用现有 watch，不重复启动；交接前停止 watch。没有 watcher 时报告当前状态并交还，不写轮询或 sleep 脚本。
7. **限定循环并判断就绪。** 使用 `pr-open.md` 中与本任务共用的 review / fix 轮次预算；需要新设计决策、权限或外部确认时也停止。merge-ready 要求：无冲突且已基于最新 base、最新 Head 的必需检查通过、风险对应的人工审批满足、没有未解决的 blocking finding 或人类 change request、必需 review 完成、Change map 与 Head 一致。High 风险没有可核实的人类审批时不得合并。非必需 bot 仅作提示。`full-stop` 再次确认 PR 未启用自动合并、未加入 merge queue；`full-send` 只有全部 gate 满足才可按仓库配置的 merge method / queue 合并。合并前刷新远端状态；任何模式都不得绕过分支保护。
8. **汇报现场。** 简要列出 PR 链接、CI、最新 SHA、Change map 和 review 结论；只逐项说明未解决 finding 与重要取舍，不复述无关评论。

## 禁止事项

不 force-push 共享分支、不用 `--no-verify`、不把失败检查标为非必须、不因 `full-stop` 合并 PR、不关闭 Issue。仅 `full-send` 明确授权在 merge gate 通过后合并；必要 rebase 只可对本任务分支使用 `--force-with-lease`。更新已发布的 Postplan 时，按 `html-communication` 为该版本重新取得发布确认。
