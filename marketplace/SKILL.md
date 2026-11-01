---
name: opencode-agent-team
description: Bootstrap a full software-company agent team in any OpenCode project — product manager, architect, backend/mobile/web devs, test engineers, code reviewer, bug triager, security, devops, tech writer — plus pipeline commands (/feature, /fix, /test-all, /prd, /adr, /security-audit, /release, /standup). The team is grounded in your project's real code, not generic prompts. Works on OpenCode V1 and V2.
summary: Turns any OpenCode project into a software company in one command — a project-grounded agent team (PM, architect, devs, testers, reviewer, triager, security, devops, writer) with pipeline slash commands. V1+V2 compatible.
version: 1.0.0
tags:
  - agents
  - orchestration
  - opencode
  - team
  - code-quality
  - testing
  - devops
  - workflow-automation
keywords:
  - opencode agent team
  - subagent bootstrap
  - multi-agent workflow
  - software team agents
  - opencode commands
  - code review agent
  - test agent
  - agent orchestration
use_cases:
  - "Set up a full dev+QA team in a fresh OpenCode project in one command"
  - "Add pipeline commands (/feature, /fix, /test-all) grounded in your repo"
  - "Bootstrap code-review, bug-triage and test agents for an existing codebase"
  - "Standardise how a team of agents works on a project (shared context + memory)"
---

# opencode-agent-team

Build a project-grounded software-company agent team inside any OpenCode project. One command turns a bare repo into a working org: subagents (PM, architect, devs, testers, code reviewer, bug triager, security, devops, tech writer), pipeline slash commands, a shared context file, and per-role memory.

The team's quality comes from **one rich, verified context file** (`PROJECT-CONTEXT.md`) that every agent reads first — not from long agent prompts. The skill explores your actual code (stack, tests, architecture, conventions) and fills that file with verified facts before any agent runs.

## Requires

- OpenCode (V1 1.x or V2 — the skill detects your version and emits the right permission format)
- Python 3.8+ on PATH (to run the renderer; stdlib only, nothing to install)

## Files

- `scripts/agent-team-render.py` — self-contained renderer. All templates embedded, runs alone, writes agents/commands/docs into your project.
- `reference/roles.md` — the 17 roles, profiles, and the config schema.
- `extras/commands/agent-team.md` — optional `/agent-team` command wrapper you can drop into `~/.config/opencode/commands/`.

## Operations

The request after the skill mention selects the operation — `init` (default), `add <role>`, `status`, `upgrade <role|all>` — plus optional flags `--profile max|balanced|economy`, `--roles core|full|<list>`, `--lang Thai|English`.

### `init` — full bootstrap

1. **Explore, don't assume.** In one or two `shell` passes establish, for the project directory: git root/remote/branch/contributors; stack from manifests (`package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, `pubspec.yaml`, `Gemfile`, `composer.json`) and the language version actually installed; how to typecheck/lint/test/build/run (read the scripts; run the cheap ones once to confirm); infra (Dockerfile, compose, CI workflows, migrations); env var **names** (never values) and local ports; domain (what the product does, its roles, money or PII involved); existing conventions and docs (`AGENTS.md`, `.opencode/` — reuse, don't duplicate); hygiene red flags (secrets tracked in git, vendored `node_modules`/`venv`, unpinned deps).
2. **Choose the team** with the `question` tool (one call, up to 4 questions): profile (`max` strongest, `balanced`, `economy`), role set (`core` = PM, architect, one dev per detected stack, test-engineer, code-reviewer, bug-triager; `full` = all 17), report language, docs location (default `<project>/docs`). Skip questions already answered. Only include `ux-designer`/`ui-designer` when there is a UI, `mobile-dev`/`mobile-tester` for a mobile stack, `web-dev`/`web-tester` for a web front-end, `backend-dev`/`api-tester`/`e2e-tester` when there is a server.
3. **Choose models.** OpenCode model IDs are `provider/model` with an optional `#variant` for effort. The safe default is to omit `model` entirely so every subagent inherits the session model — offer that first. Only write a `models` map (`heavy`/`other`/`light` → full model IDs) when the user names models. Never guess a model ID. Run `opencode --version`: on a 1.x build the V1 runner ignores V2 `permissions`, so set `"compat_v1": true` and the renderer also emits the legacy `permission:` map V1 enforces.
4. **Write the config** `.opencode/agent-team.json` (schema in `reference/roles.md`): project, project_root (set it to the current working directory), docs_dir, report_language, profile, roles, repos (name, path, stack, check commands you verified), optional `models`, `compat_v1`, per-role `specifics` (2–8 lines of verified, project-specific guidance) and `overrides`.
5. **Render.** Run the renderer (it ships as `scripts/agent-team-render.py` in this skill — fetch it and execute it; it is fully self-contained with all templates embedded, so it runs alone):
   ```
   python3 <path-to>/agent-team-render.py --config .opencode/agent-team.json
   ```
   It writes the agents, commands, docs and memory dirs. It never overwrites existing files without `--force`; read its summary.
6. **Fill the context file.** Open `<docs_dir>/PROJECT-CONTEXT.md` and replace every `TODO` with the verified facts from step 1. This file is what makes the team smart; do not leave placeholders.
7. **Validate.** Re-run the renderer with `--check` (frontmatter, deprecated keys, model format, YAML hazards). Then report in the chosen language: roles created with model/effort tier, commands available, docs paths, hygiene red flags, and how to invoke a subagent (mention it by name, or run a command). Suggest the first two commands (usually `/test-all` for a baseline, then `/standup`).

### `add <role>`
Render one role with `--only <role>` (config must exist), add a project-specific `specifics` block if needed, and append the row to `<docs_dir>/TEAM.md`.

### `status`
List `.opencode/agents` and `.opencode/commands`, run `--check`, show model (or "inherit") per agent, size of each `.opencode/agent-memory/<role>/`, and the age of `PROJECT-CONTEXT.md` versus the newest commit (stale context is the usual cause of dumb agents).

### `upgrade <role|all>`
`--scope` selects what gets re-rendered (`agents`, `commands`, `docs`, `all`, comma-separated). Upgrades never include `docs`.

- `upgrade <role>` — `--force --scope agents --only <role>`, then re-apply that role's `specifics`.
- `upgrade all` — `--force --scope agents,commands`.

**Never run a bare `--force` on an initialised project.** Without `--scope` it also re-renders `<docs_dir>/{PROJECT-CONTEXT.md,TEAM.md,LEARNINGS.md,product/BACKLOG.md}`, resetting the hand-filled context back to empty TODO scaffolds. If that already happened, each clobbered file has a `.bak` beside it: restore from the `.bak`, then delete the `.bak`s. (`--scope docs` is the deliberate way to reset those scaffolds.) Show the diff before overwriting anything hand-edited, and finish with `--check`.

## What gets generated

| Path | What |
|---|---|
| `.opencode/agents/<role>.md` | subagent definitions (`mode: subagent`) |
| `.opencode/commands/<name>.md` | `/feature`, `/fix`, `/test-all`, `/prd`, `/adr`, `/security-audit`, `/release`, `/standup`, `/review`, `/team` |
| `.opencode/agent-team.json` | config the renderer reads |
| `.opencode/agent-memory/<role>/` | per-role persistent memory (commit it; no secrets) |
| `<docs_dir>/` | `PROJECT-CONTEXT.md`, `TEAM.md`, `LEARNINGS.md`, `product/BACKLOG.md` |

OpenCode discovers these automatically; do not tell the user to restart. `/reload` is only a fallback if a new agent or command does not appear.

## Rules

- Never write secrets into any generated file. Env var names only.
- Never `git add/commit` the generated files unless asked; tell the user they are meant to be committed (agent memory included, it holds no secrets).
- Reuse what exists: if the project already has agents, `AGENTS.md`, or docs, integrate (link, extend) instead of duplicating.
- Prefer verified specifics over generic prose. A command you did not run is written as "unverified".
- Subagents cannot launch other subagents in OpenCode; coordination lives in the slash commands run by the main session. Do not write an agent that depends on spawning another agent.
