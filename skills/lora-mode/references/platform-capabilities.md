# Platform capability routing

Read this only when a task needs browser, desktop, or office-file tools. Check the target runtime's available skills and tools first; names below are routing examples, not guarantees. Do not install or configure tools without authorization.

| Need | Route | Boundary |
|---|---|---|
| Public web research | Built-in web search/fetch | Use for public information when no interactive session is needed. |
| Logged-in websites and browser UI | `ego-browser` (`ego-lite`) | Read its skill and current usage guide first; use for the user's logged-in browser context. |
| Browser or Electron interaction | `agent-browser` | Load its task skill before CLI use; use for structured browser interaction or supported Electron apps. |
| Repeatable browser flow or E2E check | `playwright` | Use the repo's existing test stack for checked-in tests; use its CLI for ad hoc interaction. |
| Native desktop, visual-only, or canvas interaction | `computer-use` / CUA | Use for on-screen controls that DOM or CLI cannot operate; skip it for ordinary browser or file work. |
| Local `.docx` creation, editing, review | `documents:documents` | Render and inspect the final pages when layout matters. |
| Local `.xlsx`, `.xls`, or CSV work | `spreadsheets:Spreadsheets` | Use its supported workbook workflow and verify formulas and visible output. |
| Native Google Docs or Sheets | `google-drive:google-docs` / `google-drive:google-sheets` | Use for native Drive files; do not treat them as local DOCX/XLSX files. |
| Live Excel session | `spreadsheets:excel-live-control` | Use only to control an open workbook; use `spreadsheets:Spreadsheets` for ordinary workbook files. |
| PDF or presentation work | `pdf:pdf` / `presentations:Presentations` (or another installed specialist skill) | Load only for those deliverables. |

Prefer the narrowest available route. If the required capability is absent, report that and use an available equivalent only when it preserves the requested interaction; do not silently substitute public web access for an authenticated browser or desktop session.
