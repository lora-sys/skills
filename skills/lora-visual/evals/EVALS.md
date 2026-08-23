# lora-visual v1.0 acceptance tests

## Mode A — explanatory image

Prompt:

```text
Use $lora-visual in Mode A.

Create one finished explanatory image.

Title:
Agent Harness 的工作流程

Exact labels:
目标
计划
工具调用
反馈
结果

Show one left-to-right workflow.
Use lora + Mochi once as a narrative anchor.
No other readable text.
```

Pass only when:

- output is one final image, not a board/contact sheet
- title is exact
- all five labels are exact and appear once
- no extra readable text appears
- lora + Mochi appear once
- the workflow remains obvious without reading the labels
- palette remains black / cream / amber
- no purple-blue AI SaaS styling

Golden reference:

`assets/golden/mode-a/agent-harness-workflow.png`

## Mode B — transparent illustration

Prompt:

```text
Use $lora-visual in Mode B.

Create one reusable lora thinking asset.
No text.
```

Pass only when:

- one reusable asset is produced
- source is on a uniform chroma-key background
- `scripts/cutout.py` is actually run
- final output is RGBA PNG
- four corners have alpha 0
- subject is complete and not cropped
- lora identity matches the canonical reference
- no checkerboard or presentation board is treated as transparency

Golden references live in:

`assets/golden/mode-b/`
