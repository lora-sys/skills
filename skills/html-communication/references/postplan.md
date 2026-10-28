# Postplan 配置速查

- 默认 API：`https://postplan.dev`
- CLI：`npx postplan`
- 凭据文件：Windows 下通常为 `%USERPROFILE%\.postplan\credentials.json`
- API key 环境变量：`POSTPLAN_API_KEY`
- API 地址环境变量：`POSTPLAN_API_URL`
- 凭据来源：已有的 `.postplan/credentials.json`，或由密钥管理器注入的 `POSTPLAN_API_KEY`
- 验证凭据：`npx postplan whoami`
- 发布：`npx postplan upload <file.html>`
- 查看账号 drafts：`npx postplan list`

上传接口为 `POST /api/uploads`，CLI 会输出公开 `URL`、`Raw HTML`、draft ID 和版本号。交付时返回两个 URL。不要把 key 作为 CLI 参数传入，也不要写入 HTML、仓库或日志。
