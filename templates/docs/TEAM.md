# {{PROJECT}} agent team (org chart)

All agents live in `{{PROJECT_ROOT}}/.opencode/agents/`; commands in `{{PROJECT_ROOT}}/.opencode/commands/`. OpenCode subagents cannot spawn subagents (nesting depth is one), so the roles that *coordinate* are slash commands run by the main session (you + OpenCode), acting as engineering manager. Profile: `{{PROFILE}}`. Every agent reads `{{CONTEXT_PATH}}` and `{{LEARNINGS_PATH}}` first and keeps per-role memory in `{{MEMORY_ROOT}}/<role>/` (commit it; it holds no secrets).

| Agent | Category | Model |
|---|---|---|
{{ROLE_TABLE}}

What each role does, in one line:
- `product-manager` PRD, user stories, acceptance criteria, backlog priority → `product/`
- `architect` ADR, technical design naming endpoints/schemas/migrations per repo, spikes → `adr/`, `design/`
- `ux-designer` flows, screen specs, copy in every supported language, HTML mockups → `design/ux/`
- `ui-designer` design system, component specs with real class names, visual QA → `design/DESIGN-SYSTEM.md`, `design/ui/`
- `backend-dev` / `mobile-dev` / `web-dev` implement from PRD + design in their repo, prove with the repo's checks and tests
- `test-engineer` permanent automated tests and test infrastructure; turns findings into regression tests
- `api-tester`, `e2e-tester`, `mobile-tester`, `web-tester` exploratory system test runs, report only
- `code-reviewer` read-only review of a diff · `bug-triager` reproduce → ticket → owner
- `security-engineer` authz/PII/secrets/money audit → `runbooks/security/`
- `devops-engineer` Docker, CI, migrations ops, deploy prep (never deploys) → infra files, `runbooks/`
- `tech-writer` README, runbooks, API docs, release notes; owns `PROJECT-CONTEXT.md`

## Commands
| Command | Flow |
|---|---|
| `/feature <idea>` | product-manager → architect (+ux → ui) → scrutiny → **checkpoint** → devs in parallel → code-reviewer + security-engineer → test-engineer → testers → tech-writer |
| `/fix <bug>` | bug-triager → owning dev → code-reviewer (+security) → regression test → re-test → ticket closed |
| `/prd`, `/adr`, `/security-audit`, `/release`, `/test-all`, `/review`, `/standup`, `/team` | single-role or utility flows |

## Working agreements
- The PRD says *what* and *why*; the design says *how*; devs do not widen scope beyond them.
- Nothing is "done" without: checks clean, a test (or written manual check), code-reviewer pass, docs touched if behaviour changed.
- No commits, deploys, or production calls unless the owner says so in that turn.
- Everyone reads the context file first and corrects it when it is wrong; lessons go to `LEARNINGS.md`.
