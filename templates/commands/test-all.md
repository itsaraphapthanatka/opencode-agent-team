---
description: Run the QA team ({{TESTERS}}) in parallel and aggregate one report
---
You are the QA lead. Run the tester subagents for: $ARGUMENTS (empty = all of: {{TESTERS}}).

1. Launch every selected tester **in parallel** with the `subagent` tool (several calls in one message), each with: "Run your full procedure now. No arguments. Return only your report." Fall back to the `general` subagent with "read `.opencode/agents/<role>.md` and adopt it" when a type is not loaded.
2. Wait for all. Do not start fixing anything.
3. Verify the top 3 blocking findings yourself (read the file:line or re-run the request); drop or downgrade what you cannot reproduce.
4. Write one aggregated report in {{LANG}}: a table (area · verdict · bugs · security · warnings); "must fix first" across all areas by severity with file:line / METHOD /path and fix; security; warnings; "not tested and why"; then each tester's full report verbatim. Deduplicate findings several testers reported (keep the most precise, note who else saw it). Save it to `{{DOCS_DIR}}/qa/QA-REPORT-<YYYY-MM-DD>.md` and update `{{BACKLOG_PATH}}` rows for new blockers.
