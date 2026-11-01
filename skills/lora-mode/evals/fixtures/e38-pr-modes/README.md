# Offline PR fixture

This directory simulates PR state locally. It contains no real repository or remote credentials. `state.json` is synthetic; `bin/gh` implements the subset of GitHub CLI commands needed by the fixture, and records invocations in `calls.jsonl`.

To run the mock, prepend `bin/` to `PATH`. From the skills repository root, the deterministic tests run with `rtk python3 -m unittest discover -s skills/lora-mode/evals/fixtures/e38-pr-modes`.
