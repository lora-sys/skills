# Issue / PR SVG 变更图

Issue 和 PR 正文默认附一张自包含 SVG。它是给人审查的图，也带有 Agent 可解析的结构化记录。日常流程不另写 HTML 报告；复杂图或用户要求独立页面时才准备 Postplan 报告。

GitHub 支持 SVG 附件，`gh pr create/edit` 和 `gh issue create/edit` 可用 `--attach <file.svg>` 上传并将正文里的本地图片引用替换成附件 URL。其他 tracker 使用其支持的图片附件方式。草稿交付时同时给 Markdown 正文和本地 SVG 文件，不把本机路径当成远端 URL。

用 `scripts/render-impact-svg.py <graph.json> --output <map.svg>` 从短 JSON 图数据生成 SVG。渲染脚本只绘图，不读取源码或推导依赖；Agent 必须先准备有证据的 JSON，不要把“图已生成”当成依赖分析已验证。不要手写大段 SVG。JSON 字段、PR/Issue 示例和错误检查见 `evals/fixtures/e14-pr/map.json`、`evals/fixtures/e16-issue/map.json` 和渲染脚本。

## SVG 内容

每张图包含可见图形和机器可读的 SVG 元数据：

```xml
<title>简短图标题</title>
<desc>一句话说明图表达的变化、范围和主要未知。</desc>
<metadata id="lora-change-map-v1">{"schema":"lora-change-map/v1","kind":"pr","scope":"分析范围","base":{"sha":"..."},"head":{"sha":"..."},"nodes":[{"id":"...","label":"...","status":"added|modified|deleted|affected|unchanged","phases":["base","head"],"evidence":"...","confidence":"confirmed|reported|inferred|unknown"}],"edges":[{"from":"...","to":"...","relationship":"depends-on|calls|event","phase":"base|head","change":"unchanged|added|removed","evidence":"...","confidence":"confirmed|reported|inferred|unknown"}],"unknowns":["..."]}</metadata>
```

PR metadata includes `base`, `head`, per-edge `phase` and `change`; each node's `phases` lists where it exists. Issue/state metadata omits those fields; node status is limited to `observed`, `expected`, `unknown` or `inferred`. Every edge must name its relationship, and the legend explains that arrows run from the `from` node to the `to` node; it must not imply every edge is a dependency.

SVG 要求：

- 文件自包含，不含脚本、外链字体、远程图片或动画。
- 图中节点名称使用人能识别的模块或状态名。节点直接写 `新增`、`修改`、`删除`、`受影响`、`观察到`、`期望` 或 `待确认`；颜色只作辅助，不能单独承载含义。
- `<desc>` 说明图的读法。`<metadata>` 内嵌符合 `lora-change-map/v1` 的 JSON，记录节点状态、依赖/事件边、边类型、证据来源、确认状态、分析范围和未覆盖项；PR 同时记录 base/head SHA 和影响距离。把 JSON 作为 XML 文本安全转义，保证附件可被脚本或 Agent 解析。
- 边使用箭头表达方向；`A → B` 表示从 A 指向 B，具体关系看边标签。依赖边可读作“A 依赖 B”；事件边可读作“A 流向 B”。实线只表示已由源码、配置或运行证据核实的 `confirmed` 关系；`reported`、`inferred`、`unknown` 都用虚线，并在边上标“报告”“推测”或“待确认”。删除边也用虚线。节点也用短文字区分报告、推断和待确认状态。
- 控制图的范围，只显示本次改动或问题涉及的模块和必要上下游，不尝试画全仓库。节点过多时先按包或子系统聚合，不能隐藏跨边界影响。

## PR 依赖图

- 从目标分支 merge-base 和当前 head 取证，记录两个 SHA。仓库已有 `.codegraph/` 且 CLI/MCP 可用时，用 CodeGraph 导航；没有索引时遵从仓库说明和用户选择，默认不初始化。用户选择启用后，每仓库只运行一次 `codegraph init`。MCP 服务运行时 watcher 增量同步，重连时补齐离线变化；watcher 不可用或在 MCP 外查询时，分析前运行一次 `codegraph sync`。不设定时任务或周期性全量重建。若 CLI/MCP 未安装，不静默修改机器级 agent 配置，改用 diff、源码和项目配置取证，并在 Coverage 中说明。记录索引对应的提交；索引只覆盖一个版本时，只把它作为该版本的导航证据，另一版本须从对应源码、配置或可用索引补证。
- 只有检查到足以支持关系的具体源码、配置或运行证据，才将边标为 `confirmed` 并填写 evidence；用户/Issue 提供的关系标 `reported`，静态推断标 `inferred`，没有证据标 `unknown`。非 `unknown` 节点和边都必须填写 evidence。缺失 confidence 默认 `unknown`，不默认当作事实。
- Base 与 Head 上下排列，以便缩放到 PR 正文宽度后仍能读清节点。依赖拓扑未变化时也画前后状态图，并明确写“依赖拓扑未变化”。
- 画出新增、删除、修改的模块与依赖边变化，以及直接受影响的未改消费者。对照 diff 核对节点和边。
- 元数据记录关系证据来自 import、调用、配置、CodeGraph、运行时复现或报告者陈述。标出反射、插件发现、配置路由、运行时数据流等静态分析未覆盖关系；不要把 CodeGraph 未显示的边说成不存在。
- 文档专属改动照样给图，并写明“源代码依赖图未变化”。局部图不能称作完整调用图。

## Issue 路径图

- Bug 图表达报告者动作、观察到的结果和期望结果。Feature 图表达当前路径与目标路径。
- 证据不足时只画已知信息和等待补充路径。模块线索若未经源码或日志确认，标作候选节点并用虚线连接。
- SVG 中同时提供 `<desc>` 和文本标签，避免图成为唯一的信息载体。元数据列出未知项和来源。
- 只有需要验证并发、协议或跨状态不变量时，才使用 pstack `statechart` / TLA+ / TLC。先确认要验证的状态规则；普通 Issue 不做形式化建模。

## 描述正文

PR 正文保留 Why、改动范围、风险和真实验证结果，并嵌入附件：

```markdown
### Change map
Base: `<base SHA>` · Head: `<head SHA>` · Coverage: <工具与限制>

![Base 到 Head 的模块依赖变化图，图例解释新增、修改、删除、受影响节点及依赖箭头](./change-map.svg)
```

Issue 正文保留问题/目标、实际与期望行为、验收条件和未知项，并嵌入附件：

```markdown
### Issue map
![已观察路径、期望路径与待确认模块关系图](./issue-map.svg)
```

给 GitHub CLI 时用 `--attach change-map.svg` 或 `--attach issue-map.svg`。CLI 会上传附件并替换正文中的本地图片引用。没有创建/更新授权时只交本地草稿；不执行 tracker 写入。

若本任务已经生成并获准公开 Postplan 报告，在 PR / Issue 正文加一条补充链接；SVG 仍是内嵌主图，不要复制成长报告。不要为满足这个链接而自动公开发布。

## Agent 自查

交付前逐项核对 SVG 和图内 JSON：

- 图中新增、删除、修改节点是否与实际 diff 一致？
- 依赖边是否能从源码、索引或配置找到证据？边的方向和类型是否正确？
- 是否遗漏直接受影响的模块或消费者？跨模块改动是否说明原因和验证？
- base/head SHA、图例、覆盖范围和未知项是否准确？
- Issue 的观察路径是否来自报告者信息或真实复现？期望是否清楚标为目标而非当前行为？
- 视图中每个状态是否有文字标签，元数据是否可解析，SVG 是否自包含？

图用于快速定位审查范围，不能替代复现、测试或代码审查。关键行为仍须用真实运行、测试或受控复现核验。

## Postplan 例外

只有当 SVG 无法承载必要上下文、用户要求独立网页，或项目规则要求完整报告时才生成 HTML。加载 `html-stable-publish`，运行 preflight；上传前按本次任务取得公开发布确认，并检查页面不包含私密代码、Issue 原文、分支名、凭据或内网 URL。私有内容使用 tracker 附件或用户指定的私有报告位置。
