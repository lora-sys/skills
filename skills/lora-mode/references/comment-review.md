# Comment review

Use this review on every code diff, or when explicitly triggered by requests for comment cleanup (triggers: `注释清理`, `清理注释`, `no-comment`, `comment-review`). If comment cleanup is requested, cover the affected files. Do not expand the scope to unrelated files.

## Review

1. Read each added, changed, or deleted comment with its surrounding code, callers, tests, and any contract it describes.
2. Delete comments that restate the code, describe behavior that no longer exists, or preserve a workaround whose root cause can be fixed in scope.
3. Keep comments that explain non-obvious intent, an invariant, or an external contract the code cannot express. Verify claims against the source that owns the rule. If that source is unavailable, keep the comment and report it for review.
4. Audit lint, type-check, and test suppressions in scope. Narrow or remove unnecessary suppressions. Treat suppressions that hide correctness or safety failures as actionable defects.
5. For a comment that claims a code constraint, check whether a type, test, lint rule, or CI check can enforce it. Encode the constraint when the task authorizes that change; otherwise keep the comment and report the gap.
6. If a comment exposes a code defect, fix the smallest root cause in scope. Do not delete the comment and leave the behavior it describes broken.

Report the scope, comments removed, comments kept with reasons, unresolved external claims, suppressions checked, fixes made, and any unverified constraints.

This workflow adapts the review in [backnotprop/pstack `no-comments`](https://github.com/backnotprop/pstack/blob/main/skills/no-comments/SKILL.md) to lora-mode's scope and authorization rules. Run it as a separate pass after reviewing the code diff. Use an independent reviewer only when the active task workflow authorizes one.
