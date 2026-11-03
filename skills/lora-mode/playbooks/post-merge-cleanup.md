# post-merge-cleanup — 合并后的仓库与本地清理

> **适用**：PR 合并后的任务收尾，或用户要求清理仓库/本地工作痕迹。**主导工具**：`git`、`gh`、`git worktree`。

清理是「定义完成」的一部分，不是可选抛光。分三层：每个实现步骤后清本地残留，任务完成后做一遍，仓库级定期跑一次。清理不得掩盖真实失败，也不得删掉还有用的信号。

## 步骤

1. **确认合并状态。** `gh pr view <n> --json state,mergeCommit,headRefOid` 确认 PR 已 MERGED，并核对本地默认分支已快进到 merge commit。未合并的 PR 不做合并后清理；不能把本地 `git status` 干净当作远端已合并的凭证。
2. **删已合并分支。** 远端：`git push -d origin <branch>`；本地：`git branch --merged origin/main` 列出后用 `git branch -d <branch>` 删。`-d` 拒绝删未合并分支，这是要保留的安全栏；确认要丢弃实验时才用 `-D`。仓库可在 Settings → General → Pull Requests 打开 *Automatically delete head branches*，让远端删除不再依赖人工记得。
3. **清 worktree。** `git worktree list` 找出本任务建的 linked worktree，先 `git worktree remove <path>`（同时删目录和 git 台账，但不删分支，所以第 2 步仍要做）。若目录已被 `rm -rf` 删过，用 `git worktree prune` 清残留记录；先 `git worktree prune --dry-run -v` 预览。`remove` 拒绝删有未跟踪/已修改文件的 worktree，除非 `--force`；主 worktree 不能 remove。
4. **处置 Issue。** 合并 PR 时用 `Closes #n` / `Fixes #n` / `Resolves #n` 关键字让 GitHub 自动关闭（Settings → General → Issues 的 *Auto-close issues with merged linked pull requests* 默认开启）。对本任务遗留的未关闭 Issue 逐条判断：已完成就关，仍有后续就写明剩余工作再交回队列。长期不动的 Issue/PR 靠 stale 策略兜底（如 `actions/stale`：静默 N 天打标签，再 M 天关闭，有活动就重置计时），不要手工凭记忆猜哪些过期。关闭 Issue 与删除数据各自需要授权，不因「顺手」而做。
5. **更新文档。** 按实际改动核对 README、CHANGELOG、API/架构文档、用户指南和配置示例；功能或安装方式变了就必须改，只改受影响的段落并链接对应 Issue/PR。版本号、徽章、发布 tag 仅在用户要求或正式发布时动。
6. **清产物与缓存。** 删本任务产生的临时目录、日志、验证副本和 scratch 文件；逐项标为已清理、为审查保留（写位置与用途）或未确认，不能只报一句「已清理」。生成物不进库：`__pycache__/`、`*.pyc`、`*.py[cod]`、构建输出写进 `.gitignore`；已误提交的用 `git rm -r --cached <path>` 移出索引再补 `.gitignore`。只在仓库内清忽略文件用 `git clean -d -f -X`，`-x` 会连未忽略的未跟踪文件一起删，执行前先确认没有要留的东西。
7. **校验。** `git status --short` 无未跟踪/已修改残留、`git worktree list` 无 prunable 条目、`gh pr list --state open` 里没有本任务已合并的 PR、`git diff --check` 干净。清理后重跑一次受影响检查，确认清理没有顺手改坏行为或掩盖失败。

## 仓库级定期卫生

周期性（不是每次任务）跑：列出已合并但未删的分支、prunable worktree、超过静默期的 Issue/PR、仓库内被跟踪的生成物、以及失效的文档链接。清理改动走普通 PR，不改行为；一次只做一类，便于回滚。

## 不得

- 不删未合并分支凑「干净」；不确定就用 `-d` 让它拒绝。
- 不在有未跟踪工作成果的仓库里跑 `git clean -x`。
- 不重写已发布历史，不推默认分支，不用 `--admin` 绕过保护。
- 不把清理当时髦：删掉测试、断言、日志或验证工件来让状态变干净。
- 未获授权不关 Issue、不删数据、不打发布 tag。
