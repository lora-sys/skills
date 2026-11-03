# 形式化验证与 Statechart 路由

## 何时使用

用户明确要求模型与实现对齐或证明不变量时，直接进入形式化验证路由；其他任务只有源码证据表明用户承诺依赖事件顺序、并发交错、重试、协议阶段或跨状态不变量且常规测试难以覆盖时才触发。先按 [`verification-routing.md`](./verification-routing.md) 筛性质，再从相关源码、调用方和现有测试选出一个可验证的用户承诺；不要因项目领域或术语本身触发。形式化门槛满足且项目没有覆盖该性质的验证时，必须读取并执行 `../../create-formal-verification-skill/SKILL.md`，实际留下项目级验证技能和模型；不能只写计划、只补普通测试或因本机缺少工具而跳过建模。已经存在覆盖该代码的项目验证时，加载 `maintain-formal-verification-skill` 维护它，不重复创建。

事件顺序或并发交错默认使用 TLA+ 状态模型；工具可用且模型能对应源码原子步骤时，读取 `../../statechart/SKILL.md` 并用 TLC 检查、输出状态图和反例路径。只有无法忠实建模、验证器不可用或成本与问题不成比例时，才改用其他验证方法；说明选择依据和覆盖边界。不要以装饰性状态图或手写穷举脚本替代可用的模型检查器。

仅仅涉及状态、调用链或有 Mermaid 图，不足以触发形式化验证。普通 PR/Issue 的 Change map 继续使用 [`change-impact.md`](./change-impact.md)，只描述由 diff、源码、配置或运行记录支持的模块与依赖关系。

## 工具分工

| 工具 | 用途 |
|---|---|
| CodeGraph | 在已经存在且可用的索引中导航符号、调用方和静态依赖；索引缺失时使用源码、配置和测试，不初始化索引。 |
| `create-formal-verification-skill` | 从项目中选择高风险性质，生成项目本地、可复跑的验证技能，并用破坏性质的真实代码变体验证它能失败。 |
| `statechart` | 检查 TLA+ 状态模型，生成包含违反规则的最短路径的报告和 Mermaid 状态图。仅在已有或本任务建立了 TLA+ 模型时使用。 |

这些能力互补。Statechart 不检索源码依赖，也不能替代 CodeGraph；CodeGraph 不证明状态机不变量，也不能替代 TLC。需要描述 PR 影响时，仍单独生成 Change map。

## 执行边界

- 先将模型中的动作、原子步骤和不变量逐项对应到实际源码。Model checker 的 PASS 只说明给定模型、边界和假设，不自动证明真实程序正确；把每条反例路径带回实现验证。
- `statechart` 输出的 `.mmd` 可用于阅读模型中的状态迁移。报告应同时说明验证范围、边界、未建模行为，以及被压缩或隐藏的步骤。不能把模型状态图当作 PR 影响图。
- 在仓库外、由本任务创建的 scratch 目录运行，并为输出指定新目录或空目录。脚本会拒绝非空输出目录；不得将用户目录或已有验证材料作为输出目录。
- 此仓库的 Statechart CLI 不会自动安装工具。先检查固定版本的 TLC 与 Java 是否已具备；缺失时说明依赖和安装命令并等待用户授权，或使用已具备的验证器。获得授权后手动安装，再运行 CLI。
- 只有用户要求 PNG/SVG 或 Mermaid 文本过大难以阅读时，才按 [`statechart` 的 render.md](../../statechart/references/render.md) 使用 Pele 渲染；普通 PR/Issue 正文保留 Mermaid 源文本，不生成附件。
- 结束时删除本任务创建且确认无用的 scratch 目录和输出；保留的证明材料要写明位置与用途。不要删除目录之外或归属未确认的文件。

## 创建、复用与维护

- 改动前核对项目是否已有覆盖目标源码与性质的验证技能、模型、测试和最后验证的 commit；名字相近但覆盖不同代码不算已覆盖。
- 并发任务同时具备以下证据时，对能映射成有限状态的流程增加模型检查，并保留真实实现回归测试：(1) 性质保护容量、唯一所有权或至多完成一次等安全结果；(2) claim/lease、过期、重试/接管和完成等至少两种异步步骤会交错；(3) 普通测试只能复现选定调度，无法覆盖生命周期组合。仅有主题名称、线性状态图或单一且已原子保护的竞态不满足该门槛。
- 没有合适覆盖且形式化验证满足上面的触发条件时，必须读取并执行 `create-formal-verification-skill`，在项目内实际创建可复跑的项目验证技能、性质模型与源码映射，并在隔离副本验证检查能发现被破坏的性质。不能只描述将来要创建的验证。
- 形式化路由一旦满足，不能因定向/压力测试已通过或本机缺少 TLC/Java 而跳过建模。始终先创建项目验证技能和可映射模型；工具缺失时仍把模型技能标为 `draft / blocked`，列明缺失工具与预期命令，保留实现回归测试，不更新 sync commit，也不声称形式化通过。缺工具限制的是模型执行与破坏变体复测，不是验证工件创建。
- 实现后，对覆盖源码的修改调用 `maintain-formal-verification-skill`：复跑原检查，确认模型动作仍映射真实代码；仅在语义变化使模型不再准确时更新模型与覆盖记录。不能为让检查通过而弱化性质。
- 只有通过检查且确认覆盖映射对应当前代码后，才更新验证记录中的 sync commit。若覆盖代码仍处于未提交工作树，记录具体 dirty worktree 的验证证据并保留上一个已提交 sync commit；待改动提交后再核对并推进 sync commit。性质变化未经需求授权、模型与实现不一致、验证器缺失或执行失败时，保留旧 sync commit 并报告为未验证/受阻；不得安装依赖或伪称通过。

## 上游与同步

- `statechart`：[`cursor/plugins/pstack/skills/statechart`](https://github.com/cursor/plugins/tree/4dd1d05818d19792e7cd6e818f1667f95f7e1dbe/pstack/skills/statechart)，上游 Cursor commit `4dd1d05818d19792e7cd6e818f1667f95f7e1dbe`；对应独立镜像 `backnotprop/pstack` commit `25abb38559ddbabec563646224d09eff9a250eca`。本地补充相对 `JAVA` / `TLA2TOOLS` 路径解析、TLA+ 不安全整数拒绝、超大区间投影限制、缺工具时不自动安装及对应回归测试。
- `create-formal-verification-skill`：[`cursor/plugins/pstack/skills/create-formal-verification-skill`](https://github.com/cursor/plugins/tree/4dd1d05818d19792e7cd6e818f1667f95f7e1dbe/pstack/skills/create-formal-verification-skill)，同一上游 commit；本地要求在临时副本或隔离工作树中执行破坏性复测，避免修改用户正在使用的工作树。
- 两个技能各自目录保留 pstack MIT License。同步前查看 Cursor 上游与独立镜像的差异，不从镜像仓库根目录整体覆盖；保留许可证，更新来源 SHA，并运行本地 skill validator、statechart 脚本测试与本文件规定的路由 eval。
