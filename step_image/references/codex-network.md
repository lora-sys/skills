# StepFun API access notes

## Authentication
Set `STEP_API_KEY` with a key from https://platform.stepfun.com.

## Network
The CLI makes outbound HTTPS requests to `api.stepfun.com`. Ensure your environment allows outbound traffic on port 443.

## Rate limits
StepFun may return 429 on rate limit. The CLI retries transient errors with backoff.
