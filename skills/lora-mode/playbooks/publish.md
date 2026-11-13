# publish: 把 HTML / 站点发出去

> **适用**：单页 HTML 要公开链接。**主导 skill**：html-communication。

存量静态站的体验改造与站点发布走 `static-site-release.md`。

## 步骤

1. **识别产物。** 确认单页 HTML，并确认是否已有旧版本要更新。
2. **发布前检查。** 跑 html-communication 的 preflight 脚本。产物里的外部链接用浏览器或截图通道实际打开核对，打不开的记入待核清单，不得默认可用。
3. **按发布目标应用授权。** 标准 Postplan 公开 draft 遵循 `html-communication`：默认直接发布或更新，不另行确认；用户要求仅本地交付时不上传；无法判断哪些内容可公开时先不上传，完成安全本地版并对公开范围提出具体澄清。生产站点、域名托管或其他外部平台发布仍需本次明确授权，说明目标、可见范围和回滚方式。
4. **执行发布。** 按 html-communication 执行 `npx postplan upload`；凭据走本机配置，key 不写入产物。
5. **回验（强制）。** 打开公开 URL 实际验证：内容完整、资源加载、交互可用；记录 URL、draft ID、版本。
6. **按证据交付。** 公开链接、回验截图、发布记录（时间、版本、如何更新/回滚）。

## 证据形态

回验截图（真实打开的公开 URL）、preflight 输出、版本记录。

## 移交

发布后发现体验问题 → `static-site-release.md`；更新迭代 → 回本 playbook 重复 2–5。
