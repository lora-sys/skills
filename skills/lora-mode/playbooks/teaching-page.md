# teaching-page — 教学 / 讲解类自包含 HTML

> 继承 SKILL.md 七步骨架与硬边界，本文件只写每步的具体动作。
> **适用**：讲解页、课件、story deck、架构 walkthrough、HTML 报告。**主导 skill**：teaching-html-story-deck。

## 步骤

1. **识别现状。** 加载 teaching-html-story-deck 并按其全程执行；明确受众、讲解目标、是否需要发布。单篇文章转 HTML、营销落地页不适用，改走 `web-feature.md`。
2. **核实事实。** 讲解涉及的技术论断查官方文档核实；不编造数据与引用。
3. **出计划。** 叙事主线蓝图（问题先行）+ 概念到图型的映射清单；需要 lora/Mochi 角色出场时调度 lora-visual，普通配图走 generate-image 并标注"AI 生成"。
4. **实现。** 按 teaching-html-story-deck：单文件、无构建、内嵌 SVG 图解、演讲者备注、键盘翻页、prefers-reduced-motion。
5. **验收（强制）。** 跑 validate_deck.py，不过不许交付；浏览器实际翻页检查（键盘、窄屏、动效降级）。
6. **隔离对抗审查（强制）。** 按 `../references/review-protocol.md`，重点：产物完整性、状态诚实、可访问性。
7. **按证据交付。** 校验脚本输出、翻页截图、文件路径。

## 证据形态

validate_deck.py 通过输出、浏览器翻页截图（含窄屏）、SVG 渲染检查。

## 移交

用户要公开链接 → `publish.md`（说"本地就行"则止于文件交付）。
