# Specialized routes

Load this matrix when a task is specialized, spans workflows, or does not match the common routes in `SKILL.md`.

| Task | Route |
|---|---|
| UI direction, visual refinement, throwaway prototype | `ui-design`, `visual-refinement`, `prototype` |
| Iterative quality optimization against a target or score | `goal-eval` |
| Testing a skill behavior change | `eval` |
| Explicitly checking what a diff could break outside its changed lines | `references/blast-radius.md` |
| Code feature, bug fix, or refactor with a source-backed concurrency, idempotency, invariant, consistency, resource, or authorization risk | Run the light property screen, then `references/verification-routing.md`; reuse a covering project check before creating one |
| Concurrent RSI training schedule with source-backed claim/lease, expiry, retry/reassignment, and completion transitions | When event order can violate capacity/ownership and tests only force selected schedules, create or maintain a finite model check alongside implementation regressions |
| Training quality, learning-rate, or model-parameter optimization | Controlled experiment/model evaluation with baseline, seeds, and held-out metric; no formal proof of a quality optimum |
| Multiplayer trades, inventory, balances, reservations, or ownership transitions | State-machine/property checks for conservation, uniqueness, and valid transitions; add concurrency/model checks only when the source exposes that risk |
| Pure game animation, asset, copy, documentation, or isolated presentation change | Existing visual/runtime/content checks; no formal route without a changed state or safety property |
| Refactor touching source covered by a project-local verification skill | `maintain-formal-verification-skill` |
| Browser, desktop, document, or spreadsheet work | Read `references/platform-capabilities.md`, then load only the matching available skill/tool |
| Concurrency, retries, protocols, or state transitions with an invariant ordinary tests cannot cover | `references/formal-verification.md`; use formal verification selectively, not for routine PR/Issue maps |
| Remote installs, tests, or service checks | `remote-dev` if installed; pure checks go direct, code changes stay local then hand off |
| Refresh or assess an older PR | `modernize`; use `takeover` when the request is to take responsibility for inherited work |
| Explicit multi-provider review | `council`; ordinary review stays on `code-review` or `review-loop` |
| Teaching HTML, publishing, static-site release | `teaching-page`, `publish`, `static-site-release` |
| Skill authoring | `skill-authoring` |
| Image generation, GitHub solution search | Direct skill: `lora-visual` / `generate-image`, `github-gem-seeker` |
| Resume an interrupted task; unattended long task; skill reflection | `session-pickup`, `autonomous-run`, `reflect` |
| Merged PR, or a request to clean repository and local work traces | `post-merge-cleanup` |

## Direct dispatch

A single deliverable in ≤2 files with no shared-structure change goes directly to its skill: teaching page → `interactive-teaching-page`; standalone HTML publication → `html-communication`; image → `lora-visual` or `generate-image`. Use a playbook when work spans files, shared structure, debugging, or downstream handoffs. Use `goal-eval` only when the user asks to improve an outcome against a target; bugs and spec-only changes keep their normal routes.

Open-source solution search goes to `github-gem-seeker`. For a mixed request, route by the final deliverable and follow explicit playbook handoffs. Keep the active route across same-task messages. If no route fits, choose the nearest playbook and state the assumption. Read `references/platform-capabilities.md` only for browser, desktop, or office-file tasks; skip it for ordinary repository work.

Use only skills and tools available in the target agent environment. Do not assume a platform-specific tool exists because another runtime uses it.
