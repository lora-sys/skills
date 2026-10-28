# pr-open — 准备并创建 Pull Request

> 继承 SKILL.md 的七步骨架与硬边界。本 playbook 负责把已验收的改动整理成可审 PR。
> **适用**：用户明确要求开 PR 或提交审阅。**主导 skill**：`code-review` + `gh`。

## 步骤

1. **加载 `references/change-impact.md`。** 查看目标分支、merge-base、head 和未提交改动；保持用户已有工作。
2. **核对范围。** 一个 PR 聚焦一个逻辑变更。概述 Why、变更范围、非目标、风险和验证结果。
3. **生成 Change map。** 比较 base/head 的代码依赖图，标出新增、修改、删除、受影响模块和分析限制；自己逐项对照 diff。
4. **准备 Postplan 报告。** 记录 SHAs、图、影响解释和真实验证证据。加载 `html-stable-publish`，完成 preflight，并在上传前取得本次公开发布确认。
5. **写 PR 描述。** 正文内嵌 Mermaid 图、base/head 和验证摘要，附 Postplan draft 页面链接；报告未公开或内容不适合公开时，暂停创建并给出可行的私有方案。
6. **自审。** 调用 `code-review`，核对 spec、diff、依赖影响和验证；修复真实问题后重跑相关检查并更新图和报告。
7. **创建并核验。** 只有用户明确要求时创建 PR。默认创建 ready PR，不自动开始 babysit；用 `gh pr view` 核实标题、正文、图、链接和状态。

描述模板与图例见 `references/change-impact.md`。沿用该模板，不在 PR body 里重复整份 HTML 报告。

## 移交

用户明确要求继续看 CI 或评论 → `pr-babysit.md`。
