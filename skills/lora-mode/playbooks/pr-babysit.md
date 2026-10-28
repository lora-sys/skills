# pr-babysit — 跟进开放的 Pull Request

> 继承 SKILL.md 的七步骨架与硬边界。本 playbook 只在用户明确要求 shepherd / babysit 时运行。
> **适用**：处理已开 PR 的冲突、CI、review 和 bot 评论。**主导 skill**：`gh`。

## 步骤

1. **加载 `references/change-impact.md`。** 读取 PR 状态、base/head、最新 Change map SVG。
2. **按优先级处理。** 合并冲突 → CI 失败 → 人工 review → bot 评论。先分类再动手。
3. **区分评论。** 机械修正可按原意处理；设计判断、歧义和安全发现先写回复草稿，不猜作者意图。
4. **每次 push 后刷新证据。** 更新 head SHA、Change map SVG 和验证结果，再确认 PR 描述中的附件对应最新改动。
5. **复验改动。** 运行受影响的测试或复现；不为绿 CI 修改断言来隐藏行为差异。
6. **限定循环。** 连续三轮 fix → push → recheck 仍失败就停止；需要新设计决策、权限或外部确认时也停止。
7. **汇报现场。** 每条评论标明已改、已回或未处理及原因；列出 CI 状态、最新 SHA 和 Change map 状态。

## 禁止事项

不 force-push 共享分支、不用 `--no-verify`、不把失败检查标为非必须、不替用户合并 PR 或关闭 Issue。用户要求补充公开报告时，按 `html-stable-publish` 取得本次发布确认。
