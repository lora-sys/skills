---
name: remote-dev
description: Use when the user explicitly requests dependency installation, tests, or service checks on a configured development host. Not for local-only tests or production deployment.
---

# Remote development

## Prepare

1. Find the local project root with Git. Ask for the source directory if it is not a Git working tree.
2. Read `local-targets.md` beside this installed skill. Match a target only to a project category the user stated. If the category or target is missing, ask and stop. Never infer it from the repository, name, or Git remote.
3. Preview the transfer before writing. Exclude `.git`, `.env*`, local agent settings, dependencies, caches, and build output. Add project-specific excludes. Review every overwrite and deletion; stop if any are unexpected. Never use `--delete-excluded`.

## Verify on the development host

- Keep source edits local. For an explicit remote check, run the requested install, tests, and service checks on the configured host. Do not repeat the same test suite locally just to satisfy that request.
- Choose install and test commands from the lockfile and project instructions. Start only the requested service. Do not use `sudo`, touch production hosts, or stop processes you did not start.
- If source changes are needed, make them locally, transfer again, and rerun the affected remote checks.
- Report commands actually run and their results. Mark skipped or failed checks clearly; never claim an unrun remote check passed.

Keep passwords and private keys out of `local-targets.md` and command arguments. If the local target file is missing, do not invent SSH or transfer commands; ask the user to configure a target or use another explicitly authorized workflow.
