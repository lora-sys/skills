# Codex 安装提示词

将以下内容粘贴到 Codex：

```text
请通过 Skills CLI 将 lora-sys/skills 中的全部技能全局安装到 Codex。

执行：
npx skills add lora-sys/skills --skill '*' --agent codex --global --yes

完成后执行：
npx skills list --global --agent codex

请列出已安装的技能名称；若某一步失败，请保留错误输出并说明需要的权限或依赖。不要修改其他项目文件。
```

如果只需要一个技能，请替换 `--skill '*'`：

```text
请全局安装 lora-sys/skills 中的 static-site-experience-release 到 Codex。

执行：
npx skills add lora-sys/skills --skill static-site-experience-release --agent codex --global --yes

完成后执行：
npx skills list --global --agent codex
```
