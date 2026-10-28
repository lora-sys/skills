# pr-review — 审查 Pull Request

> 继承 SKILL.md 的七步骨架。本流程按 spec 与工程规范审 PR，不使用“自己的交付物”零上下文协议。
> **适用**：审查自己的或他人的 PR、给出 verdict。**主导 skill**：`code-review`。

## 步骤

1. **加载审查规则。** 读取 `references/change-impact.md`、`references/pr-review-policy.md` 和 `code-review`。确认 PR base/head、变更范围、关联 Issue 和 Change map SVG 附件。外部 PR 先用 `issue-triage.md` 提取请求、验收条件和未知项，再独立进入 PR 审查。
2. **建立审查输入。** 按 diff 和影响范围给改动分 Low / Medium / High 风险，并记录证据。Spec 轴优先读取关联 Issue 正文和验收条件；Standards 轴读取 diff 与仓库规范。两条轴分开记录，不能套用禁止阅读需求的盲审协议。不要运行仓库不存在的 `/setup-matt-pocock-skills`；若没有可用 Spec，标明缺失并继续 Standards 审查。
3. **核对 Change map。** 查看 SVG 和其中的机器可读元数据，对照真实 diff 和可查依赖，核验增删模块、边界变化、受影响消费者、SHA 与覆盖限制。图不可信时说明具体差异，不让图替代源码。
4. **验证关键行为。** 按风险运行相关检查或最小复现；High 风险覆盖相关安全、集成和恢复路径。明确没有运行或无法验证的项目。
5. **分级 findings。** 用 `blocker`、`should-fix`、`nit`、`FYI`；只报告由改动引入或加重且有证据的问题。过滤纯风格偏好、重复项和未经验证的猜测。按 `engineering-writing` 写每项，包含证据、影响和可执行修复建议，并把 Spec 与 Standards 问题分组。保留两轴各自结论，不跨轴挑一个“最严重问题”。
6. **给出 verdict。** `blocker` 或 `should-fix` 导致 `request changes`；无阻塞项但 Spec 缺失或验证有限时用 `comment`；无阻塞项且改动满足 Spec、改善代码健康度时用 `approve`。Verdict 只说明下一步动作，不合并或重排两轴 findings。
7. **交付草稿。** 默认只输出 review 草稿，不发布评论或批准；用户明确要求提交后才调用 GitHub。图缺失或过期时要求更新 SVG 附件。

## 边界

CI、PR 评论与冲突跟进 → `pr-babysit.md`。PR 审查不替作者改代码，除非用户明确要求。
