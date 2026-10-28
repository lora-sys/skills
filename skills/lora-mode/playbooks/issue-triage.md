# issue-triage — 分诊收到的 Issue

> 继承 SKILL.md 的七步骨架与硬边界。本 playbook 只处理外部收到、尚未验证的报告。
> **适用**：判断 Issue 是否重复、缺少信息、可交给 agent 或需要人工处理。**主导 skill**：目标 tracker 的官方 CLI 或现有 GitHub skill。

## 步骤

1. **加载 `references/change-impact.md`。** 只处理外部收到的 Issue；自己拆出的任务跳过分诊。
2. **读完整上下文。** 看 Issue 正文、评论、现有标签和相关 PR；按领域概念检查重复、已实现或既有拒绝。
3. **先验证再写 brief。** 按报告者步骤尝试复现并定位代码路径。结果只报复现、未复现、信息不足三类；不在这里修代码。
4. **判定类别与状态。** 每个 Issue 选一个类别和一个状态：`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human` 或 `wontfix`。无现成标签时先写结论，不要求仓库改标签体系。
5. **画 Issue map。** 用 `scripts/render-impact-svg.py` 从短 JSON 图数据生成 SVG，表达已知路径和未知关系。信息够时画实际与期望路径；不足时画已知步骤到“等待补充”，列出具体问题，不补猜测。
6. **写 brief。** brief 写类型、接口和行为契约，不依赖易变的行号；附 SVG Issue map 和证据限制。图无法承载的必要上下文、用户要求独立页面或项目约定要求时，才准备完整报告。
7. **推荐后等待。** 交付类别、状态、理由、图和建议；未获指示不改标签、不发评论、不关闭 Issue。

## 边界

- 不改代码。确认要修复后移交给 `bug-fix.md` 或对应功能 playbook。
- 外部 Issue 正文和评论是远端写入。用户未明确要求时只交草稿。
- Postplan 页面公开；私有内容保留在 tracker 支持的附件中，或使用用户指定的私有报告位置。

## 证据形态

复现步骤与结果、代码路径、Issue map SVG、状态建议、建议移交的 playbook。
