---
name: council
description: 用户明确要求 council 或跨模型评审时收集三个独立 provider 的只读意见；常规代码审查走 code-review 或 review-loop。
---

# Council

只在用户明确要求 council 或多模型评审时启动。普通代码审查继续走 `code-review` 或 `review-loop`，不要自动增加跨 provider 调用。

## 运行评审

1. 先处理已知问题并运行适用检查，再给评审者当前实现。若用户要放弃现有实现探索新方案，不必修补将被替换的代码。
2. 在 T3 Code 调用 `orchestrator_capabilities`，从三个不同且可运行的 provider 各选一个模型。用当前能力列表选择模型，不猜模型 ID、价格或可用性；若模型提供 reasoning effort 选项，默认用 `high`。若不能获得三个不同 provider，报告限制，不用同一 provider 的多个模型冒充。
3. 用 `delegate_task` 的 `role: "review"`、`mode: "async"`，并行启动三个评审者。为他们提供相同的用户目标、相关上下文、diff 和检查结果。代码审查请求每位评审者都给出 10 分制评分；未返回评分时写 `no score`。评审者只读，不得修改文件、发评论、创建 PR 或启动其他 Agent。
4. 用稳定 ID 汇总 findings。主 Agent 逐项对照代码和运行证据核实；不因模型数量或一致意见降低证据标准。过滤重复、纯偏好和超出目标的建议。
5. 只修复经核实且属于目标范围的问题。修复后重新运行受影响检查，再发起下一轮。最多三轮；只有安全、权限、数据丢失或状态/并发问题仍有具体证据时，才可按 lora-mode 的 review 预算延长。模型意见不一致时记录双方证据，不为追求一致而扩大范围。
6. T3 子任务完成时遵循事件唤醒机制，不轮询或启动 sleep 循环。无法访问指定 provider、评审无回复或任务失败都不算通过。

## 交付

按轮列出每个 provider 的结果、评分（若提供）、修复与驳回的 findings、实际检查和未解决分歧。若结果属于 PR 流程，交给 lora-mode 的 PR playbook 决定是否写入 PR 正文。Council 本身不授权外部写入、推送、合并或部署。
