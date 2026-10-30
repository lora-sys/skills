# publish — 把 HTML / 站点发出去

> **适用**：单页 HTML 要公开链接、静态站点发布。**主导 skill**：html-communication（单页）、static-site-experience-release（站点发布段）。

## 步骤

1. **识别产物。** 单页 HTML / index.html 静态目录 / 站点仓库；确认是否已有旧版本要更新。
2. **发布前检查。** 单页：跑 html-communication 的 preflight 脚本；站点：本地生产构建通过。产物里的外部链接用浏览器或截图通道实际打开核对，打不开的记入待核清单，不得默认可用。
3. **按发布目标应用授权。** 单页走 Postplan 公开 draft 时遵循 `html-communication`：标准 draft 默认直接发布或更新，不另行确认；用户要求仅本地交付时不上传；公开内容安全性无法判断时暂停澄清。生产站点、域名托管或其他外部平台发布仍需本次明确授权，说明目标、可见范围和回滚方式。
4. **执行发布。** 单页：html-communication（npx postplan upload，凭据走本机配置，key 不写入产物）；站点：static-site-experience-release 的分支发布段（本地生产预览 + Lighthouse 通过后合并推送）。
5. **回验（强制）。** 打开公开 URL 实际验证：内容完整、资源加载、交互可用；记录 URL、draft ID、版本。
6. **按证据交付。** 公开链接、回验截图、发布记录（时间、版本、如何更新/回滚）。

## 证据形态

回验截图（真实打开的公开 URL）、preflight/构建输出、版本记录。

## 移交

发布后发现体验问题 → `static-site-release.md`；更新迭代 → 回本 playbook 重复 2–5。
