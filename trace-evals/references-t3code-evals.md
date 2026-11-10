# 第二阶段参考：t3code evals 方法论（PR #24635 + evals/README.md）

> 来源：https://github.com/pingdotgg/t3code/pull/24635 （closed，merged 进 main）与 https://github.com/pingdotgg/t3code/blob/main/evals/README.md 。抓取于 2026-11-08。用于本评估集第二阶段（降 token）与整体方法论校准。

## PR #24635 核心信息

- **动机**：T3 频繁改 agent instructions 和 MCP tool 描述，但无法判断改动让 agent 变好还是变坏；agent 还反复犯同类 T3 工具误用（用原生 subagent 而非 `delegate_task`、`sleep` 轮询而非 `watch_pull_request`、PR 不链接等）。
- **结构**：顶层 `evals/` 包；`evals/README.md` 规定何时写 eval、怎么跑、标准形态（`run.ts` 入口、cases 即数据、`--out`/`--model`/`--baseline`）、case 规则（复现真实失败、修复前必须失败、controls、无用户数据）、成本规则。AGENTS.md 指向它。
- **mcp-tool-use eval**：回放 88 个小假线程，跑在 Claude/Codex 上，检查 T3 工具调用与最终文本；**被载文本与工具 schema 直接来自源码**，因此两个分支对比就是两个版本的文本对比。廉价模型扮演 shell，本机不执行任何真实命令。
- **模板脱敏**：`trim-capture.ts` 从真实回合裁剪模板，移除用户指令、个人 skills/agents、账号 id、home 路径。**教训**：一个原本通过的 case 在脱敏模板下暴露了真实缺口——个人技能会掩盖 gap（与我们 held-out 防过拟合同一目的）。
- **成本**：一次全量 Sonnet run 约 $9。结果指标：cases passing / samples passing（Sonnet 82/85、96%；GPT-6.1 Sol 77/83、88% 多为 proxy 流错误）。

## evals/README.md 规则（原文要点）

### 何时写/跑 eval
- 改动影响模型所见或所为时：agent 指令、MCP 工具描述与 schema、工具结果、生成标题、功能引导语。
- 单元测试帮不上忙的地方：模型输出每次不同，小文案改动就能改变结果。

### eval 标准形态
- `evals/<eval>/run.ts` 入口；README 说明测什么、怎么跑、怎么加 case、跑一次多少钱。
- **Cases 是数据**：每个 case 有 `id`、来源（PR/issue/thread）、checks 或 rubric。
- **从源码 import 被测代码，永不把 prompt/工具描述/schema 抄进 eval**——保证永远测当前文本。
- flags：`--out`（必需）、`--model`、`--baseline`（对比）、`--case`（慢/贵时只跑部分）。
- 自判的 eval 用 `run.test.ts` 测 grader（纯逻辑，进 CI）；人判时对人隐藏哪个输出是新的。

### Case 规则（对本项目直接适用）
1. case 复现一个真实坏体验，或守护一个真实好体验；必须注明来源。
2. **先加 case 再修**：必须在旧文本上失败、新文本上通过。
3. 改 case 时，改后的 case 仍须在它针对的文本上失败；**优先修技能，不许放宽 case**。
4. **加 controls**：正确行为是普通工作的 case，专门抓“修复过度矫正”。
5. 模型输出会变：每个 case 跑多次；**半数及以上样本失败才算该 case 失败**；与**同模型基线**对比，不看绝对分。
6. case/夹具/模板不出现用户数据；用 `/home/user`、`acme/app`；提交前读遍每个夹具。
7. 提交文件不出现未发布模型细节（model id 表除外）。

### 成本规则
- 只跑改动触及的 case 直到通过；PR 合并前每个模型跑一次全量；每次 run 的成本记进 summary。

## 对本评估集的落地改造

1. **多样本**：终验轮每 case ≥2 样本，≥半数失败才判 FAIL（单人单次只作过程参考）。
2. **基线对比**：Round 0 即基线；后续轮次同模型（pi/step-5-preview）对比，不追求绝对分。
3. **Controls**：保留 Q01 类“正确行为是普通工作”的题与 OK-SKIP 场景，防修复过度矫正（如把 full-send 改成事事请示）。
4. **先题后修**：本轮已按此执行——Round 0 基线先于任何技能修改。
5. **不许放宽判据**：迭代失败时优先改技能，不改测试题判据；判据变更需在 test-plan.md 留痕。
6. **成本记录**：每轮记录题数、样本数、墙钟、delegate 调用数；平台未提供 token/单价时明确标注“不可用”，不做假精估算。
7. **防记忆答案**：held-out 6 题只在阶段一末/阶段二末跑；最终评审（qwen-work+gemini）不知道题号与优化过程，只拿到技能文本与场景。
