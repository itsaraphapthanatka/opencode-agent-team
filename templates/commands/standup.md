---
description: Cross-repo status in ten lines
---
Produce a standup in {{LANG}} (≤ 12 lines) without launching subagents:

1. For each repo in `{{CONTEXT_PATH}}`, one `shell` call: `git -C <repo> status --porcelain | wc -l` and `git -C <repo> log -3 --format='%h %ad %s' --date=short`.
2. Read `{{BACKLOG_PATH}}` (top 5 open P0 rows), `ls {{DOCS_DIR}}/tickets` (open count), the newest file in `{{DOCS_DIR}}/qa/` (date + verdict), and `{{DOCS_DIR}}/releases/UNRELEASED.md` if present.
3. Report: one line per repo (uncommitted files, last commit date + subject); then urgent items, open tickets, latest QA, and one suggested next command (`/fix …`, `/feature …`, `/test-all`).
