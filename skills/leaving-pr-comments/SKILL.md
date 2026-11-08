---
name: leaving-pr-comments
description: 代表用户在 GitHub 提交 PR 或 Issue 评论时规范身份归属标识与格式；不授予直接发布权限。
---

# Leaving PR comments

为代表用户提交的 GitHub 评论标明代理身份。先遵循当前任务的写入授权，再处理评论格式。

## Attribution

确认运行环境公开的模型名，以及当前 GitHub CLI 认证对应的用户登录名。不要猜测身份；模型名不可用时写 harness 名，GitHub 身份不可验证时不要代填用户名。

评论使用以下结构：

```markdown
> [!NOTE]
> 🤖 **<verified model or harness> responding on behalf of <verified GitHub login>**

<comment>
```

归属说明放在 GitHub note 中，评论正文另起一段。不要在正文后追加签名、分隔线或第二份归属说明。用户明确要求原样发布的文字除外。PR 描述和提交信息不使用这个格式。

## Write and publish

- 先读 `engineering-writing`，再用 `unslop` 检查评论。每条评论聚焦一个问题，说明证据、影响和可执行的下一步；删除泛化表扬和进度播报。
- 发布前检查整条 Markdown，包括引用和附件，不得泄露密钥、私有信息或未公开的安全细节。先预览排版。
- 本技能只规范评论内容。是否发布、回复或解决 review thread，仍由当前 lora-mode 流程和本次用户授权决定。
- 发布后确认 GitHub 返回了评论或 review 的 URL。只有回复成功后才解决对应 review thread。
