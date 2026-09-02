# StepFun Image API reference

## Base URL
`https://api.stepfun.com/step_plan/v1`

## Endpoints
- Generate: `POST /v1/images/generations`
- Edit: `POST /v1/images/edits`

## Common parameters
- `model`: `step-image-edit-2` (default), `step-1x-medium`
- `prompt`: text description
- `n`: number of images (1-4)
- `size`: `1024x1024`, `768x1360`, `896x1184`, `1360x768`, `1184x896`
- `response_format`: `b64_json`

## Generation parameters
- `cfg_scale`: classifier-free guidance scale
- `steps`: inference steps
- `seed`: random seed
- `text_mode`: enable text optimization

## Edit parameters
- `image`: input image file(s)
- `prompt`: edit instruction
- `cfg_scale`, `steps`, `seed`, `text_mode`: same as generation

## Limits
- Prompt limit: 512 characters for `step-image-edit-2`
- Input image max size: 4096x4096
- Output matches input dimensions for edits
