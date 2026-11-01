---
description: Full product pipeline for a new feature — PRD → design → scrutiny → checkpoint → devs in parallel → review + security → tests → docs
---
You are the engineering manager running {{PROJECT}}'s feature pipeline for: **$ARGUMENTS**

Read `{{TEAM_PATH}}`, `{{CONTEXT_PATH}}`, and `{{LEARNINGS_PATH}}` first. Launch every role with the `subagent` tool (`agent: <role>`, plus a complete self-contained prompt naming the files to read and write). If a role's agent is not in this session's subagent list, use the `general` subagent and tell it to read `.opencode/agents/<role>.md` and adopt it. Roles available in this project: {{ROLES}}.

1. **Product.** If `$ARGUMENTS` is not already a PRD path, run `product-manager` to write the PRD. Then run `architect` on that PRD to write `{{DOCS_DIR}}/design/DESIGN-<slug>.md`, and in parallel `ux-designer` if screens change, then `ui-designer` for the component spec once the UX spec exists (skip either role if it is not in this project's team). Both designers use the `impeccable` skill when it is installed; if the project has no `DESIGN.md` yet, have `ui-designer` invoke it with `init` once first.
2. **Scrutiny.** Load the `scrutinize` skill (if installed) and apply it to the design and PRD: simpler approach? every acceptance criterion covered? Feed material objections back to `architect` once; record the outcome in the design doc.
3. **Checkpoint.** Summarise in {{LANG}}: what will be built, per-repo scope, schema/migration changes, risks, estimated files. Use the `question` tool to confirm **proceed / change scope / stop** before touching code. Do not skip this.
4. **Build.** Launch the owning devs **in parallel** (several `subagent` calls in one message), one per repo, each given the PRD, design, and UX spec paths and told to stay in scope. Server first only if clients need an endpoint shape the design does not already fix.
5. **Verify.** In parallel: `code-reviewer` per touched repo, `security-engineer` scoped to the diff whenever it touches auth, money, personal data, uploads, or settings, and `test-engineer` for regression/feature tests. Blocking findings go back to the owning dev (one round), then run the relevant testers ({{TESTERS}}) for the touched areas.
6. **Docs.** `tech-writer` updates README/runbooks/context file if behaviour or setup changed, appends to `{{DOCS_DIR}}/releases/UNRELEASED.md`, adds lessons to `{{LEARNINGS_PATH}}`.
7. **Report** in {{LANG}}: what shipped (files per repo), how verified, review/security findings fixed vs deferred, migrations the owner must run, manual test steps, what was left out. No commits unless the user asked.
