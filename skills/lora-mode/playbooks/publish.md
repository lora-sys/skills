# publish — 把 HTML / 站点发出去

> 继承 SKILL.md 七步骨架与硬边界，本文件只写每步的具体动作。
> **适用**：单页 HTML 要公开链接、静态站点发布。**主导 skill**：html-stable-publish（单页）、static-site-experience-release（站点发布段）。

## 步骤

1. **识别产物。** 单页 HTML / index.html 静态目录 / 站点仓库；确认是否已有旧版本要更新。
2. **发布前检查。** 单页：跑 html-stable-publish 的 preflight 脚本；站点：本地生产构建通过。产物里的外部链接用浏览器或截图通道实际打开核对，打不开的记入待核清单，不得默认可用。
3. **用户确认（强制，硬边界）。** 公开发布必须取得本次明确确认；说明发布到哪、谁能看到、是否可更新。不把此前授权当发布授权。
4. **执行发布。** 单页：html-stable-publish（npx postplan upload，凭据走本机配置，key 不写入产物）；站点：static-site-experience-release 的分支发布段（本地生产预览 + Lighthouse 通过后合并推送）。
5. **回验（强制）。** 打开公开 URL 实际验证：内容完整、资源加载、交互可用；记录 URL、draft ID、版本。
6. **按证据交付。** 公开链接、回验截图、发布记录（时间、版本、如何更新/回滚）。

## 证据形态

回验截图（真实打开的公开 URL）、preflight/构建输出、版本记录。

## 移交

发布后发现体验问题 → `static-site-release.md`；更新迭代 → 回本 playbook 重复 2–5。
