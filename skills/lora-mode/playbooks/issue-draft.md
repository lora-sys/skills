# issue-draft — 起草可执行的 Issue

> 继承 SKILL.md 的七步骨架与硬边界。本 playbook 只负责把已确认的工作写成可读、可执行的 Issue。
> **适用**：用户要创建或整理 GitHub / GitLab Issue 描述。**主导 skill**：目标 tracker 的官方 CLI 或现有 GitHub skill。

## 步骤

1. **加载 `references/change-impact.md`。** 区分 bug、功能和技术债；范围未定时先列出待决问题。
2. **核实现状。** bug 引用可复现的实际结果；功能写清当前行为和要改变的行为。没证据的代码路径标为未知。
3. **写行为契约。** 包含背景、实际/期望、验收条件、非目标和外部约束；不要把文件行号当长期契约。
4. **画 Issue map。** 用 Mermaid 显示实际/期望路径或未决状态；人和 agent 都能从图中分辨已知与未知。
5. **准备 Postplan 报告。** 报告包含完整上下文、图、证据和未决项。页面发布前执行 `html-stable-publish` preflight，并取得本次公开发布确认。
6. **准备描述。** 正文包含 Issue map 和 Postplan draft 链接。按 unslop 检查描述与报告。
7. **按授权提交。** 用户只要求草稿时交付草稿；用户明确要求创建 Issue 后才调用 tracker。核实标题、正文和链接。

描述骨架见 `references/change-impact.md`。信息未知时保留 `Unknowns`，没有 Postplan 发布确认时不编造链接。

## 证据形态

Issue 草稿、图源、Postplan URL、实际 tracker 返回的 Issue URL。未创建时明确交付草稿状态。

## 移交

新收到的外部 Issue → `issue-triage.md`；实现 Issue → 对应功能或 bug-fix playbook。
