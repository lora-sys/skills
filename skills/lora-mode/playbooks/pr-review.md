# pr-review — 审查 Pull Request

> 继承 SKILL.md 的七步骨架。本流程按 spec 与工程规范审 PR，不使用“自己的交付物”零上下文协议。
> **适用**：审查自己的或他人的 PR、给出 verdict。**主导 skill**：`code-review`。

## 步骤

1. **加载 `references/change-impact.md` 和 `code-review`。** 确认 PR base/head、变更范围、关联 Issue 和 Change map SVG 附件。
2. **建立审查输入。** Spec 轴读取 Issue / 验收条件；Standards 轴读取 diff 与仓库规范。两条轴分开记录，不能套用禁止阅读需求的盲审协议。
3. **核对 Change map。** 查看 SVG 和其中的机器可读元数据，对照真实 diff 和可查依赖，核验增删模块、边界变化、受影响消费者、SHA 与覆盖限制。图不可信时说明具体差异，不让图替代源码。
4. **验证关键行为。** 按项目能力运行相关检查或最小复现；明确没有运行或无法验证的项目。
5. **分级 findings。** 用 `blocker`、`should-fix`、`nit`、`FYI`；每项给证据、影响和可执行修复建议，把 spec 偏差和 standards 问题分组。
6. **给出 verdict。** `approve`、`request changes` 或 `comment`，说明阻塞项和剩余风险。
7. **交付草稿。** 默认只输出 review 草稿，不发布评论或批准；用户明确要求提交后才调用 GitHub。图缺失或过期时要求更新 SVG 附件。

## 边界

CI、PR 评论与冲突跟进 → `pr-babysit.md`。PR 审查不替作者改代码，除非用户明确要求。
