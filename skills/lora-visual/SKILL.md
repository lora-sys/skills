---
name: lora-visual
description: "Create a consistent lora-style visual system in two modes: finished explanatory images with short accurate labels generated directly inside the scene, and transparent character illustrations produced with a bundled background-removal script. Use for concepts, mechanisms, comparisons, workflows, tradeoffs, hero artwork, editorial character scenes, and reusable layout illustrations featuring lora and Mochi."
---

# Lora Visual

Create raster visuals in one shared cute Japanese-anime editorial language. Choose one output mode before generating; do not mix the two production paths.

Use `assets/lora-character-reference-v1.jpg` as the canonical character reference whenever the image tool supports references.

## Choose the output mode

### Mode A — explanatory image

Use when the image must explain a concept, mechanism, workflow, comparison, or tradeoff by itself.

- Deliver a complete PNG or WebP with a finished off-white scene.
- Generate every essential title and label directly inside the bitmap.
- Make the relation visible through objects, paths, states, or repeated materials; labels identify the evidence but do not replace it.
- Do not generate an unlabeled base and add essential words in a separate rendering step.

### Mode B — transparent illustration

Use when the character scene will be composed into a hero, document, card, slide, or other layout.

- Generate the subject on a perfectly uniform chroma-key background that does not occur in the artwork. Default to `#00FF00`; use `#FF00FF` when the subject contains green.
- Do not include explanatory labels unless the user explicitly requests text inside the illustration.
- Remove the background with the bundled `scripts/cutout.py` and deliver a transparent PNG.
- Keep the transparent artwork as a reusable visual asset; the surrounding layout supplies the title and explanatory copy.

If the destination is unclear, choose Mode A when the image itself must communicate the idea and Mode B when another layout will carry the explanation.

## Shared visual language

- Keep the recurring characters visually consistent with `assets/lora-character-reference-v1.jpg`.
- lora is a cute young-adult Japanese-anime heroine with dark brown-black hair in a loose high messy bun, soft face-framing strands, large warm dark-brown eyes, a small amber `lora` hair clip when visible, an oversized cream hoodie, loose dark cargo pants, and black-and-white sneakers.
- Mochi is a small fictional warm-cream fluffy companion dog with floppy ears, round dark eyes, a black nose, and a compact friendly silhouette.
- Keep characters secondary to the subject's evidence or action.
- Use black, off-white, cream, warm gray, brown, and amber as the base visual system. Amber is the main identity accent.
- Add at most one additional muted semantic color when the explanation truly needs it.
- Favor clean anime line work, restrained paper texture, notebook/editorial materiality, and a warm creator-world atmosphere.
- Avoid 3D, glossy gradients, photorealism, purple-blue AI gradients, neon cyberpunk, generic card grids, dashboards, decorative clutter, excessive pink, and watermarks.

## Mode A workflow — explanatory image

### 1. Write the visual brief

```text
viewer_question: what should be understood in 10 seconds?
concrete_claim: one-sentence conclusion
real_objects: visible objects, interfaces, documents, tools, or states
relation: comparison, transformation, causality, sequence, hierarchy, feedback, tradeoff, or pipeline
visual_evidence: what must remain understandable when labels are ignored?
scene: believable setting and 2–4 useful environmental cues
semantic_colors: what each accent color means
labels: exact short strings plus the evidence surface for each label
```

Show the input, action or relation, and result. Keep one dominant focal action and no more than three major visual regions. For multiple steps, use a simple left-to-right or top-to-bottom sequence.

### 2. Design the labels

- Prefer 2–6 labels. Use more only when the explanation truly needs them.
- Keep each label short and concrete: role, action, state, or outcome.
- Place every label on or immediately beside its evidence surface, such as a desk nameplate, task sheet, folder tab, machine, meter, lane, or result document.
- Use modern Chinese sans-serif typography, medium or bold, large enough to read at the intended display size.
- Do not turn body copy, commands, tables, or long paragraphs into image text. Use a deterministic layout method when dense or editable text is required.

Add this block to the generation prompt:

```text
Text (verbatim): Render these exact labels as part of the bitmap illustration:
"<label 1>", "<label 2>", "<label 3>".
Use each phrase exactly once. Do not translate, paraphrase, misspell, repeat,
or add any other text. Use modern sans-serif medium/bold typography, large
and readable. Place "<label 1>" on <evidence surface>; place "<label 2>" on
<evidence surface>; place "<label 3>" on <evidence surface>.
```

### 3. Build the prompt

Use this order:

1. State the concrete claim and shared task.
2. Describe the real setting and the lora/Mochi action.
3. Describe the evidence objects and their geometry: aligned, nested, connected, split, transformed, repeated, or converging.
4. Assign semantic colors.
5. Quote the exact labels and specify each placement.
6. Add the Mode A style anchor.
7. End with exclusions.

Mode A style anchor:

```text
Cute Japanese-anime editorial illustration with clean confident charcoal/black
line work and restrained warm paper texture. Use the canonical lora reference:
dark brown-black loose high messy bun, soft face-framing strands, large warm
dark-brown eyes, small amber "lora" hair clip when visible, oversized cream
hoodie, loose dark cargo pants, and black-and-white sneakers. Include Mochi,
a small warm-cream fluffy companion dog with floppy ears, when the composition
allows. Use an off-white lightly textured real environment, not a blank white
canvas. Typography is modern sans-serif, medium or bold, large and readable.
Color is restrained: black, off-white, cream, warm gray, brown, and amber,
plus at most one muted semantic accent color. Keep the scene cute, thoughtful,
clean, warm, and editorial. No 3D, no glossy gradients, no photorealism,
no purple-blue AI gradient, no neon cyberpunk, no generic card grid,
no dashboard, no decorative clutter, no excessive pink, no tiny text,
no long paragraphs, no watermark.
```

### 4. Inspect and retry

1. Inspect the output at original resolution.
2. Compare every label with the brief character by character. Confirm that each appears exactly once and that no stray text was added.
3. Reject missing, duplicated, invented, or misspelled labels.
4. Regenerate with one targeted correction while repeating all scene and style invariants. Do not conceal an error with a separate text layer.

Use this retry instruction:

```text
Keep the scene, composition, characters, objects, colors, and all correct labels unchanged.
Change only the incorrect text "<wrong>" to the exact text "<right>".
Do not add, remove, translate, or repeat any other text.
```

## Mode B workflow — transparent illustration

### 1. Describe one reusable scene

Use one character action and only the objects needed to establish it. Examples: thinking with a notebook, writing, pointing, using a laptop, sitting with Mochi, or celebrating a finished result. Leave generous padding around the subject so the cutout can be composed safely.

### 2. Build the prompt

Describe the subject first, then append this fixed anchor:

Replace `<KEY_COLOR>` with the selected hex color before sending the prompt.

```text
Style: cute Japanese-anime editorial character illustration. Clean confident
charcoal/black line work with controlled detail, not photorealistic and not 3D.
Use the canonical lora reference: dark brown-black loose high messy bun, soft
face-framing strands, large warm dark-brown eyes, small amber "lora" hair clip
when visible, oversized cream hoodie, loose dark cargo pants, and black-and-white
sneakers. Include Mochi only when requested or when the asset is a lora + Mochi
pair: a small warm-cream fluffy dog with floppy ears, round dark eyes, and a
compact friendly silhouette. Color is restrained: black, off-white, cream,
warm gray, brown, and amber.

The background must be a perfectly uniform flat <KEY_COLOR> rectangle with zero
gradient, texture, noise, speckles, shadows, floor plane, or lighting variation.
Do not let line work, props, hair, shoes, dog ears, tail, or the subject touch
the image border. Keep generous padding. No text, no watermark. PNG format.
```

### 3. Validate the source

- Inspect the image before removal.
- Confirm all four corners are uniform and visually match the chosen key color.
- Reject backgrounds with gradients, texture, shadows, speckles, or artwork touching the border.
- Preserve the source image alongside the transparent result until the output is approved.

### 4. Remove the background

Install Pillow if the active Python environment does not have it, then run:

```bash
python3 scripts/cutout.py source.png transparent.png
```

Optional tuning:

```bash
python3 scripts/cutout.py source.png transparent.png \
  --transparent-threshold 12 \
  --opaque-threshold 220
```

The script samples the image border, builds a soft alpha matte from color distance, and removes color spill from antialiased edges. It works with any uniform key color, so the key can be chosen to avoid the subject palette.

### 5. Validate the transparent result

- Confirm the output is RGBA and all four corners have alpha `0`.
- Confirm the subject remains complete, including loose hair strands, hoodie strings, shoes, the `lora` hair clip, Mochi's ears and tail, and small props.
- Check for a gray, green, or magenta fringe at 100% zoom.
- Confirm internal cream / white areas were not erased.
- Regenerate the source instead of forcing the algorithm when the background is visibly uneven.

## Regression references

Read [evals/EVALS.md](evals/EVALS.md) only when testing or updating this skill. The images under `assets/golden/` are regression references, not content to insert into ordinary outputs. See [manifest.json](manifest.json) for the frozen v1 asset hashes and upstream provenance.

## Output handling

- Save approved project assets inside the current project or output directory.
- Do not leave project-referenced images only in the generator's default storage.
- Use versioned filenames instead of overwriting an approved asset unless the user explicitly requests replacement.
- Report the final prompt, output mode, source image path when Mode B is used, final image path, and any non-default cutout options.

## Quality gate

For every output:

- The subject is recognizable in about 3 seconds.
- The main action or relation is clear in about 10 seconds.
- Characters support the subject instead of becoming generic decoration.
- lora, Mochi, the black/cream/amber palette, and the warm editorial feel remain consistent.

For Mode A:

- One claim, one focal action, and no more than three major visual regions.
- The visual evidence still shows the relation when labels are ignored.
- Every required label is exact, appears once, and is integrated into the correct evidence surface.
- All labels remain readable at the intended display size.

For Mode B:

- Background removal is clean and the output has real transparency.
- Thin details and internal cream/white regions remain intact.
- No source background, fringe, shadow, or border artifact remains.
