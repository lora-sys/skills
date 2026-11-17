---
name: file-upload
description: 把截图、录屏、视频和指定文件上传到 Cloudflare R2，返回可放进 PR 的公开证据链接；当 lora-mode 验证/录屏/开 PR 需要 evidence 链接、用户说「上传这个 / 传截图 / 传录屏 / 传附件 / upload this asset / evidence link」时使用；不负责本地截图或录屏（由 run / agent-browser 产生），不写 PR 正文（由 file-pr / pr-open 负责），不上传密钥或私密文件。
---

# file-upload

把本地媒体文件上传到 Cloudflare R2，返回公开链接。文件字节直传 R2，密钥只在环境变量和 Worker Secret 中，不在本技能或仓库里。

## 触发与边界

- 自动模式：lora-mode 的 `web-feature` / `pr-open` 等流程产生验证媒体（截图、录屏）时，按项目 `AGENTS.md` 的规则主动调用本技能上传。
- 手动模式：用户说「上传这张图 / 传录屏 / 传这个文件 / upload this asset」时，直接上传用户指定的文件。
- 本技能只做上传与返回链接。截图、录屏由 `run` / `agent-browser` / `ego-browser` / `preview_recording` 产生；PR 正文由 `file-pr` / `pr-open` 写入。
- 不上传 `.env`、密钥、令牌、个人私钥或任何用户未授权公开的文件。上传前按「安全检查」过一遍。

## 两种模式

### 自动模式

满足条件时不等用户逐条确认，直接执行：本任务产生了验证媒体，且项目 `AGENTS.md` 要求「改完必须运行、录屏、上传、贴 PR」。步骤：

1. 收集本次任务产生的媒体文件（截图、录屏、指定附件）。路径来自验证命令或会话产物。
2. 逐个上传（见「上传一个文件」）。
3. 把返回的链接和对应验证结果交给 `file-pr`，由它写进 PR 正文。

- 只上传本次调用**显式列出**的文件路径。禁止扫描 `artifacts/`、`/tmp/evidence/` 或会话目录来「收集」媒体；目录里可能有无关的草稿、日志或密钥。
- 本次任务没有明确文件路径时，不上传；未完成验证或未产生媒体时也不上传。自动模式不扩大写入、部署或发布权限。是否开 PR 由当前 lora-mode 流程决定，不作为上传门槛。

### 手动模式

用户明确指定文件或路径时：

1. 确认文件存在且不属于「安全检查」中的禁传类型。
2. 按用户指定的 retention 上传；未指定用 `temp`。
3. 返回公开链接，并说明保留时长（temp=90 天 / release=长期）。

## 上传一个文件

```bash
node scripts/upload.mjs <file> [--retention temp|release]
```

- `--retention temp`（默认）：对象写入 `temp/` 前缀，90 天后 R2 生命周期规则自动删除。**验证截图、录屏一律用此值；用户说「正式留档」也先用 temp 并说明 release 的永久存储成本。**
- `--retention release`：对象写入 `release/`，不设过期。只用于用户明确说「正式发布 / 长期保留」且确认承担永久存储成本的资产。必须同时传 `--confirm-release`，并设置 `UPLOAD_RELEASE_TOKEN`；签名服务单独校验该令牌。
- 输出：一行 JSON，含 `ok`、`file`、`key`、`url`、`retention`、`size`、`verified`。把 `url` 原样交给 `file-pr`。

批量上传多个文件：

```bash
node scripts/upload-many.mjs [--retention temp] <file> [<file> ...]
```

每个文件输出一行 JSON，最后一行是汇总。单个失败不影响其他文件；失败项在 stderr 打印原因。

**批量预算**：默认最多 10 个文件、总计 1 GiB；超出时脚本直接拒绝，并提示分批或 `--force`。`--force` 只放开本地预算，单文件 500 MiB 和签名端限速不变。不要把整个 artifacts 目录通配进来；只上传显式列出的文件。失败后只重跑失败项，不重跑整批，避免重复对象和额外写入费用。

### 成本边界（必须遵守）

- R2 出站流量不收费，成本来自存储量、Class A 写入操作和 Worker 请求。
- `temp/` 对象 90 天后由生命周期规则删除；该规则已在线上核验为 `prefix: temp/`、`maxAge: 7776000`。不要手动把验证资产写成 `release/` 前缀。
- 签名端限速为每 IP 每分钟 10 次。遇到 `429` 时脚本明确报出等待秒数；**停止操作**，不要在等待期内重试或重跑整批。
- 当前配额以 Cloudflare Dashboard 为准；本技能不假定免费额度永不变。批量上传前按上面的预算自检。

脚本内部行为（无需手动干预）：

- 按 `shared/policy.mjs` 校验文件名、扩展名、大小（上限 500 MiB）和保留策略。
- 调用 Worker `/presign` 拿短时效（15 分钟）PUT URL；429 会报出 `retry-after` 并停止，不重试风暴；其他可重试错误带指数退避，最多 3 次。
- 直接 `PUT` 文件字节到 R2，不经过 Worker。失败重试 3 次；若 URL 过期（403）自动重新签名一次。
- 上传完成后用 `HEAD` 请求校验公开链接可访问；HEAD 只读取响应头，不会下载整个视频。校验失败时报告「上传成功但公开链接不可访问」，不返回坏链。
- 自动重命名：清理文件名、加 UTC 时间戳和随机后缀，避免同名覆盖；重复上传同一文件会生成新对象，因此不要重跑已成功的上传。

### 紧凑格式优先（节省存储和传输）

| 证据类型 | 首选 | 避免 | 原因 |
| --- | --- | --- | --- |
| 截图 | WebP / PNG | GIF | GIF 对屏幕内容体积非常大 |
| 录屏 | MP4 (H.264 + AAC) / WebM | MOV / M4V | MOV 常为 HEVC/ProRes，浏览器无法内联播放 |
| 附件 | 明确指定的小文件 | ZIP / 日志大文件 | 不在证据范围内时不要上传 |

不强制转换已有文件；只在需要转码或重新截图时，优先选择上表左侧格式。

### 视频可播放性

链接要能在 GitHub PR 中直接点开播放，视频文件必须满足：

- 容器为 MP4 或 WebM，编码为 **H.264 (AVC) + AAC**；带 `+faststart` 标志的 MP4 可在浏览器中边下边播。
- `.mov`（macOS 录屏默认格式）经常是 HEVC/ProRes，浏览器无法内联播放。上传前若本机有 `ffmpeg`，转码：

```bash
ffmpeg -i input.mov -c:v libx264 -pix_fmt yuv420p -crf 26 -preset veryfast -movflags +faststart -c:a aac output.mp4
```

- 没有 `ffmpeg` 时按原格式上传，并在回复中如实说明「链接可下载，但浏览器可能无法内联播放」。不为此阻塞其他工作。

## 环境变量契约

必填：

| 变量 | 说明 |
| --- | --- |
| `UPLOAD_SIGNER_URL` | 签名 Worker 根地址，如 `https://asset-upload-signer.<sub>.workers.dev` |
| `UPLOAD_TOKEN` | 调用 `/presign` 的 Bearer 令牌，与 Worker Secret 同值 |

可选：

| 变量 | 说明 |
| --- | --- |
| `R2_PUBLIC_BASE_URL` | 签名服务未返回 `publicUrl` 时的兜底域名根 |
| `UPLOAD_RELEASE_TOKEN` | 仅发布资产需要；与 Worker Secret `UPLOAD_RELEASE_TOKEN` 同值 |

验证资产流程不应设置 `UPLOAD_RELEASE_TOKEN`；这样即使误传 `--retention release` 也会在签名端失败。

搭建桶、域名、CORS、生命周期规则和 Worker Secrets 的完整步骤见 `references/setup.md`。首次使用或上传失败时先读该文档。

## 安全检查

上传前逐项确认，命中任一项则停止并说明原因：

- 文件名或内容疑似 `.env`、`.env.*`、`id_rsa`、`.pem`、`.key`、凭证或 token 文件。
- 目录含 `node_modules/`、`.git/`、`__pycache__/` 或构建产物缓存。
- 用户未明确授权公开的私人数据、个人信息、内部链接或敏感业务内容。
- 无法判断能否公开时：不上传，先就公开范围向用户提出具体澄清。

## 与 file-pr 的交接

本技能输出的是「链接 + 元数据」，不写 PR。优先用结构化 JSON 交接，把「链接 → 验证动作 → 命令结果」绑定成一条记录；`upload-many.mjs` 的原始 JSON 行可直接作为 `evidence` 数组元素：

```json
{
  "version": "1.0",
  "evidence": [
    {
      "claim": "checkout flow works with a valid cart",
      "command": "npm run test:e2e -- cart.spec.ts",
      "status": "passed",
      "mediaType": "video",
      "url": "<upload 返回的 url>",
      "originalFile": "artifacts/cart.mp4",
      "retention": "temp"
    }
  ]
}
```

`claim`、`command`、`status` 由调用方（lora-mode / file-pr）补齐；`file-upload` 负责 `url`、`originalFile`、`retention`、`size`。没有验证上下文时，退回简表：

```
- 文件：screenshot-wide.png → 链接：<url>（temp，90 天）
- 文件：flow.webm        → 链接：<url>（temp，90 天）
```

- 截图链接交给 `file-pr` 时必须写成 `![alt](url)`，不要写成普通链接；否则 PR 不渲染图片。
- 视频链接交给 `file-pr` 时写成可点击链接。GitHub 评论中的远程视频链接不保证内联播放，因此不得声称“已内联播放”。
- `file-pr` 将它们放进 PR 正文的证据区。链接必须是本次上传真实返回的值，不得编造或复用过期链接。

## 失败处理

- 配置类错误（缺 env、401、桶不存在）：读 `references/setup.md` 修复；属外部阻塞时如实报告，不假装上传成功。
- 文件类错误（类型不支持、超限）：按错误提示处理；用户坚持上传不支持类型时说明限制，不绕过校验。
- 网络类错误：脚本已自动重试；仍失败时报告错误码和文件，不重复手动盲试。
- 公开链接不可访问：R2 自定义域绑定或 CORS 未生效，按 `references/setup.md` 排查；不要返回坏链。
- 不得因为上传失败而阻塞其余独立工作；其他验证、PR 草稿照常完成，并把上传状态标为受阻。
