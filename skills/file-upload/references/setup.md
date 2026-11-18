# R2 与签名服务搭建

本文只写一次性搭建步骤。日常上传见 `SKILL.md`。

## 当前部署（lora-sys）

以下为本仓库当前已部署、可用的配置。密钥不在此列，只存于 Worker Secret 和本地 env。

| 项 | 值 |
| --- | --- |
| 桶 | `lora-assets` |
| 公开域名 | `https://assets.lorasys.de5.net` |
| 签名服务 | `https://asset-upload-signer.3526039967.workers.dev` |
| 生命周期 | `temp/` 前缀 90 天后删除；`release/` 长期保留 |
| 认证 | Bearer `UPLOAD_TOKEN` 或个人 Worker Secret（例如 `UPLOAD_TOKEN_LORA`） |

日常上传时，签名服务地址默认从上表读取。令牌优先从环境变量读取；macOS 未设置环境变量时，脚本读取当前用户 Keychain 中 service 为 `lora-file-upload` 的项目。其他平台通过 shell 环境设置 `UPLOAD_TOKEN`。

macOS Keychain 项必须允许当前用户在无交互提示下读取。上传脚本禁用钥匙串认证弹窗；如果读取权限不足，它会报错退出。脚本检测到标准代理环境变量后，会自动启用 Node 的代理支持。

```bash
export UPLOAD_SIGNER_URL="https://asset-upload-signer.3526039967.workers.dev"
export UPLOAD_TOKEN="<本地保管的 UPLOAD_TOKEN>"
```

验证端到端可用：`curl -s "$UPLOAD_SIGNER_URL/health"` 返回 `{"ok":true,...}`。

## 0. 原则

- 密钥只存两处：Cloudflare Worker Secrets，本地 shell 环境或 gitignored 的 `.env`。
- 绝不把 `R2_SECRET_ACCESS_KEY`、`UPLOAD_TOKEN` 写进仓库、SKILL.md、命令行参数或 PR 正文。
- 文件字节只走「客户端 → R2」。Worker 只签发短时效 URL，不接收文件内容。
- 所有验证资产进入 `temp/` 前缀，默认 90 天后由 R2 生命周期规则自动删除。正式发布资产进 `release/`，不设过期。

需要的环境变量：

| 变量 | 位置 | 用途 |
| --- | --- | --- |
| `R2_ACCOUNT_ID` | Worker Secret | 构造 S3 endpoint |
| `R2_ACCESS_KEY_ID` | Worker Secret | R2 API Token 的 Access Key ID |
| `R2_SECRET_ACCESS_KEY` | Worker Secret | R2 API Token 的 Secret |
| `R2_BUCKET` | Worker Secret | 桶名 |
| `UPLOAD_TOKEN` | Worker Secret + 本地 env | 兼容令牌；调用 `/presign` 的 Bearer 令牌 |
| `UPLOAD_TOKEN_<OWNER>` | Worker Secret | 个人令牌；不覆盖其他客户端使用的 `UPLOAD_TOKEN` |
| `UPLOAD_RELEASE_TOKEN` | Worker Secret + 仅发布时本地 env | 使用 `release` 永久保留时必须单独提供的令牌 |
| `R2_PUBLIC_BASE_URL` | Worker var（wrangler.toml）+ 可选本地 env | 拼接公开链接的域名根 |
| `UPLOAD_SIGNER_URL` | 本地 env | Worker 根地址，例如 `https://asset-upload-signer.<subdomain>.workers.dev` |

## 1. 建专用桶

在 Cloudflare Dashboard → R2 → Create bucket，建一个专用桶，例如 `lora-assets`。桶名只用于本上传流程，不混放其他数据。

CLI 等价命令（需已登录 `wrangler login`）：

```bash
npx wrangler r2 bucket create lora-assets
```

## 2. 绑定文件域名

Dashboard → R2 → 选中桶 → Settings → Custom domains → Connect domain，填入你的子域，例如 `assets.example.com`。前提是该域名在同一 Cloudflare 账户的 zone 中；按提示添加 CNAME 记录。

注意：API Token 必须包含 `Zone → DNS → Edit` 权限，否则 Cloudflare 无法自动创建所有权与 CNAME 记录，域名会一直停在 `pending`。CLI 等价命令：

```bash
npx wrangler r2 bucket domain add lora-assets \
  --domain assets.example.com \
  --zone-id <YOUR_ZONE_ID> -y
```

绑定后用 API 查状态，等 `ownership` 与 `ssl` 都变为 `active` 才可用（通常数秒到数分钟）：

```bash
curl -s -H "Authorization: Bearer $CF_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/r2/buckets/lora-assets/domains/custom"
```

不要用 `*.r2.dev` 的公开地址做长期链接：它是共享测试域，不适合正式 PR 证据。

设置完成后把域名根填入 `worker/wrangler.toml` 的 `R2_PUBLIC_BASE_URL`，注意末尾不要带斜杠：

```toml
[vars]
R2_PUBLIC_BASE_URL = "https://assets.example.com"
```

## 3. 配置 CORS（浏览器直传需要）

浏览器用预签名 URL PUT 时，R2 必须允许对应来源。Dashboard → R2 → 桶 → Settings → CORS policy，添加：

```json
[
  {
    "AllowedOrigins": ["https://example.com", "https://app.example.com"],
    "AllowedMethods": ["GET", "HEAD", "PUT"],
    "AllowedHeaders": ["content-type"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3600
  }
]
```

`AllowedOrigins` 要与 Worker 的 `ALLOWED_ORIGINS` 保持一致。只用 curl / node 脚本上传时，CORS 不参与，但上传后 `upload.mjs` 会用 HEAD 校验公开链接；保留 GET/HEAD 配置可避免浏览器或预览面板中的校验失败。

### 视频编码要求

链接要能在 GitHub PR 中直接播放，视频必须使用 H.264 (AVC) + AAC 编码。macOS 录屏产生的 `.mov` 常为 HEVC 或 ProRes，浏览器无法内联播放。上传前用 `ffmpeg` 转码：

```bash
ffmpeg -i input.mov -c:v libx264 -pix_fmt yuv420p -crf 26 -preset veryfast -movflags +faststart -c:a aac output.mp4
```

`+faststart` 把 moov atom 移到文件头部，视频可边下边播。没有 `ffmpeg` 时可上传原文件，但必须如实告知「链接可下载，浏览器可能无法内联播放」。

## 4. 配置 90 天生命周期

Dashboard → R2 → 桶 → Settings → Lifecycle rules，新建规则：

- 规则名：`temp-90d`
- 前缀匹配：`temp/`
- 动作：对象创建 90 天后删除

不要给 `release/` 加过期规则。正式发布资产长期保留，需手动删除。生命周期规则的前缀过滤必须为 `temp/`，不能为空或根路径；否则 `release/` 资产也会被删除。

对象键由签名服务生成，格式为 `<retention-prefix>/<日期>/<清理后的文件名>-<时间戳>-<随机后缀>.<扩展名>`。自动重命名保证同名文件不互相覆盖，随机后缀避免冲突。`temp/` 对象 90 天后由 R2 直接删除，没有宽限期或恢复机制；需要长期保留的资产必须显式传 `--retention release`。

## 5. 创建 R2 API Token

Dashboard → R2 → Manage R2 API tokens → Create API token：

- 权限：Object Read & Write
- 范围：只选第 1 步的桶，不要给账户级权限
- TTL：按需设置；到期后轮换并更新 Worker Secret

创建后页面会显示 Access Key ID 和 Secret Access Key。**只在此刻复制一次**，不要贴进聊天、文档或代码。

## 6. 设置 Worker Secrets

生成上传令牌（本地生成，不要手写可猜测的值）：

```bash
openssl rand -hex 32
```

在 `worker/` 目录下逐个设置。每条命令都会交互式读取值，避免密钥进入 shell 历史：

```bash
cd worker
npx wrangler secret put R2_ACCOUNT_ID
npx wrangler secret put R2_ACCESS_KEY_ID
npx wrangler secret put R2_SECRET_ACCESS_KEY
npx wrangler secret put R2_BUCKET
npx wrangler secret put UPLOAD_TOKEN
# Add a separate personal token when a client must not share UPLOAD_TOKEN.
npx wrangler secret put UPLOAD_TOKEN_LORA
# 可选但推荐：发布资产的独立令牌；不设置则 release 上传一律失败
npx wrangler secret put UPLOAD_RELEASE_TOKEN
```

把第 5 步生成的令牌值用于 Worker Secret。个人令牌使用 `UPLOAD_TOKEN_<OWNER>`，例如 `UPLOAD_TOKEN_LORA`；脚本仍通过 `UPLOAD_TOKEN` 环境变量或 macOS Keychain 发送它。`UPLOAD_RELEASE_TOKEN` 应使用另一个随机值，只在需要永久保留资产时导出给客户端；日常验证流程不要设置它。

## 7. 部署签名服务

```bash
cd worker
npm install
npm run typecheck
npx wrangler deploy
```

部署输出会给出 Worker 地址，例如 `https://asset-upload-signer.<subdomain>.workers.dev`。

## 8. 配置本地客户端环境

macOS 配好当前用户的 Keychain 项后无需导出 `UPLOAD_TOKEN`。其他平台可在当前 shell 导出，或写进 gitignored 的 `.env` 后再 source。Keychain 项的 service 名称为 `lora-file-upload`，account 为当前系统用户名：

```bash
export UPLOAD_SIGNER_URL="https://asset-upload-signer.<subdomain>.workers.dev"
export UPLOAD_TOKEN="<第 6 步生成的同一个令牌>"
```

验证签名服务存活：

```bash
curl -s "$UPLOAD_SIGNER_URL/health"
# 期望: {"ok":true,"service":"file-upload-signer"}
```

## 9. 端到端验证

用一个小 PNG 走完整链路：

```bash
cd <skill 目录>
node scripts/upload.mjs /path/to/small.png --retention temp
```

成功时输出一行 JSON，包含 `url` 字段。打开该 URL，应能看到图片：

```bash
open "<输出的 url>"
```

失败排查：

- `401 unauthorized`：`UPLOAD_TOKEN` 与 Worker Secret 不一致。
- `429 rate limited`：一分钟内签名请求超过 10 次；等 60 秒。
- `400 unsupported file extension`：扩展名不在 `shared/policy.mjs` 的允许列表。
- `403` 且来自浏览器：CORS 的 `AllowedOrigins` 与实际来源不一致。
- 能上传但 URL 404：自定义域未绑定成功，或 `R2_PUBLIC_BASE_URL` 写错。

## 10. 轮换与撤销

- 令牌疑似泄露：立即 `npx wrangler secret put UPLOAD_TOKEN` 换成新值，并同步所有客户端 env。
- R2 Token 泄露：在 Dashboard 撤销旧 Token，创建新 Token，更新 Worker Secret 后重新部署。
- 不再需要服务：`npx wrangler delete`，再删除桶与自定义域绑定。
