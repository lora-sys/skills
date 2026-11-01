# Offline PR fixture

This directory simulates PR state locally. It contains no real repository or remote credentials. `state.json` is synthetic; `bin/gh` models the GitHub CLI shapes and the lora-mode merge gates needed by these evals, and records invocations in `calls.jsonl`. It is not a full GitHub API emulator.

To use the mock, prepend `bin/` to `PATH`.

Run the fixture tests from the repository root with:

```bash
rtk python3 -m unittest discover -s skills/lora-mode/evals/tests -p 'test_*.py' -v
```
