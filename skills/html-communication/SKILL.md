---
name: html-communication
description: Create standalone HTML reports, teaching pages, diagrams, and static pages, and publish them to Postplan as public drafts by default. Use when creating an HTML deliverable unless the user explicitly requests local-only output.
---

# HTML communication through Postplan

## 适用范围

处理单个 HTML 文件，或根目录包含 `index.html` 的静态页面。默认使用 `https://postplan.dev` 的官方 `postplan` CLI 发布公开 draft。同一 HTML 文件再次上传时，默认更新对应 draft。

## 默认发布行为

- 用户通过本技能请求 HTML 交付物时，默认在完成内容和发布前检查后上传到 Postplan；标准公开 draft 不需要另行询问上传确认。
- 用户明确要求本地草稿、离线文件或不上传时，只交付本地产物。
- 此默认行为只适用于 Postplan 公开 draft；生产网站、域名托管或其他外部平台不在默认授权范围内。

## 凭据与内容安全

- 使用已有的 `.postplan/credentials.json`，或由密钥管理器注入 `POSTPLAN_API_KEY`。API 地址可用 `POSTPLAN_API_URL` 覆盖，默认是 `https://postplan.dev`。
- 如果没有凭据，请让用户通过安全配置方式提供。不要把 API key 放进命令行参数、shell 历史或日志。
- 绝不把 API key 写入 HTML、项目文件、日志、对话回复或版本库。
- 上传前检查最终 HTML 及将要上传的资源。移除或匿名化密码、令牌、个人身份信息、私有客户数据、原始对话、线程 ID/链接、本机绝对路径、内网地址和未公开资源。
- 能安全删减时，先生成不含这些内容的公开版再继续；如果无法判断哪些内容可公开，暂停上传并向用户澄清。不要上传 `.env`、私密附件或整个源码/依赖目录。

## 发布流程

1. 确认产物是单个 HTML，或目录中存在 `index.html`。对目录发布时先准备干净的构建输出目录。
2. 运行 `scripts/preflight_static_site.py <文件或目录>`，修复入口、绝对本地路径和敏感文件问题。该检查是发布前辅助检查，最终 HTML 规则仍以 Postplan CLI 返回的验证结果为准。
3. 检查最终公开内容和资源，按上面的规则清除私密信息。除非用户明确要求仅本地交付，否则直接继续发布，不再询问标准 Postplan draft 的上传确认。
4. 发布或更新 draft：

   ```sh
   npx postplan upload <html-file> --description "简短说明"
   ```

   可选参数：`--new`（用户要求创建新 draft 时使用）、`--api-url <url>`。
5. 打开 CLI 返回的公开 URL 检查页面，并读取 Raw HTML URL，确认两者均可访问且内容与本地产物一致。检查失败时修复并更新同一 draft，再复核。
6. 返回公开 URL、Raw HTML URL、draft ID 和版本号，明确说明这是 Postplan 公开 draft，不是永久生产托管。用户明确要求仅本地交付时，说明未发布并返回本地文件位置。

## 常用命令

```sh
# 检查已配置的凭据
npx postplan whoami

# 发布或更新页面
npx postplan upload <file.html> --description "页面说明"

# 查看当前账号的 drafts
npx postplan list
```

## HTML 限制

Postplan 会在上传时拒绝外部脚本、module script、事件处理属性、`javascript:` URL、表单、iframe/embed/object/applet 以及 meta refresh。允许语义 HTML、内联 CSS、普通 HTTPS 链接、HTTPS/data 图片，以及受平台规则允许的内联经典 JavaScript。页面不应依赖本地文件路径或未公开资源。

## 参考

需要核对 CLI 参数、凭据位置或 API 行为时，读取 `references/postplan.md`；不要再使用旧的匿名 Drop/Netlify 流程。
