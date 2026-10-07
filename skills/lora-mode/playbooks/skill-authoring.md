# skill-authoring — 写新 SKILL.md / 改进现有 skill

> 继承 SKILL.md 七步骨架与硬边界，本文件只写每步的具体动作。
> **适用**：用户点名写或改 skill 时。**主导 skill**：skill-creator。

## 步骤

1. **识别现状。** 加载 skill-creator；明确意图、触发面、期望输出；改现有 skill 保留原名与目录名。
2. **核实事实。** 触发面借鉴本仓库现有 description 的写法（中文、触发面优先、含不触发清单）；平台规范按 skill-creator。
3. **出计划。** SKILL.md 结构（正文 <500 行，细节进 references/scripts/assets）+ 2–3 条真实测试 prompt。
4. **实现。** 写草稿到仓库 `skills/<name>/`；从已有工作流提取步骤时不编造没发生过的规则。
5. **验收（强制）。** 逐条跑测试 prompt（新会话或子代理，一次一条）；子代理回传后与用户一起读结果；看触发、看输出、看是否制造忙活。
6. **迭代。** 按反馈改；顽固问题换框架而非堆规则；删不拉重量的内容。
7. **按证据交付。** 测试 prompt 的实际输出摘要、最终文件路径；README Skills 表加/改行，`skills-lock.json` 随发布流程更新；跨 agent 工具分发时，安装说明按目标工具改写（技能发现路径不同）。

## 证据形态

测试 prompt 输出摘要、迭代前后对照、文件路径与 README 行。

## 移交

无——skill 落盘即终点；使用反馈回来后重新进入本 playbook 迭代。
