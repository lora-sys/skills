# Offline PR fixture

This directory simulates PR state locally. It contains no real repository or remote credentials. `state.json` is synthetic; `bin/gh` implements the subset of GitHub CLI commands needed by the fixture, and records invocations in `calls.jsonl`.

To use the mock, prepend `bin/` to `PATH`.
