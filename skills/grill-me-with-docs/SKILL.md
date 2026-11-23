---
name: grill-me-with-docs
description: Align a user and development agent on a multi-file task. Use when the user asks to reconcile documents or agree on scope, decisions, and acceptance, then save the shared context to context.md.
---

# Grill Me with Docs

Use when the user asks to align on a document-heavy task before development. Do not trigger on file count alone or when the request and source documents already agree.

## Workflow

1. Read the supplied files, relevant project instructions, and only the nearby sources needed to resolve the task. Map each important statement to its file and heading.
2. Separate confirmed facts, conflicting requirements, assumptions, and decisions. Do not ask questions that the sources already answer.
3. Ask one material question at a time. Explain the conflict briefly and offer clear choices when possible. Do not edit implementation files while a consequential decision is open.
4. Summarize the agreed goal, scope, non-goals, constraints, decisions, and acceptance criteria. Mark unresolved items as open; never present an assumption as an agreement.
5. After the user confirms the summary or explicitly approves the stated assumptions, create or update context.md at the requested location. If no location is given, use the project root. Read an existing context.md first and preserve unrelated content. Use references/context-template.md when creating the file.
6. Keep context.md compact. Link to source paths and headings instead of copying long passages. Exclude secrets and unrelated personal data.
7. Give the development agent a handoff to read context.md and its cited sources. User instructions and project rules remain authoritative; report any conflict before implementation.

Do not send messages to external people or services. The handoff is a local task brief.
