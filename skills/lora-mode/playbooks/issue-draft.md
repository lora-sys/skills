# issue-draft — 起草可执行的 Issue

> **适用**：用户要创建或整理 GitHub / GitLab Issue 描述。**主导 skill**：目标 tracker 的官方 CLI 或现有 GitHub skill。

## 步骤

1. **加载 `references/change-impact.md`。** 区分 bug、功能和技术债；范围未定时先列出待决问题。
2. **核实现状。** bug 引用可复现的实际结果；功能写清当前行为和要改变的行为。没证据的代码路径标为未知。
3. **写行为契约。** 包含背景、实际/期望、验收条件、非目标和外部约束；不要把文件行号当长期契约。
4. **画 Issue map。** 在正文中写 Mermaid 图，区分实际路径、期望路径、候选模块和未知项；用实线表示已核实关系，用虚线标出报告、推断或待确认关系。
5. **准备描述。** 按 `engineering-writing` 写行为契约和 Issue 正文，再按 `unslop` 检查；正文包含 Mermaid Issue map。
6. **按授权提交。** 用户只要求草稿时交付完整 Markdown 草稿；用户明确要求创建 Issue 后才调用 tracker。预览可用时核实 Mermaid 图已正确渲染；没有预览工具时标明渲染未验证。

图规范和描述骨架见 `references/change-impact.md`。信息未知时明确标注，不把推测画成事实。普通 Issue 草稿内嵌 Mermaid；只有用户要求报告或符合 `references/postplan-reports.md` 的报告型场景时才准备 Postplan。

## 证据形态

Issue Markdown 草稿、实际 tracker 返回的 Issue URL。未创建时明确交付草稿状态。

## 移交

新收到的外部 Issue → `issue-triage.md`；实现 Issue → 对应功能或 bug-fix playbook。
