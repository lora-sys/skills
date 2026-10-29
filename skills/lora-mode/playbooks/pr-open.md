# pr-open — 准备并创建 Pull Request

> **适用**：用户要求开 PR；或 `full-stop` / `full-send` 串联到 PR 生命周期。**主导工具**：一个独立 reviewer + `gh`。

## 步骤

1. **准备上下文。** 当前任务链尚未加载或会话恢复时读取 `references/change-impact.md` 和 `references/pr-review-policy.md`；否则复用。查看目标分支、merge-base、head、未提交改动和该分支是否已有 PR；保持用户已有工作。Full mode 若当前在默认分支，为本任务创建 topic branch，不推默认分支。只接续 head 与当前任务分支匹配的已有 PR；分支不匹配就停止，不修改该 PR。Full-stop 授权仅对这条任务 PR 关闭 auto-merge / 退出 merge queue；改动前和每次 push 前核实已关闭，不能确认时暂停。
2. **核对范围与风险。** 一个 PR 聚焦一个逻辑变更。按实际 diff 和受影响模块给出 Low / Medium / High 风险与理由；作者身份不降低风险。按仓库惯例取标题范例，标题简洁说明问题或收益。描述先说问题和解决方式，再给影响图、风险和验证；不列文件清单复述 diff。
3. **生成 Change map。** 比较 base/head 的代码依赖图，准备短 JSON 图数据并运行 `scripts/render-impact-svg.py`。图中标出新增、修改、删除、受影响模块、依赖边变化和分析限制；对照 diff 核验图中内容。SVG 内含简短描述和机器可读的节点/边元数据。
4. **写 PR 描述。** 按 `engineering-writing` 起草，再按 `unslop` 检查。GitHub CLI 可用 `--attach <svg>` 上传附件并替换正文中的本地图片引用；仅准备草稿时一并交付 SVG 文件。
5. **独立审查。** 常规只启动一次 Spec / Standards 审查，同时读取 Issue / 验收条件、base 到 head 的 diff、验证结果和 Change map。High 风险再增加一次聚焦安全、数据、并发或恢复路径的独立审查；使用 `references/pr-review-policy.md` 的人类审批门。没有 Spec 时注明并继续 Standards，不要运行缺失的 setup 命令。只修 blocker 与 should-fix。若没有独立 reviewer，自己做一轮相同检查并说明未独立复核。显式 PR review 请求继续使用 `pr-review.md` 的双轴审查。
6. **创建并核验。** 普通“开 PR”请求创建并核验后结束；`full-stop` / `full-send` 继续交给 `pr-babysit.md`，使用一个宿主事件 watcher 等到 ready 或阻塞。用 `gh pr view` 核实标题、正文、SVG 附件、最新 SHA 和状态；缺图、图过期或附件上传失败时修好再交付。`gh` 支持 `--attach` 时直接附图；旧版本不支持时先报告阻塞，不创建缺图 PR。

**轮次预算**：普通 PR 一轮初始 review，最多两轮有实质问题的 fix → push → recheck；`pr-babysit` 与本步骤共用该预算。安全、认证、数据丢失或并发风险仍有 blocker / should-fix 时最多五轮。后续轮次只复查行为改动和未解决 findings；纯文档、正文、附件或格式变化不重跑代码测试，也不触发新一轮 review。达到上限就交付当前已验证状态和阻塞项。

High 风险达到第三轮仍无收敛时，先重新评估设计和根因；只有后续轮次能验证实质修复时才可用到五轮。不得重复提交已核实且无新证据的 finding。

## 描述最小格式

```markdown
<问题与解决方式，1–2 句>

### Change map
Base: `<sha>` · Head: `<sha>` · Coverage: <索引与分析限制>
![模块依赖变化图](./change-map.svg)

### Evidence
`<实际命令>` → <观察到的结果；行为变化时补充前后差异>

### Risk and recovery
Tier: <Low | Medium | High> · Reason: <依据 diff 的一句话>
Reversibility: <easy to reverse | hard to reverse> · Blast radius: <受影响模块或用户>
Rollback: <feature flag, revert, or recovery steps; state when reverting this PR is sufficient>
```

普通 PR 创建沿用 SVG 和简短正文，不为内部 pre-open 审查另写 Postplan。用户要求独立报告或任务符合 `references/postplan-reports.md` 的报告型场景时，再生成 Postplan。

## 移交

用户明确要求继续看 CI 或评论 → `pr-babysit.md`。
