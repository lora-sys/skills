# Specialized routes

Load this matrix when a task is specialized, spans workflows, or does not match the common routes in `SKILL.md`.

| Task | Route |
|---|---|
| UI direction, visual refinement, throwaway prototype | `ui-design`, `visual-refinement`, `prototype` |
| Iterative quality optimization against a target or score | `goal-eval` |
| Browser, desktop, document, or spreadsheet work | Read `references/platform-capabilities.md`, then load only the matching available skill/tool |
| Concurrency, retries, protocols, or state transitions with an invariant ordinary tests cannot cover | `references/formal-verification.md`; use formal verification selectively, not for routine PR/Issue maps |
| Remote installs, tests, or service checks | `remote-dev` if installed; pure checks go direct, code changes stay local then hand off |
| Teaching HTML, publishing, static-site release | `teaching-page`, `publish`, `static-site-release` |
| Deck, video, skill authoring | `deck`, `video`, `skill-authoring` |
| Resume, image generation, GitHub solution search, Notion | Direct skill: `chinese-ai-resume`, `lora-visual` / `generate-image`, `github-gem-seeker`, `notion` |
| Resume an interrupted task; unattended long task; skill reflection | `session-pickup`, `autonomous-run`, `reflect` |

## Direct dispatch

A single deliverable in ≤2 files with no shared-structure change goes directly to its skill: teaching page → `interactive-teaching-page`; standalone HTML publication → `html-communication`; one deck → `presentation-builder`; one video plan → `short-video-director`; resume → `chinese-ai-resume`; image → `lora-visual` or `generate-image`. Use a playbook when work spans files, shared structure, debugging, or downstream handoffs. Use `goal-eval` only when the user asks to improve an outcome against a target; bugs and spec-only changes keep their normal routes.

Notion work goes to `notion`; open-source solution search goes to `github-gem-seeker`. For a mixed request, route by the final deliverable and follow explicit playbook handoffs. Keep the active route across same-task messages. If no route fits, choose the nearest playbook and state the assumption. Read `references/platform-capabilities.md` only for browser, desktop, or office-file tasks; skip it for ordinary repository work.

Use only skills and tools available in the target agent environment. Do not assume a platform-specific tool exists because another runtime uses it.
