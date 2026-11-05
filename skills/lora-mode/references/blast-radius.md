# Blast radius review

Use this when the user asks what a change could break outside the diff, or asks for evidence that a suspicious change is safe. Do not run it for every code change or PR.

1. Read the diff and identify the behavior that changed, including implicit behavior not obvious from the changed lines.
2. Trace affected callers and boundaries. Follow runtime order, serialized data, external library behavior, flags, and downstream consumers only where the diff gives a reason to inspect them.
3. State the one or two facts the safety conclusion depends on. A list of callers or hypothetical risks is not a conclusion.
4. Verify those facts with the strongest cheap evidence available: source and pinned dependency code, a concrete failure path that cannot occur, a focused script or existing test that runs real code, or the running application. Do not add tests unless the user asks; an ad hoc script or existing checks may be enough.
5. Report confirmed risks separately from risks checked and cleared. Cite file and line evidence, say where each claim stopped, and state what remains unknown. Do not call the whole change safe because one assumption passed.

This adapts [pstack blast-radius](https://github.com/backnotprop/pstack/blob/main/skills/blast-radius/SKILL.md) to lora-mode's scope and verification rules. PR Change maps remain governed by `change-impact.md`.
