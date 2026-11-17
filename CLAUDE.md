@AGENTS.md

# Claude Code notes

本项目所有协作规则以 `AGENTS.md` 为准，包括技能安装判定、漂移检测和 CLI 覆盖后的复核要求。

新增或更新技能时，Claude Code 必须确认 `~/.claude/skills/<skill-name>` 入口存在，并在当前会话技能列表中可见。只同步 `~/.agents/skills/<skill-name>/` 不算安装完成。
