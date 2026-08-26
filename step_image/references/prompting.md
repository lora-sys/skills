# Prompting best practices

These principles apply to both generation and editing workflows.

## Structure
Use a consistent order: scene/backdrop -> subject -> key details -> constraints -> output intent.

## Specificity
- If the prompt is already specific and detailed, normalize it into a clean spec without adding creative requirements.
- If the prompt is generic, add tasteful detail when it materially improves the output.

## Constraints and invariants
- State what must not change (`keep background unchanged`).
- For edits, say `change only X; keep Y unchanged` and repeat invariants on every iteration.

## Text in images
- Put literal text in quotes or ALL CAPS and specify typography.
- Spell uncommon words letter-by-letter if accuracy matters.
- Require verbatim rendering and no extra characters.

## Input images and references
- Do not assume every provided image is an edit target.
- Label each image by index and role (`Image 1: edit target`, `Image 2: style reference`).
- If the user provides images for style, composition, or mood guidance and does not ask to modify them, treat the request as generation with references.

## Iterate deliberately
- Start with a clean base prompt, then make small single-change edits.
- Re-specify critical constraints when you iterate.
- Prefer one targeted follow-up at a time over rewriting the whole prompt.
