---
name: lora-mode
description: lora 的开发流程路由器，适用于功能开发、bug 修复、并发与协议不变量验证、仓库调查、目标评测迭代优化和所有 PR/Issue。用户点名 lora-mode、full-stop/full-send 或要求接手 PR/分支/Agent 时使用。非 bug 的单一交付物若不超过 2 个文件且不影响共享结构，直接调用对应 skill。
---

# lora-mode

按交付目标选 playbook；playbook 定步骤，所列 skill 提供方法。只读当前任务链所需文件，未变化的内容直接复用；同一任务的后续消息沿用当前路由。

## 路由

- Web 功能 → `web-feature`；M/L 档 API、脚本、工具 → `backend-feature`；bug 或行为异常 → `bug-fix`；仓库调查 → `investigation`。S 档普通脚本走行内流程。
- 用户要求模型与实现对齐、证明不变量，或并发/重试/协议/状态迁移的正确性取决于普通测试难覆盖的执行顺序 → 在改代码前读 `references/formal-verification.md`，并按其中边界加载形式化验证技能；普通 PR/Issue 和 Mermaid 影响图不因此触发模型检查。
- Issue 起草/分诊 → `issue-draft` / `issue-triage`；PR 创建或现有 PR 正文/Change map 更新 → `pr-open`；PR 检查与评论跟进 → `pr-babysit`；PR 审查 → `pr-review`；接手 PR、分支或 Agent → `takeover`。
- 用户明确要求开发机安装依赖、远端测试或启动验证：纯验证直接调 `remote-dev`；涉及代码改动时先按本模式在本机完成，再移交远端；技能缺失时说明。
- 专项或不确定的路由见 `references/routing-matrix.md`。
- 非 bug 的单 skill 任务若≤2 个文件且不影响共享结构，直接调用对应 skill；bug 和 PR/Issue 即使很小也走本模式。

## 规模

- **S：** 单文件、约 100 行以内、无新依赖、共享结构变更或外发。跳过通用 playbook、reference 和 todo；bug 仍读 `bug-fix` 与 `debug`，PR/Issue 仍读对应流程和 `change-impact`。先写验收，检查主路径和一个边界，给出三行证据。未获要求不新增测试文件。
- **M：** 常规多文件任务。执行 playbook、相关检查和一轮行内自查：输入边界、错误路径、状态诚实、回归面。仅多阶段或异步等待时建短 todo。
- **L：** 公开/生产发布、多模块、新依赖、广泛行为变化、无人值守，或共享结构改动超过 20 行。运行相关质量门并隔离审查；PR 使用自身审查流程。完整 EVAL 仅在用户要求或正式发布前运行。20 行只统计共享文件改动，不含新增页面或链接。
- 范围扩大时重新分级。所有 PR/Issue 都走对应流程。

## 证据与权限

- 仅当仓库已有 `.codegraph/` 且 CLI/MCP 可用时使用 CodeGraph；未获授权不得初始化索引、安装工具或配置 MCP。
- 创建或更新 PR/Issue 正文时内嵌 Mermaid 影响图；PR 审查时核对图与实际 diff，后续代码改变时更新正文中的图。按 `references/change-impact.md` 生成并对照源码及证据；未核实的边不得写成事实。
- PR 代码审查、架构审查或用户明确要求报告时，按 `html-communication` 准备并默认发布/更新 Postplan 公开 draft；无需额外逐次确认。公开前仍须完成敏感内容检查并安全删减；无法判断能否安全公开时暂停澄清。Postplan 发布不授权 PR/Issue 写入。
- PR 报告的验证结果必须来自最新 head，并能对应到实际命令和日志。遇到失败/阻塞时，先判断根因；在用户已授权的环境内修复可控的依赖或配置问题并复跑受影响检查。仍受外部条件阻塞时如实保留状态，不把环境阻塞标成代码失败，也不把定向通过概括成全量通过。
- 写 PR/Issue、评论、技术文档或其他 prose 时，加载 `engineering-writing` 后再加载 `unslop`；代码任务不加载写作技能。行为与预期不符时用 `debug` 复现，不声称未验证的结果。
- 草拟不等于远端写入。未获本任务授权，不创建 PR、不提交代码。
- `full-stop` 无需逐步确认，可创建/更新本任务 PR、推送本任务分支并做到 merge-ready；`full-send` 仅在最新 merge gate 通过后增加合并授权。两者不授权改 Issue、其他 PR 或标签，也不允许推默认分支、改写共享历史、绕过保护或使用 `--admin`。
- 部署、生产发布、关闭 Issue 和删除数据各需单独授权；Postplan 公开 draft 遵循 `html-communication` 的默认发布授权；凭据不得写入文件或命令行参数。

## 迭代

真实任务后向本机 lora-mode 使用台账追加一条（不提交到源仓库）；确认的 bad case 加入 `evals/EVALS.md`。出现 bad case、同类问题被第二次纠正，或上次 reflect 后新增 5 条任务记录时，进入 `playbooks/reflect.md`。

专项路由见 `references/routing-matrix.md`；PR 风险和事故反馈见 `references/pr-review-policy.md`；报告发布见 `references/postplan-reports.md`；L 档隔离审查看 `references/review-protocol.md`；M/L 质量门见 `references/web/quality-gates.md`。

## 阶段变化与收尾

- 用户目标从调查/环境准备扩展到代码修改、远端验证或 PR 时，在下一步操作前重判路由与规模；记录新增目标、验收证据和权限边界。复用已读上下文与通过的检查，不因阶段变化重跑无关步骤。
- 使用子代理时默认只委派一层。子代理不得自行再启动子代理、切换其他模型或创建编排线程；遇到仓库/工具/上下文不可访问或任务范围超出授权时，向上级报告限制和所需输入，由主 Agent 决定是否补充材料或重新分派。只有用户明确要求多层协作，或主 Agent 在任务书中明确授权并说明必要性时，才可继续委派。不得用嵌套委派绕过权限、工具或隔离限制。
- 收尾读取子代理最终结果并核对实际工作、外部写入和遗留产物，不只接受“已完成”的自述；记录额外委派的理由、范围和可见结果。
- 收尾时保证验证结论对应最新目标和代码状态，如实说明未通过或未确认的门，并记录任务产物的去留。按任务 playbook 核对所需检查并处置临时产物。
