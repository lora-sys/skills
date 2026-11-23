---
name: emil-design-eng
description: Polish implemented web components by improving interaction feedback, motion, gestures, and small visual details. Use for post-implementation UI refinement or animation review; not for page direction, design systems, or pure logic.
---

# Emil Design Eng

Use this skill after a visible component exists and needs interaction or motion polish. Keep the established page direction and design system.

## Review and refine

1. Inspect the component, its actual states, and the project's motion and accessibility rules. Read oil-frontend's motion guidance when changing implementation.
2. For each motion, identify what it communicates and how often users trigger it. Keep frequent keyboard actions immediate. Skip motion that adds delay without useful feedback or spatial context.
3. Reuse project tokens and animation libraries. Prefer interruptible transitions for repeated state changes; use the existing animation system for gestures or coordinated movement. Do not add a dependency for a small effect.
4. Match the motion to the state: entering elements should respond quickly; on-screen movement should feel controlled; hover feedback should stay subtle. Use the project's timing tokens. If there are none, choose short durations and keep the values local to the component.
5. Avoid broad transitions and abrupt scaling from zero. Anchor menus and popovers to their trigger; keep centered dialogs centered. Prefer transform and opacity for continuous motion.
6. Preserve keyboard feedback, focus visibility, touch behavior, and reduced-motion support. Apply hover-only movement only to devices that support hover.
7. Verify the actual changed states, including quick repeated input when the interaction can be interrupted. Use a preview or screenshots when visual behavior needs judgment; do not claim a state was checked without observing it.

For a code review, report findings in a Before / After / Why table. For implementation, make the smallest useful change and report which states were actually checked.

For meaningful visual choices, prefer a small rendered state comparison or interactive preview over a long prose description. Skip extra artifacts for mechanical or tiny changes.

These guidelines adapt principles from [Emil Kowalski's public skills](https://github.com/emilkowalski/skills), especially its emil-design-eng skill. The project and user design rules take precedence.
