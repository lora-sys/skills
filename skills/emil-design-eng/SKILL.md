---
name: emil-design-eng
description: After the first implementation of a web component with visible interaction, state, or motion, always invoke this as a separate refinement pass. Not for page direction, design systems, or pure logic.
---

# Emil Design Eng

After the first visible implementation, run this skill once as a separate refinement phase. Pre-reading or self-review does not replace this pass. Keep the approved page direction and design system.

## Refine

1. Inspect the component's visible states and the project's motion, input, and accessibility rules.
2. For each effect, identify what it communicates and how often users trigger it. Remove motion that adds delay or hides content. Keep frequent actions immediate.
3. Reuse project tokens and libraries. Keep repeated state changes interruptible. Do not add a dependency for a small effect.
4. Match direction, easing, and duration to the state. Keep hover feedback subtle. Avoid `transition: all` and abrupt `scale(0)`. Anchor menus and popovers to their trigger.
5. Preserve keyboard feedback, focus visibility, touch behavior, and reduced-motion support. Use hover effects only on hover-capable devices.
6. Verify changed states, including interrupted or rapid input. Report only what you observed.

For reviews, report findings in a Before / After / Why table. For implementation, make the smallest useful change and report the states checked.

For meaningful visual choices, prefer a rendered comparison or preview over long prose. Skip extra artifacts for tiny or mechanical changes.

These guidelines adapt principles from [Emil Kowalski's public skills](https://github.com/emilkowalski/skills), especially its emil-design-eng skill. The project and user design rules take precedence.
