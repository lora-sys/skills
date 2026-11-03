# Verification property routing

Use this reference only after the task, source, or diff shows a concrete property at risk, or a change touches code covered by an existing verification skill. Screen before implementation and again against the final diff. A domain name such as RSI, game, backend, or agent is not evidence by itself.

## Identify the property

Read the relevant implementation and its callers, state/data model, existing checks, and the requested behavior. State the promise in one sentence, identify the code that implements it, and name the user harm if it breaks. Examples include “at most one worker owns a training slot,” “a retry cannot charge twice,” “assets remain conserved after a trade,” or “one tenant cannot read another tenant's records.” Do not invent hidden guarantees. If no meaningful property beyond local behavior is exposed, run the ordinary checks for the changed path and stop the verification route there.

Repeat the screen after editing: confirm which properties the diff can affect, whether it changes a model's assumptions, and whether existing verification covers the changed source. This catches newly exposed risks without expanding unrelated work.

## Choose the least costly adequate method

| Property evidenced in source or diff | Start with | Escalate when |
|---|---|---|
| Concurrent scheduling, retries, protocol order, or a transaction race | Deterministic concurrency/integration test that controls the relevant interleaving | Use bounded model checking when important interleavings are numerous and the state/actions can faithfully map to code; do not substitute a hand-written state diagram for a checker. |
| State or data invariant across many actions (ownership, conservation, no duplicate active record) | State-machine or property-based test that checks the invariant after every transition in generated action sequences, including rejected/retried/cancelled actions | Model-check when correctness depends on concurrent order or exhaustive transition combinations that the tests cannot reasonably cover. |
| Idempotency or duplicate delivery | Replay, retry, and property-based tests against the real operation and persisted result | Model distributed delivery/order only when retries and concurrent actors create the uncovered risk. |
| Cross-service or database consistency | Contract and integration tests using the system's stated consistency boundary | Simulate multiple nodes or model the protocol when the guarantee spans asynchronous events and the concrete race is otherwise hard to reach. |
| Resource limits, leaks, or throughput | Bounded load, soak, memory, or timing measurement with a stated budget | Use static analysis or formal reasoning only when a specific resource invariant and an appropriate tool apply. |
| Authorization or tenant isolation | Positive and negative tests for each changed role, object, and boundary | Add model/formal checks only for a concrete policy state machine whose transitions are difficult to cover with tests. |
| Untrusted parser/input handling | Boundary/property tests and a bounded fuzz target using existing project tooling | Formal methods only when the relevant language/tool can verify the actual implementation or a justified model. |
| Numerical/model/training optimization | Controlled experiment against a baseline, with fixed seeds and held-out or validation metrics | Use statistical/model evaluation for quality claims; do not formally prove which hyperparameter is best. |
| Pure visual, animation, or copy change | Existing visual/runtime smoke or targeted snapshot check where available; assert a sample where the changed result differs (for curves, a non-midpoint sample as well as endpoints) | Do not add formal verification unless the diff also changes a real state, safety, or protocol property. |
| Ordinary docs, formatting, or isolated logic with no identified invariant | Existing lint/test or a focused example | Do not create a verification skill or add a verification framework. |

Choose the cheapest method that can falsify the stated property. Before reporting success, confirm the check exercises the changed behavior and would distinguish the intended result from the previous behavior. Methods can be combined when each covers a distinct gap (for example, a state model plus a real implementation regression test). Keep runs bounded and use existing dependencies and tooling. Never install a verifier or package without authorization. A missing tool blocks that method; report it and retain the property as unverified rather than claiming a pass or replacing model checking with a decorative diagram.

### Formal escalation for lifecycle races

Use model checking alongside implementation tests when all of these are visible in source: (1) the property protects a safety outcome such as bounded capacity, unique ownership, or at-most-once completion; (2) two or more concurrent/asynchronous transitions can interact, such as claim/lease, expiry, retry/recovery, reassignment, and completion; and (3) a deterministic test can show one failure but cannot cover the lifecycle combinations. First confirm that a finite model can map to actual source steps. If no project verification covers these paths, create one through `create-formal-verification-skill`; if coverage already exists, maintain it. Passing regression or stress tests supplement this route; they do not replace it once these conditions are met. Keep the concrete regression tests too. An isolated race with one atomic critical section and a complete deterministic regression can stay on the ordinary test route.

## Create, reuse, and maintain

- If the diff touches source listed in an existing project-local verification skill, read and follow `../../maintain-formal-verification-skill/SKILL.md` even for a behavior-preserving refactor. Run the existing check, confirm model/source mapping, and update its coverage record and sync commit only after the new code passes. Do not create a duplicate or rerun unrelated models.
- If the property meets the formal threshold above and no relevant project-local verification exists, read `../../create-formal-verification-skill/SKILL.md` and create the smallest reusable project skill/model before stopping. Map each model action to real source steps and validate it on a disposable broken variant when tools are available. Tool availability controls the result, not whether a qualifying model is created: when a verifier is unavailable, mark the project verification `draft / blocked`, record the exact missing tool and run command, preserve the ordinary regression checks, and leave its sync commit unset. Do not install dependencies or label an unrun model verified.
- If formal verification is not warranted, use the selected test, fuzz, simulation, runtime, or evaluation path directly. The absence of a formal skill is not a reason to create one.

## Evidence record

For each selected property, report:

```text
Property and user harm:
Covered source paths/functions:
Method and tool/version:
Command and observed result:
Assumptions/bounds:
Uncovered behavior or blocker:
```

Keep each claim scoped to the code, model, input domain, seeds, environment, and run actually observed. A model-checker pass is evidence about its stated model and bounds; it is not a blanket proof of the implementation. A failed, skipped, unavailable, or unrun check is never “passed.”
