---
name: step_image
description: Generate or edit images with StepFun's step-image-edit-2 model. Use for text-to-image, image editing, style transfer, background replacement, object removal, compositing, or project visual assets. Calls StepFun API at https://api.stepfun.com/step_plan/v1. Requires STEP_API_KEY. Do not use for SVG/vector/code-native assets.
---

# Step Image

Generate and edit images using StepFun's step-image-edit-2 model.

## When to use
- Create an image from a text prompt
- Edit an existing image with a text instruction
- Generate or revise visual assets for a project
- Apply style transfer, background replacement, or object changes

## When not to use
- SVG/vector icons, logos, or illustrations that belong in code
- Simple shapes, diagrams, or wireframes better built in SVG/HTML/CSS
- Tasks where the user clearly wants deterministic code-native output

## Workflow
1. Collect the prompt, exact text, input images, and constraints from the user.
2. Label each input image by role: edit target, style reference, supporting insert.
3. If the edit target is a local file, inspect it before editing.
4. Run `scripts/image_gen.py` with the right command and arguments.
5. Check the output for subject, style, text accuracy, and invariants.
6. Iterate with one targeted change if the result needs adjustment.

## Prompt rules
Write prompts with enough detail for image models:
- Subject and scene
- Composition and camera or layout
- Style, mood, lighting, and color palette
- Text that must appear in the image, quoted exactly
- Constraints such as "keep the same character", "preserve the logo", or "do not change the background"

For edits, state what changes and what stays unchanged. Repeat invariants on every iteration.

## Supported sizes
- 1024x1024
- 768x1360
- 896x1184
- 1360x768
- 1184x896

## Environment
- Set `STEP_API_KEY` before running CLI commands.
- Base URL: `https://api.stepfun.com/step_plan/v1`
- Default model: `step-image-edit-2`
- Optional model: `step-1x-medium` for style-reference image edits

## Output
- The CLI writes final images under `output/step_image/` by default.
- Use `--out` to choose a specific path.
- Do not overwrite existing assets unless the user asked for replacement.

## Reference map
- `references/cli.md`: CLI usage and recipes
- `references/image-api.md`: API parameters and limits
- `references/prompting.md`: prompt structure and iteration guidance
- `references/sample-prompts.md`: prompt recipes by use case
