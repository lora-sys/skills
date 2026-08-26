# CLI reference (`scripts/image_gen.py`)

## What this CLI does
- `generate`: create a new image from a prompt
- `edit`: edit one or more existing images

## Quick start

Dry run:
```bash
python scripts/image_gen.py generate \
  --prompt "Test" \
  --out output/step_image/test.png \
  --dry-run
```

Generate:
```bash
python scripts/image_gen.py generate \
  --prompt "A cozy alpine cabin at dawn" \
  --size 1024x1024 \
  --out output/step_image/alpine-cabin.png
```

Edit:
```bash
python scripts/image_gen.py edit \
  --image input.png \
  --prompt "Replace only the background with a warm sunset" \
  --out output/step_image/sunset-edit.png
```

## Defaults
- Model: `step-image-edit-2`
- Size: `1024x1024`
- Output format: `png`
- Default output path: `output/step_image/output.png`

## Supported sizes
- `1024x1024`
- `768x1360`
- `896x1184`
- `1360x768`
- `1184x896`

## Parameters
- `--cfg-scale`: classifier-free guidance scale
- `--steps`: inference steps
- `--seed`: random seed for reproducibility
- `--text-mode`: enable text-optimized generation

## Environment
- `STEP_API_KEY` must be set for live API calls.
- Do not paste the key in chat. Set it in the environment and confirm when ready.
