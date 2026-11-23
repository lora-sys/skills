---
name: grill-me-with-docs
description: Align a user and development agent on a document-driven, multi-file task. Use when the user asks to reconcile project docs or agree on scope and acceptance, then save context.md.
---

# Grill Me with Docs

Use only when the user asks to align project documents before development. File count alone is not a trigger.

## Workflow

1. Read project instructions and only the relevant source documents. Map important claims to file paths and headings.
2. Separate facts, conflicts, assumptions, and decisions. Treat user-stated decisions as settled within their stated scope and record how they resolve conflicts. Ask one question at a time only when an unspecified choice can materially change scope or acceptance.
3. While a material choice is open, do not implement or create/update context.md. Leave source documents unchanged unless the user asks to edit them.
4. After the user settles a choice, including one stated in the request, record the goal, scope, decisions, constraints, acceptance criteria, and open questions. Never present an assumption as an agreement.
5. By default, create or update project-root context.md. Read it first and preserve unrelated content. Use references/context-template.md for new files.
6. Keep context concise. Link sources instead of copying them. Exclude secrets and unrelated personal data. Give the development agent a brief handoff to read context.md and its sources.

Do not message external people or services. User decisions and project rules remain authoritative.
