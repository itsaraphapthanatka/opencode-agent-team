---
description: Run the security-engineer for a full or scoped application security audit
---
Run the **security-engineer** subagent (or the `general` subagent with "read `.opencode/agents/security-engineer.md` and adopt it") with scope: $ARGUMENTS (empty means all).

Before relaying, verify its top 3 findings yourself at the cited file:line. Relay the report verbatim in {{LANG}}, mark which findings you confirmed, and list the tickets that should be opened (`/fix <finding>`).
