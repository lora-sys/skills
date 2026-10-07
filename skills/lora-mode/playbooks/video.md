# video — 短视频策划到多平台草稿分发（点名时进入）

> 继承 SKILL.md 七步骨架与硬边界，本文件只写每步的具体动作。
> **适用**：用户点名要走完整链路时；单条视频策划默认直接调度 samuel-video-coach。
> **主导 skill**：samuel-video-coach（策划）→ video-publisher（分发）。

## 步骤

1. **识别现状。** 输入材料（笔记/项目/经历）、目标平台、是否首次使用 video-publisher（首次先 onboarding：可用平台 + 默认平台）。
2. **策划。** 加载 samuel-video-coach：证据盘点 → 故事发动机 → 类型 → 标题封面 → 逐字口播 → 逐镜头分镜 → AI 转场清单 → 剪辑地图；结构化输出跑 validate_storyboard.py；缺失证据标【待补证据】，不虚构。
3. **出计划。** 分镜经用户确认（或用户授权代决并留痕）后列资产清单：封面图（按目标平台规格出：抖音封面 3:4/4:3，竖屏口播 9:16 是成片比例、封面常需另裁）、素材图（generate-image；角色走 lora-visual，标注"AI 生成"）、平台文案与标签（过 unslop）。
4. **制作资产。** 生成封面与素材并回读检查；视频成片剪辑不在本链路内（只做策划与草稿准备）。
5. **校验与分发。** 加载 video-publisher：首次使用先完成 onboarding（平台账号、默认平台、抖音话题，否则 check-package 必卡）→ check-package.mjs 校验内容包 → run-safe-platforms.sh 编排（inspect/quarantine/upload 并行 → mutate 串行 → verify 并行）。
6. **停在发布按钮前（强制，硬边界）。** 草稿停在最终发布按钮前，绝不代点；原创声明需两种真实信号之一；不用 cookie/凭据入库。
7. **按证据交付。** 分镜校验输出、各平台草稿验证结果（READY 需新鲜页面证据）、发布确认清单。

## 证据形态

validate_storyboard.py 输出、封面素材（标注 AI 生成）、四平台草稿 verify 结果。

## 移交

发布表现复盘 → 用户反馈后走 `investigation.md`；选题库沉淀 → notion（可选）。
