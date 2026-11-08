---
name: maintain-formal-verification-skill
description: Update and maintain a project's existing formal verification models and source mappings when code changes touch covered behavior, without weakening verified properties.
---

# Maintain formal verification

Use this skill whenever a code change touches source listed in an existing project-local verification skill or model, including behavior-preserving refactors. It maintains that verification; it does not create duplicate models or authorize changing product behavior.

## Workflow

1. Read the project verification skill, its coverage/sync record, the changed source and relevant callers, and the existing model/check command. Confirm the changed symbols are actually covered.
2. Compare the behavioral contract and model assumptions before and after the change. If changed code is outside the recorded coverage, report that fact and use the ordinary verification route; do not expand the model by association alone.
3. Run the existing check using the project's documented command and installed tools. Also run affected implementation tests when the model alone cannot exercise real code. Do not install or upgrade dependencies.
4. If behavior is intended to remain the same, keep the property unchanged. Update source paths, symbols, or model steps only when the refactor makes the old mapping inaccurate, then rerun the verification and relevant implementation tests.
5. If behavior changes the property, preserve the prior invariant as the default. Do not weaken or replace it to make the model pass. Treat a requested contract change as a separate acceptance decision; report the failing counterexample and the exact property at issue.
6. If a run fails, replay the counterexample against implementation where possible and distinguish a real defect, model mismatch, and unavailable tool. If a required verifier is missing, leave the sync record unchanged and report the blocker. Never call a skipped or unrun check a pass.
7. If the covered code is committed and the model/checks pass with a reviewed source mapping, advance the sync commit to that commit. If covered changes are still uncommitted, leave the last committed sync commit unchanged and append a concise latest-verification record to the project verification skill: dirty paths, confirmed source-to-model mapping, commands, results, and limits. Never point a sync commit at a HEAD that does not contain the checked code. After the code is committed, rerun or confirm the checks against that commit before advancing the record.

## Evidence to return

```text
Property and harm:
Changed covered source:
Model/check reused or updated:
Command and observed result:
Source-to-model mapping confirmed at commit:
Assumptions, bounds, and uncovered behavior:
Working-tree state and last committed sync commit:
```

A model-checking pass covers only its model, assumptions, and explored bounds. Keep that limit visible in the result.
