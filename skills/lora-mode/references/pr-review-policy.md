# PR risk and review policy

Read this from `pr-open.md`, `pr-review.md`, `pr-babysit.md`, and `takeover.md`. Classify risk from the changed behavior, affected modules, consumers, and reversibility. Do not lower a tier because the author is trusted. If evidence is incomplete, use the higher tier.

| Tier | Typical changes | Review depth |
|---|---|---|
| Low | Documentation, copy, isolated tests, or additive behavior behind a disabled flag | Focused checks and the normal independent Spec / Standards review |
| Medium | Ordinary behavior, API, component, or cross-module changes | Focused unit and consumer-path checks, plus the normal independent review |
| High | Authentication, access control, secrets, billing, private data, destructive migrations, concurrency, CI/CD, release, deployment, installers, or shared invariants with broad impact | Focused integration, security, and recovery checks; add one independent risk-focused review when available; require the repository's human approval. If high risk has no verifiable human approval gate, stop before merge and ask for one |

A test-only change that weakens a gate is High risk. Add `Risk: <tier> — <reason>` to the PR description. An agent's review does not count as a required human approval. `full-send` does not bypass branch protection or the High-risk human gate.

## Findings and convergence

- Report a finding only when the diff introduces or worsens a concrete failure. Cite the changed file and line, a realistic trigger, the effect, and a repair.
- Filter style preferences, unsupported guesses, duplicate reports, and findings that tooling already enforces. Label a confirmed pre-existing defect as pre-existing; do not attribute it to this change.
- Keep uncertainty explicit. Do not request changes for an unverified suspicion.
- Use the shared round budget in `pr-open.md`. After three rounds without convergence, reconsider the design. Later rounds inspect changed hunks and unresolved findings only; do not repost a finding without new evidence.

## Learning from outcomes

For PR work, append a compact outcome to the existing local `USAGE.md` row: risk tier, rounds-to-pass, finding disposition (fixed, disproved, intentional, deferred, or pre-existing), available human-review effort (approvals, substantive comments, and time waiting on a person), and any confirmed post-merge incident or revert. Keep private details local. Do not count an unresolved or merely unaddressed suggestion as a false positive.

- Add a sanitized eval case when evidence confirms a missed bug, incident, or revert.
- Add a clean-case eval when evidence confirms a review finding was false or pre-existing and the pattern could recur.
- When review rules, prompts, tools, or models change, rerun the PR-review eval subset. Compare confirmed bug detection, clean-case noise, and rounds-to-pass. To assess human effort, compare approvals, substantive human comments, and time waiting on a person across comparable risk tiers; these are proxies unless review time is measured directly. Track confirmed reverts and incidents per merged PR as quality guardrails. Report rates only when numerators and denominators are known and comparable; otherwise report counts or mark them unknown. Do not claim time saved from fewer review rounds alone.
- Do not invent incidents or seed the eval set with unverified findings.

This adapts the risk-based gates and incident-driven eval loop described in [Anthropic's code review process](https://claude.dev/blog/solving-code-review-at-anthropic/) and the handoff principles in [t3dotgg/tstack takeover](https://github.com/t3dotgg/tstack/blob/main/skills/takeover/SKILL.md) to lora-mode's authorization boundaries.
