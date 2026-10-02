---
name: generate-image
description: 使用七牛云 Modelink（GPT Image 2 / Gemini 图像模型）生成或编辑图片。凡是要文生图、改图、去水印、扩图、风格迁移、生成海报/封面/插画/透明底素材/项目配图，或用户提到"生成图片、画一张、做张图、generate image、text-to-image、image editing"时都应使用。只要用户想得到一张位图输出，就用本 skill；只有代码级 SVG/图表才不用它。
license: MIT
metadata:
  version: "1.2"
  author: lora
  api: Qiniu Modelink (https://api.qnaigc.com/v1)
  primaryEnv: MODELINK_API_KEY
---

# Generate Image（七牛云 Modelink）

通过七牛云 Modelink 网关生成和编辑图片，一个 key 可用 GPT Image 系列和 Gemini 图像系列。

## 何时使用

**用它：** 照片级图片、插画、海报和封面视觉、概念图、项目配图、带透明底的素材、图片编辑与多图合成。

**不用它：** 流程图/架构图/电路图等代码级示意图（用 SVG/HTML/CSS 直接画）、矢量 logo 且必须是 SVG 格式（同样代码画）。仓库里的 `step_image`（StepFun）是另一个可选的图像后端，本 skill 是默认首选。

## API Key

调用脚本按以下顺序解析 key（**绝不硬编码、绝不写进仓库文件**）：

1. `--api-key`（仅一次性使用，避免出现在共享日志里）
2. `MODELINK_API_KEY` 环境变量
3. `~/.modelink/.env`（推荐：在仓库外，天然不会被 git 提交）
4. 工作目录向上搜索到的 `.env` 文件（必须保持 gitignored）

没有 key 时脚本会退出并给出配置说明。key 在 Modelink 控制台创建。

## 快速开始

```bash
# 文生图
python scripts/generate_image.py "山顶日落，photorealistic，暖色，无文字"

# 编辑已有图片（图生图）
python scripts/generate_image.py "把天空改成紫色" -i photo.jpg -o edited.png

# 指定尺寸与质量
python scripts/generate_image.py "海报背景" --size 1536x1024 --quality high

# 透明底
python scripts/generate_image.py "吉祥物贴纸" --background transparent -o mascot.png
```

路径相对本 skill 目录。输出默认写到当前目录 `generated_image.<ext>`，扩展名跟随 API 返回格式。**生成后必须回读图片检查**：构图、画幅、文字是否正确，模型不会主动报错。

## 选模型

默认 `openai/gpt-image-2`。

| 需求 | 模型 |
| --- | --- |
| 默认，草稿到定稿全流程 | `openai/gpt-image-2` |
| 更高画质（2.5 系列，额外支持 `xhigh`/`max` 质量档） | `openai/gpt-image-2.5-flare`、`openai/gpt-image-2.5-sunburst` |
| 多图合成、GPT 反复做不好的对话式改图（备选） | `google/gemini-3.1-flash-image`（chat 路由，约 $0.067/张） |

在七牛刊例价下 **gpt-image-2 才是便宜的那个**：1024² 一张，low 约 $0.006、medium 约 $0.053、high 约 $0.211；Gemini 1K 图约 $0.067，比 GPT low 贵 10 倍。省钱靠 quality 档位，不靠换模型。路由由脚本自动处理：模型名含 `gemini` 走 chat 接口，其余走 images 接口。

## 参数按模型路由分流

发一个模型不支持的参数会被拒绝，脚本会在**发请求前**本地拦截并提示：

- **GPT Image 系列（images 路由）**：`--size`（`auto`、`宽x高` 或预设 `1024x1024`/`1536x1024`/`1024x1536`/`2048x2048`/`2048x1152`/`3840x2160`/`2160x3840`；自定义要求 16 的倍数、最长边 ≤3840、长短边比 ≤3:1、总像素 655360–8294400）、`--quality`（low/medium/high/auto）、`--background`（auto/transparent/opaque）、`--output-format`（png/jpeg/webp）、`--output-compression`（0–100，仅 jpeg/webp）、`--n`（多张，上游透传）。
- **Gemini 系列（chat 路由）**：`--aspect-ratio`（1:1、16:9、9:16、4:3、3:2、21:9 等 14 档）、`--resolution`（512/1K/2K/4K）、`--output-format`（png/jpeg，部分 gemini lite 模型默认 jpeg）。

`--dry-run` 免费打印完整请求体，先验证再花钱。

## 写 prompt

prompt 质量比选模型更影响产出。每方面一句话：

1. **主体**——画面里有什么、占多大。"一支移液枪头悬于 96 孔板上方。"
2. **媒介与风格**——摄影、水彩、3D 渲染、扁平矢量、科学插画。
3. **光影与色板**——"柔和漫射光，冷蓝白配色。"
4. **构图**——"广角，主体偏左，右侧留白放标题。"（给海报/幻灯片留标题位是最有用的构图指令）
5. **排除项**——"无文字、无标签、无水印。"

迭代措辞时走下面的「默认工作流」。

## 默认工作流：GPT low 草稿，GPT high 定稿

**全程用 `openai/gpt-image-2`，省钱靠 quality 档位：**

1. **草稿/迭代**：`--quality low`（1024² 约 $0.006/张），快速试措辞、构图、风格，随便废
2. **定稿**：措辞认可后，用定稿 prompt 以 `--quality high` 正式出图（1024² 约 $0.21/张，海报/封面首选）；质量要求一般的配图用 `medium`（约 $0.053）即可；要微调而非重画时，把 low 草稿作为 `-i` 参考图喂给定稿请求
3. **Gemini 只做特殊场景备选**：多参考图合成、GPT 反复做不好的对话式改图；不要用它出草稿——七牛价格下它比 GPT low 贵约 10 倍

简单一次性图片直接 medium/high 一步出图，跳过草稿。价格为刊例价估算，以控制台账单为准。

## 编辑与参考图

`-i/--input` 可重复，最多 16 张；接受本地路径、HTTP(S) URL 或 data URL。本地文件自动 base64 编码。支持 png/jpeg/webp/gif。

```bash
# 单图编辑
python scripts/generate_image.py "给这个人加上墨镜" -i portrait.png

# 多图合成
python scripts/generate_image.py "把这两种风格融合" -i style_a.png -i style_b.jpg -o blend.png
```

编辑时指令要具体："把天空换成日落色" 好过 "改一下天空"。

## 脚本参数

| 参数 | 作用 |
| --- | --- |
| `prompt` | 图片描述或编辑指令（必填） |
| `-m`, `--model` | 模型 ID（默认 `openai/gpt-image-2`） |
| `-o`, `--output` | 输出路径（默认 `generated_image.<ext>`） |
| `-i`, `--input` | 参考图：路径/URL/data URL，可重复，最多 16 张 |
| `--n` | 单次请求数量（gpt-image，上游透传） |
| `--size` | `auto`/`宽x高`/预设（gpt-image） |
| `--quality` | low/medium/high/auto（gpt-image；2.5 另有 xhigh/max） |
| `--background` | auto/transparent/opaque（gpt-image） |
| `--output-format` | png/jpeg/webp |
| `--output-compression` | 0–100，仅 jpeg/webp |
| `--aspect-ratio` | 画幅比例（gemini） |
| `--resolution` | 512/1K/2K/4K（gemini） |
| `--api-key` | 临时覆盖 key 解析 |
| `--base-url` | 覆盖 API 地址（默认 `https://api.qnaigc.com/v1`） |
| `--timeout` | 单请求超时秒数（默认 300） |
| `--retries` | 429/5xx/网络错误重试次数（默认 2） |
| `--dry-run` | 打印请求体后退出，不发送不计费 |
| `--list-models [FILTER]` | 列出网关模型 ID（可子串过滤），免 key |

## API 形态（不经脚本直连时）

```bash
curl -s https://api.qnaigc.com/v1/images/generations \
  -H "Authorization: Bearer $MODELINK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "openai/gpt-image-2", "prompt": "白墙前的红色自行车", "quality": "high"}'
```

响应中 `data[].b64_json` 是裸 base64（非 data URL），`data[].output_format` 指示真实格式；`usage` 返回 token 与张数计数。图生图用 `POST /v1/images/edits`，`image` 字段接受 URL、data URI 或裸 base64 的数组。Gemini 系列走 `POST /v1/chat/completions`，图片在 `choices[0].message.images[].image_url.url`（data URL）。

## 注意事项

- **模型不可信于文字**：图内文字常拼错或乱码，需要文字时让模型"no text"，再用代码叠加真实文字。
- **生成图是插画不是证据**：永远不要把生成图当作显微、成像、实验结果的替代；配图需标注"AI 生成/示意"。
- **计费请求**：迭代措辞时用低质量/低分辨率省钱；`--dry-run` 免费。生成耗时约 5–60 秒。
- **隐私**：参考图会上传到七牛云网关，不要发送未公开的敏感数据或受隐私约束的图片。
- **安全**：key 只放环境变量或 gitignored 文件；不要写进仓库、日志或截图。一旦泄露立即在控制台禁用并轮换。
- **拒绝**：内容政策拒绝通常表现为无图返回或 400/403，改写措辞重试；临床与解剖类题材更容易触发。
- 429/5xx 自动重试；4xx 不重试——那说明请求本身要改。
