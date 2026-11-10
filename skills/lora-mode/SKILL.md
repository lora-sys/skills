---
name: lora-mode
description: lora 的工程流程路由器，用于功能开发、修复/重构、仓库调查、目标评测、PR/Issue 全流程及注释清理（no-comment/comment-review）；用户点名 lora-mode、full-stop/full-send，或要求持续完成、接手工作、现代化旧 PR 时也使用；不超过两个文件且无共享影响的非 bug 改动直接调用对应技能。
---

# lora-mode

按交付目标选 playbook；playbook 定步骤，所列 skill 提供方法。只读当前任务链所需文件，未变化的内容直接复用；同一任务的后续消息沿用当前路由。

## 路由

- Web 功能 → `web-feature`；M/L 档 API、脚本、工具 → `backend-feature`；bug 或行为异常 → `bug-fix`；仓库调查 → `investigation`。S 档普通脚本走行内流程。
- 代码改动 → 按 `references/comment-review.md` 检查本次差异中的注释；当用户明确要求“注释清理”、“清理注释”，或输入触发词 `no-comment`、`comment-review` 时，审查并清理受影响文件。不要把按需审查扩大为全仓清理。
- 改动前与 diff 后做性质筛查：发现并发交错、租约/过期接管、重试、状态或数据不变量、幂等等可信性质，或改动命中已有验证覆盖时，读 `references/verification-routing.md` 与 `references/formal-verification.md` 并按其中门槛执行。主题词不触发建模；普通文档或无关界面改动沿用原有检查。
- 满足形式化门槛且项目无覆盖时必须创建项目级验证并保留回归测试；refactor 命中已有覆盖时按相邻 `maintain-formal-verification-skill` 复核模型。TLC/Java 缺失只将模型标为 draft/blocked 并留下命令，不跳过、不声称完成。其余风险选能回答问题的最低成本验证；PR 创建与审查需核对当前 head 的验证证据。
- Issue 起草/分诊 → `issue-draft` / `issue-triage`；PR 创建或现有 PR 正文/Change map 更新 → `pr-open`；PR 检查与评论跟进 → `pr-babysit`；PR 审查 → `pr-review`；旧 PR 现代化 → `modernize`；接手 PR、分支或 Agent → `takeover`。
- PR 合并后或用户要求清理仓库/本地工作痕迹 → `post-merge-cleanup`；该 playbook 也规定仓库级定期卫生。
- 用户明确要求在开发机安装依赖、跑测试或启动验证：纯验证直接调 `remote-dev`；涉及代码改动时先按本模式在本机完成，再移交远端；技能缺失时说明。
- 用户要求自主持续做到完成时，保留原任务类型路由并读取 `playbooks/autonomous-run.md`；该 playbook 规定执行方式，不替代 bug、功能、PR 等任务流程。
- 专项或不确定的开发路由见 `references/routing-matrix.md`。

## 规模

- **S：** 单文件、约 100 行以内、无新依赖、共享结构变更或外发。跳过通用 playbook、reference 和 todo；代码改动仍读 `comment-review`，bug 读 `bug-fix` 与 `debug`，PR/Issue 读对应流程和 `change-impact`。先写验收，检查主路径和一个边界，给出三行证据。未获要求不新增测试文件。
- **M：** 常规多文件任务。执行 playbook、相关检查和一轮行内自查：输入边界、错误路径、状态诚实、回归面。仅多阶段或异步等待时建短 todo。
- **L：** 公开/生产发布、多模块、新依赖、广泛行为变化、无人值守，或共享结构改动超过 20 行。运行相关质量门并隔离审查；PR 使用自身审查流程。只在用户要求或正式发布前运行完整 eval；行为、路由或权限规则变化时只运行对应 case。20 行只统计共享文件改动，不含新增页面或链接。
- 范围扩大时重新分级。所有 PR/Issue 都走对应流程。

## 证据与权限

- 仅当仓库已有 `.codegraph/` 且 CLI/MCP 可用时使用 CodeGraph；未获授权不得初始化索引、安装工具或配置 MCP。
- 创建或更新 PR/Issue 正文时内嵌 Mermaid 影响图；PR 审查时核对图与实际 diff，后续代码改变时更新正文中的图。按 `references/change-impact.md` 生成并对照源码及证据；未核实的边不得写成事实。
- PR 代码审查、架构审查或用户明确要求报告时，按 `html-communication` 默认发布/更新 Postplan 公开 draft，无需逐次确认；公开前完成敏感内容检查并安全删减，无法判断哪些内容可公开时不上传，先完成安全的本地报告，再就公开范围提出具体澄清。Postplan 发布不授权 PR/Issue 写入。
- PR 报告的验证结果必须来自最新 head，并能对应到实际命令和日志。遇到失败/阻塞时，先判断根因；在用户已授权的环境内修复可控的依赖或配置问题并复跑受影响检查。仍受外部条件阻塞时如实保留状态，不把环境阻塞标成代码失败，也不把定向通过概括成全量通过。
- 复用测试前确认它能观察本次预期行为；若测试只检查未变化的边界（例如只查动画起终点，却不采样能区分曲线的中间点），补充最小的有效断言后再报告该行为已验证。
- 撰写 GitHub 评论或回复时使用 `leaving-pr-comments`，发布仍按当前流程授权；其他 PR/Issue、技术文档和 prose 加载 `engineering-writing` 后再加载 `unslop`。代码任务不加载写作技能。行为与预期不符时用 `debug` 复现，不声称未验证的结果。
- 用户明确要求跨模型评审时使用 `council`；普通评审不自动启动多个 provider。`review-loop` 是单模型循环评审的默认入口。
- 草拟不等于远端写入。未获本任务授权，不创建 PR、不提交代码。
- 代码与文档改动走 PR-only，不直接推默认分支。用户说「直接更新 / commit and push / 直接提交」等未指明分支的指令时：若当前在默认分支，先说明这越过 PR-only 边界并确认一次，用户坚持再执行并留痕；在任务分支上则直接执行。full-send/full-stop 模式内仍以其边界为准。
- `full-stop`：可创建/更新本任务 PR、推送本任务分支并做到 merge-ready 后交给人审；不等待 approval 事件，须确认 auto-merge 已关闭且 PR 不在 merge queue，禁止 `--auto` 预先安排合并。`full-send`：授权在最新 merge gate 通过后合并本任务 PR，主 Agent 负责推进到实际合并；PR 创建、更新、入队和等待审批都是中间状态，不要询问是否继续；High 风险任务中用户明确给出的 `full-send` 是人类合并授权，仓库保护规则另要求 GitHub review 时必须照常满足，不能绕过。full-send 遇到必需 approval 未到时不算完成：有可用 PR watcher 就等待事件并从最新状态续跑；没有 watcher 时留下检查点并如实报告阻塞。若当前 head 缺少必需 approval，而旧 head approval 仍可能被 GitHub 计入（stale-review dismissal 关闭或无法确认），已有 queue/auto-merge 可能提前合并；先退队，再关闭 auto-merge，并核实两者都已关闭，然后保存检查点等待当前 head approval——命令与顺序见 `playbooks/pr-babysit.md`。两者不授权改 Issue、其他 PR 或标签，也不允许推默认分支、改写共享历史、绕过保护或使用 `--admin`。
- 部署、生产发布、关闭 Issue 和删除数据各需单独授权；Postplan 公开 draft 遵循 `html-communication` 的默认发布授权；凭据不得写入文件或命令行参数。
- 破坏性或不可逆操作（删除版本受控的文件或目录、清空非衍生数据、覆盖生产配置、`--force` 推送、`rsync --delete` 等）执行前必须把将变动的内容与边界项判定列为清单交给用户确认，用户确认前不得执行；用户说「删掉/清理」不构成对具体清单的确认。任务过程中自产的临时产物、构建缓存（如 `__pycache__`）和测试衍生文件的清理除外，但须在收尾汇报中列出已删项。抢救性恢复（如从 reflog 找回提交）除外，但须在汇报中说明。

## 迭代

不按任务频次写使用台账。只在路由、权限或行为规则出现可复现缺口时记录对应 case；用户明确要求复盘，或同类问题再次出现时，进入 `playbooks/reflect.md`。EVALS 不在普通任务中加载；修改了对应行为时定位并仅读相关 case。

## 自主推进与完成

- 明确可执行的目标默认做到全部验收项。开始时列出可检查的完成条件；多阶段任务维护 todo。阶段进度、找到根因或单次失败都不等于完成。每阶段汇报后更新 todo 并继续原任务中的下一项，不要询问是否继续。后续纠正补充当前验收，不要求用户重复目标。
- 失败先定位根因，修复授权范围内可控的问题，并继续不依赖阻塞项的工作。等 CI、PR 或其他外部事件时，检查能否唤醒当前任务并从持久化检查点续跑。没有事件入口时，留下进度和下一步，不承诺会话结束后自动恢复。
- 只在权限边界、必须由用户决定的实质选择（如批量删除与范围性清理的具体清单）、真正的外部阻塞或用户要求停止时暂停。自主执行不扩大写入、部署、发布、付费或删除权限。
- 收尾逐项报告已验证、未验证或受阻的项目及证据。确认交付物存在，并按最新工作区状态说明改动、检查和遗留事项。配额、凭据、服务不可用或客户端取消等外部问题如实记录；可继续的独立工作照常完成。

专项路由见 `references/routing-matrix.md`；注释审查见 `references/comment-review.md`；PR 风险和事故反馈见 `references/pr-review-policy.md`；报告发布见 `references/postplan-reports.md`；L 档隔离审查看 `references/review-protocol.md`；M/L 质量门见 `references/web/quality-gates.md`。

## 阶段变化与收尾

- 目标扩展到代码修改、远端验证或 PR 时，先重判路由、规模、验收和权限。复用已有检查，不重跑无关步骤。
- 默认只委派一层。派发子代理前先确认自己不是被委派的子代理；子代理不得自行嵌套委派、切换模型或创建编排线程，需要委派时向上报告，不自行启动。用户或主 Agent 可在任务书中明确授权多层协作。子代理遇到上下文、工具或权限限制时上报，不扩大范围。
- 收尾核对子代理的实际改动、外部写入和遗留产物；验证结论必须对应最新目标和代码状态。按任务 playbook 处理临时产物。PR 合并后按 `playbooks/post-merge-cleanup.md` 清理，再报告完成。
