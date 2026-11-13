# AGENTS.md

> 本文件是面向所有协作维护本仓库的 AI Coding Agent（如 Codex、Claude Code、Cursor、Windsurf、Antigravity 等）的运行规范、操作守则与行为护栏。在对本仓库执行任何读写、审查或维护操作前，请完整遵循以下规则。

---

## 1. 项目定位与事实来源 (Single Source of Truth)

- **核心定位**：`lora-sys/skills` 是由 **lora-sys** 维护的高质量个人 Agent Skills 集合，用于工程提效、工作流路由、形式化验证、内容创作与静态发布。
- **唯一事实来源（SSOT）**：本仓库是所有技能的**权威事实来源**。
- **本地环境关系**：本地运行时环境（如 `~/.agents/skills/<skill-name>/` 或 `~/.codex/skills/`）仅为安装副本。
  - **发布流程（仓库 → 本机）**：在仓库完成修改、测试与提交后，通过 `npx skills add . --skill <name>` 或全局安装覆盖至本地。
  - **回写流程（本机 → 仓库）**：若在外部会话中临时调试或修改了本地已安装技能，必须先 `diff` 对照排查，确认无误后再回写至本仓库并提交，严防被后续发布覆盖。

---

## 2. 目录结构与技能规范 (Directory Layout & Standards)

```text
lora-skills/
├── README.md                      # 面向人类与总体介绍的项目文档
├── AGENTS.md                      # 面向 AI Agent 的行为守则与操作规范
├── LICENSE                        # 开源许可证（MIT）
├── skills-lock.json               # Skills CLI 锁文件
├── docs/                          # 安装提示词与辅助文档
├── skills/                        # 技能集合目录
│   └── <skill-name>/              # 独立技能目录
│       ├── SKILL.md               # 技能核心规范（必须包含合规 YAML frontmatter）
│       └── optional subdirs       # scripts/, references/, templates/, assets/, evals/
└── trace-evals/                   # lora-mode 历史轨迹盲测评估集与回归夹具
```

### 技能目录硬性规范
1. **统一命名**：目录名、`SKILL.md` 中的 frontmatter `name`，以及安装命令参数 `--skill <name>` 三者必须完全一致。
2. **顶层入口**：`SKILL.md` 必须直接位于 `skills/<skill-name>/` 根目录下，严禁嵌套在次级目录中。
3. **元数据完整**：`SKILL.md` 的 YAML frontmatter 必须包含准确、精炼的 `name` 与 `description`。`description` 应清晰指明触发关键词与应用场景，以便 Agent 路由正确激活。
4. **自包含性**：每个技能引用的辅助脚本、参考文档均需使用技能目录内部的相对路径，不得跨技能强耦合。

---

## 3. 行为护栏与绝对禁止事项 (Guardrails & Prohibitions)

- 🚫 **严禁手动修改上游镜像目录**：
  `skills/oil-frontend/` 与 `skills/oil-ui/` 是 [oil-oil](https://github.com/oil-oil) 的上游镜像，由 GitHub Action [`.github/workflows/sync-oil.yml`](.github/workflows/sync-oil.yml) 每日自动全量拉取并同步。**绝不要手动修改这两个目录中的任何文件**，任何手动提交均会在下次自动同步时被覆写丢失。
- 🚫 **严禁提交隐私凭据与密钥**：
  不得将任何真实 API Keys（如 OpenAI、Anthropic、七牛云等）、访问令牌、私有部署链接或个人敏感信息提交至 Git。
- 🚫 **严禁提交临时构建与测试产物**：
  提交前必须确认工作区干净，不得混入 `__pycache__/`、`*.pyc`、`.DS_Store`、测试截图、临时导出的 PPTX/视频或未清理的构建产物。
- 🚫 **严禁伪造测试结果与断言**：
  遵循诚实报告原则。未实际运行测试不能声称“已全部通过”，未核实的环境依赖不能假定其有效。受阻时必须如实记录阻碍原因与当前状态。
- 🚫 **严禁高危与不可逆操作**：
  未经用户显式要求与确认，禁止 `git push --force`、禁止在默认分支强行重写历史，禁止执行大范围不可逆的文件删除（如 `rm -rf` 未受控目录）。

---

## 4. 常用验证与维护命令 (Essential Commands)

### 技能元数据与安装检测
在修改或添加新技能后，必须运行以下命令验证 skills CLI 能否正确发现并解析该技能：
```bash
# 验证当前仓库全部技能是否能被正确解析
npx skills add . --list
```

### 漂移检测 (Drift Check)
在执行同步前，使用以下脚本快速比对仓库与本机全局安装副本是否存在差异：
```bash
for s in skills/*/; do
  name=$(basename "$s")
  diff -rq "$s" "$HOME/.agents/skills/$name" >/dev/null 2>&1 || echo "DRIFT: $name"
done
```

### 查看具体差异
若发现漂移，使用如下命令查看具体变更细节：
```bash
diff -u -r "skills/<skill-name>" "$HOME/.agents/skills/<skill-name>"
```

### `lora-mode` 盲测与回归
若涉及核心路由技能 `lora-mode` 的行为规则、权限或路由修改，按 [`trace-evals/test-plan.md`](trace-evals/test-plan.md) 运行对应的测试题目，不得修改 held-out 题目。

---

## 5. Agent 编码与文档风格指南 (Engineering & Writing Guidelines)

- **核心规范：ASD-STE100 简明技术英文标准（必须达到 80% 达标线）**：
  在撰写英文技术文档、PR/Issue 描述、工程审查意见及代码注释时，必须严格执行工程化写作规范，**达标率必须达到 ASD-STE100 启发式检查规则的 80% 以上（即 6 项规则中至少满足 5 项）**：
  1. **短句原则 (Short Sentences)**：使用简短、完整的句子；当一句话包含多个事实或步骤时，拆分为独立句子。
  2. **单句单一事实/动作 (One Fact/Action per Sentence)**：每句话仅表达一个核心事实或动作；步骤或序列统一使用编号/无序列表呈现。
  3. **主动语态与直陈祈使 (Active Voice & Imperative Mood)**：执行者明确时必用主动语态；流程与操作步骤直接使用祈使句（如 "Run `command`"）。
  4. **术语统一与词义明确 (Consistent Terms & Clarity)**：一个概念对应一个明确术语，严禁同义词交替；在保证语意准确的前提下优先使用简单明确的词汇。
  5. **名词短语清晰 (Clear Noun Groups)**：名词短语结构清晰严密，严禁为了盲目缩短句子而省略必要的定冠词或不定冠词（a/an/the）。
  6. **代词指代明确消歧 (Unambiguous Pronouns)**：当 `this`、`that` 或 `it` 存在多个潜在先行词或指代歧义时，必须显式指明具体主语或对象。
  *(注：该标准为工程文本质量与清晰度的硬性门槛；任何事实错误、证据缺失、歧义指代或危险操作指令一律立即修正。中文文档亦需遵从同等简明严谨原则。)*
- **无套话写作 (Unslop)**：
  撰写或更新技能说明、文档与 PR 说明时，保持语言简明、直接、信息密度高，杜绝虚浮的 AI 模板套话与过度润色（严格遵照 `unslop` 技能原则）。
- **注释与改动边界**：
  保持代码与配置文件的原有整洁性，不随意变更与任务无关的缩进、空行或注释。遵循最小必要变更原则（Minimal Intervention）。
- **Git 提交信息规范 (Conventional Commits)**：
  Git commit 采用规范的语义化消息，格式如：
  - `feat(<skill-name>): add xxx capability`
  - `fix(<skill-name>): correct xxx behavior`
  - `docs(<skill-name>|repo): update xxx documentation`
  - `chore(...): sync upstream / cleanup`
