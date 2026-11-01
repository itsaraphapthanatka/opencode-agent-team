---
description: Prepare a release — devops checklist + release notes, no deploy
---
Prepare a release for: $ARGUMENTS (empty = every repo with commits since its last release note in `{{DOCS_DIR}}/releases/`).

Run **in parallel** (two `subagent` calls in one message): `devops-engineer` to produce/update `{{DOCS_DIR}}/releases/CHECKLIST.md` and the deploy runbook for the target (migrations, env vars, rebuilds, smoke tests, rollback), and `tech-writer` to write `{{DOCS_DIR}}/releases/<YYYY-MM-DD>-<repo>.md` from git history. (Fall back to the `general` subagent + "read `.opencode/agents/<role>.md`" when a type is not loaded.)

Report in {{LANG}}: what is in the release, the ordered steps the owner runs, and blockers from the latest QA report still open. Never deploy, tag, or push.
