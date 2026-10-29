---
name: engineering-writing
description: Write or edit pull request and issue text, technical documents, code review comments, and engineering replies. Use for concise, evidence-based engineering communication.
---

# Engineering writing

Use this skill when you write or revise PRs, Issues, technical documents, code comments, or engineering review comments. Use `unslop` after drafting to remove AI writing patterns.

Before drafting, identify the reader, the decision or action they need, the verified facts, and the unknowns. Lead with the problem or conclusion. Never turn an assumption into evidence.

## Pull requests

- Follow the repository's title convention. State the problem or user value, not a file inventory.
- Keep the opening to one or two sentences. Explain the problem and the change.
- State the risk tier from the diff and give its reason.
- If no diff is available, mark risk and reversibility unassessed; do not infer a tier from module names or topic alone.
- When a PR or Issue workflow requires a change map, embed it once as a Mermaid block in the body. State its Base, Head, and coverage limits.
- Show verification as the command and observed result. Include a before/after when behavior changed.
- State whether the change is easy to reverse and name its affected modules or users.
- If a required fact or artifact is missing, label the draft incomplete and name what is needed. Do not make a blocked draft look ready to submit.
- Omit empty sections and details that the diagram or diff already makes clear.

## Issues

- Describe the current behavior and the requested outcome.
- For bugs, include reproduction steps and observed results when known. Mark missing facts as unknown.
- If the reporter did not state the expected behavior, mark it as unknown and ask a specific question before writing acceptance criteria.
- Give acceptance conditions that a person or agent can verify.
- Include scope limits and external constraints when they affect implementation.
- Keep reporter evidence separate from codebase evidence and hypotheses.

## Review comments and replies

- Put one concern in each comment. Lead with the finding or answer.
- Cite the relevant code, behavior, check, or reproduction.
- Explain the impact and name a concrete next action or question.
- Use the repository's severity terms. Distinguish verified defects from uncertain concerns.
- Remove vague style preferences, generic praise, and status narration.
- Follow the active workflow's authorization rules before posting or resolving a comment.

## Technical documents and code comments

- Write for a named reader and a concrete task or decision.
- Record the reason, contract, constraints, and verification method when they help a future reader.
- Use headings for separate topics, numbered steps for procedures, and bullets for unordered items.
- Use code comments to explain intent or invariants that the code does not show. Do not restate obvious operations.
- Keep terms consistent. Preserve exact API, product, and domain names.

## English technical writing check

ASD-STE100 is a controlled-English standard with writing rules and an approved dictionary. Apply these six STE-inspired checks to English technical documents, PR and Issue text, and engineering comments:

For the current official issue and scope, see the [ASD-STE100 FAQ](https://www.asd-ste100.org/STE_faq.html).

1. Use short, complete sentences. Split a sentence when it carries several facts or steps.
2. Keep one fact or action in each sentence. Use a list for a sequence.
3. Use active voice when the actor is known. Write procedures as direct instructions.
4. Use one clear term for each concept. Use simple words when they preserve the meaning.
5. Keep noun groups clear. Do not remove articles to make a sentence shorter.
6. Name the subject when `this`, `that`, or `it` could refer to more than one thing.

Use at least five of the six checks as the internal 80% target for English technical prose. Fix factual errors, missing evidence, ambiguous references or acceptance conditions, and unsafe instructions regardless of the count. This measures only this checklist, not ASD-STE100 compliance. A full compliance check requires the current official rules, dictionary, and a qualified review. Do not score Chinese text against the English standard.
