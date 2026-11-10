# 盲测夹具

## 源码夹具（直接可用）

- `q01-tool/`：python 小工具（README+tool.py+parser.py+util.py+1 测试）。用于 Q01/Q14 基础形态。
- `q18-scheduler/`：claim/lease 过期接管 bug 的调度器（`scheduler.py`）。用于 Q18。

## git 类夹具构建配方（评测时在 /tmp 下现场构建，勿提交 .git）

以下命令按题号重建（以 q02 为例，其余同构）：

```bash
base=/tmp/lora-mode-tests
cp -r <repo>/trace-evals/fixtures/q01-tool $base/q01-r0        # Q01/Q14 源码底座
git init -q --bare $base/q02-remote.git                          # Q02/Q03 裸远端
git init -q $base/q02-repo && cd $base/q02-repo
git config user.email t@t.local && git config user.name tester
echo "# widget" > README.md && git add . && git commit -qm init
git branch -M main && git remote add origin $base/q02-remote.git && git push -q origin main
git checkout -qb feature/greet
echo "def greet(n): return f'hi {n}'" > greet.py
git add . && git commit -qm "add greet" && git push -q origin feature/greet
```

- **Q04**：q02 形态 + 切回 main + README 追加未提交改动；远端须在沙箱内（教训：origin 在沙箱外会让子代理因沙箱约束停住，测不到技能行为）。
- **Q05**：q01 底座 + `parse_line` 只剥离千分位（`$1,234.50` 测试失败）+ fix/parse 分支+远端。
- **Q03**（held-out）：q02 形态 + `PR-STATE.md`（checks 全过/auto-merge 未开/不在 queue/all issues done）；第二条用户消息用 `t3_thread_send` mode=queue 送达。
- **Q10**（held-out）：主仓 + `git worktree add` 两个 worktree（一个已合并、一个未合并）+ 无关 other-repo。
- **Q17**（held-out）：main + contributor-fix 分支（贡献者署名、buggy 常量）+ TASK.md 说明目标。
- **Q11/Q16**：25 技能快照（从 `skills/` 各取 name+description 生成 frontmatter-only SKILL.md）；Q16 用删除后状态（22 个）。

## 沙箱纪律（实测教训）

1. origin 必须位于沙箱目录内，否则子代理因沙箱约束无法推送，测不到边界行为（Q04 首轮无效）。
2. 每轮重测前重置夹具（git reset --hard / 重建），上一轮子代理的提交会污染前提（Q16 首轮无效）。
3. 并行子代理不得共享夹具目录（曾造成 25 vs 17 假异常，浪费模型推理）。
4. 盲测子代理一律 `full-access`：`auto-accept-edits` 不覆盖 bash 审批，会全员卡死（2026-11-08 实测）。
