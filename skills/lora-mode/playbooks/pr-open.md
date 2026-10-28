# pr-open — 准备并创建 Pull Request

> 继承 SKILL.md 的七步骨架与硬边界。本 playbook 负责把已验收的改动整理成可审 PR。
> **适用**：用户明确要求开 PR 或提交审阅。**主导 skill**：`code-review` + `gh`。

## 步骤

1. **加载 `references/change-impact.md`。** 查看目标分支、merge-base、head 和未提交改动；保持用户已有工作。
2. **核对范围。** 一个 PR 聚焦一个逻辑变更。概述 Why、变更范围、非目标、风险和验证结果。
3. **生成 Change map。** 比较 base/head 的代码依赖图，准备短 JSON 图数据并运行 `scripts/render-impact-svg.py`。图中标出新增、修改、删除、受影响模块、依赖边变化和分析限制；对照 diff 核验图中内容。SVG 内含简短描述和机器可读的节点/边元数据。
4. **写 PR 描述。** 正文说明 Why、范围、风险和验证摘要，并附 SVG。GitHub CLI 可用 `--attach <svg>` 上传附件并替换正文中的本地图片引用；仅准备草稿时一并交付 SVG 文件。
5. **自审。** 调用 `code-review`，核对 spec、diff、依赖影响和验证；修复真实问题后重跑相关检查并更新 SVG。
6. **创建并核验。** 只有用户明确要求时创建 PR。默认创建 ready PR，不自动开始 babysit；用 `gh pr view` 核实标题、正文、SVG 附件和状态。

图结构、视觉语义和自查规则见 `references/change-impact.md`。Postplan 只在图无法承载必要解释、用户要求独立页面，或项目约定要求报告时使用。

## 移交

用户明确要求继续看 CI 或评论 → `pr-babysit.md`。
