---
name: agent-team
description: "Bootstrap or extend a full software-company agent team (PM, architect, UX + UI designers, backend/mobile/web devs, SDET, QA testers, code reviewer, bug triager, security, devops, tech writer) plus pipeline commands (/feature, /fix, /test-all, …) in the current project, grounded in that project's real code. Use when the user wants an agent team, dev team, QA team, tester team, or says สร้างทีม / ทีม agent / ทีม dev / ทีม tester for a project."
---

# agent-team — build a project-grounded agent company (OpenCode)

You are setting up (or extending) an agent team for the project in the active OpenCode working directory. The user's request after the skill mention selects the operation — `init` (default), `add <role>`, `status`, or `upgrade <role|all>` — plus optional flags `--profile max|balanced|economy`, `--roles core|full|<list>`, `--lang Thai|English`.

The team's quality comes from **one rich, verified context file** that every agent reads first, not from long agent prompts. Spend most of your effort on that file.

Skill files live beside this `SKILL.md`; the base directory is shown when the skill loads. Templates: `templates/`, renderer: `scripts/render.py`, role/profile reference: `reference/roles.md`. Use the `shell` tool for commands and the `question` tool for choices — OpenCode has no `AskUserQuestion`, `Bash`, or `Agent` tool.

## What gets generated (OpenCode layout)

| Path | What |
|---|---|
| `.opencode/agents/<role>.md` | subagent definitions (`mode: subagent`) |
| `.opencode/commands/<name>.md` | `/feature`, `/fix`, `/test-all`, `/prd`, `/adr`, `/security-audit`, `/release`, `/standup`, `/review`, `/team` |
| `.opencode/agent-team.json` | config the renderer reads |
| `.opencode/agent-memory/<role>/` | per-role persistent memory, committed with the project |
| `<docs_dir>/` | `PROJECT-CONTEXT.md`, `TEAM.md`, `LEARNINGS.md`, `product/BACKLOG.md` |

OpenCode discovers these automatically; do not tell the user to restart. `/reload` is only a fallback if a new agent or command does not appear.

## `init` — full bootstrap

1. **Explore, don't assume.** In one or two `shell` passes, establish for every repo involved (the project dir, plus any additional working directories the user names or that obviously belong to the same product):
   - git root, remote, default branch, contributors (`git shortlog -sne | head`), uncommitted state
   - stack from manifests (`package.json` deps/scripts, `requirements.txt`/`pyproject.toml`, `go.mod`, `Gemfile`, `pubspec.yaml`, `Cargo.toml`, `composer.json`), framework and version, language version actually installed
   - how to typecheck / lint / test / build / run (read the scripts; **run the cheap ones once** to confirm they work — record failures such as missing `node_modules` or venv deps)
   - infra: Dockerfile, compose, CI workflows, deploy scripts, migrations tool and whether it works
   - environments: env var **names** (never values), local ports, production URLs, which services are running locally right now
   - domain: what the product does, its roles/users, core entity state machines, money or PII involved
   - existing conventions: i18n, folder layout, error handling, auth pattern; existing docs, `AGENTS.md`, `.opencode/` contents (reuse, do not duplicate)
   - hygiene red flags to record: secrets or `.env` tracked in git, vendored `venv/`/`node_modules`, unpinned deps
2. **Choose the team.** Use the `question` tool (one call, up to 4 questions) for: profile (`max` = strongest model + highest effort, `balanced`, `economy`), role set (`core` = product-manager, architect, one dev per detected stack, test-engineer, code-reviewer, bug-triager; `full` = all 17), report language, and docs location (default `<project>/docs`; for multi-repo products suggest a shared parent folder). Skip questions the user already answered. Only include `ux-designer`/`ui-designer` when there is a user interface, `mobile-dev`/`mobile-tester` when a mobile stack exists, `web-dev`/`web-tester` when a web front-end exists, `backend-dev`/`api-tester`/`e2e-tester` when there is a server.
3. **Choose models.** OpenCode model IDs are `provider/model` with an optional `#variant` for effort. The safe default is to omit `model` entirely so every subagent inherits the session model — the team then works with whatever provider the user runs. Offer that first. Only write a `models` map (`heavy` / `other` / `light` → full model IDs) when the user names models; ask with the `question` tool or read the user's `~/.config/opencode/opencode.jsonc`. Never guess a model ID. Run `opencode --version`: if it reports a 1.x build, the V1 runner ignores V2 `permissions`, so set `"compat_v1": true` and the renderer also emits the legacy `permission:` map that V1 enforces.
4. **Write the config** to `.opencode/agent-team.json` (schema in `reference/roles.md`): project name, project_root, docs_dir, report_language, profile, roles, repos (name, path, stack, check commands you verified), optional `models` (tier → `provider/model#variant`), optional `compat_v1`, optional per-role `specifics` (2–8 lines of verified, project-specific guidance such as the layered layout to follow, the test recipe, ports to use) and per-role `overrides` (`{"code-reviewer": {"model": "provider/model#variant"}}`).
5. **Render.** `python3 "<skill-base>/scripts/render.py" --config .opencode/agent-team.json`. It writes the agents, commands, docs and memory dirs. It never overwrites existing files without `--force`; read its summary.
6. **Fill the context file.** Open `<docs_dir>/PROJECT-CONTEXT.md` and replace every `TODO` with verified facts from step 1: product paragraph, repo table with working check commands, architecture map (entry points, layers, route prefixes, auth pattern), environments and the isolated test recipe, conventions, hygiene red flags, and a "baseline" section (link the last QA report if any). This file is what makes the team smart; do not leave placeholders.
7. **Validate.** `python3 "<skill-base>/scripts/render.py" --config .opencode/agent-team.json --check` (frontmatter, deprecated Claude Code / V1 keys, model format, YAML hazards). Then report in the chosen language: roles created with model/effort tier, commands available, docs paths, hygiene red flags found, and how to invoke a subagent (mention it by name, or run a command). Suggest the first two commands (usually `/test-all` for a baseline, then `/standup`).

## `add <role>`
Render one role from `templates/agents/<role>.md` with `--only <role>` (config must exist), then add a project-specific `specifics` block if the role needs one, and append the row to `<docs_dir>/TEAM.md`.

## `status`
List `.opencode/agents` and `.opencode/commands`, run `--check`, show model (or "inherit") per agent, size of each `.opencode/agent-memory/<role>/`, and the age of `PROJECT-CONTEXT.md` versus the newest commit (stale context is the usual cause of dumb agents).

## `upgrade <role|all>`
`--scope` selects what gets re-rendered (`agents`, `commands`, `docs`, `all`, comma-separated). Upgrades never include `docs`:

- `upgrade <role>` — `--force --scope agents --only <role>`, then re-apply that role's `specifics` from the config.
- `upgrade all` — `--force --scope agents,commands`. Commands change between template versions too, so a per-role loop is not an "upgrade all".

**Never run a bare `--force` on an initialised project.** Without `--scope` it also re-renders `<docs_dir>/{PROJECT-CONTEXT.md,TEAM.md,LEARNINGS.md,product/BACKLOG.md}`, resetting the hand-filled context that makes the team smart back to empty TODO scaffolds. If that has already happened, each clobbered file has a `.bak` beside it: restore from the `.bak`, then delete the `.bak`s. (`--scope docs` is the deliberate way to reset those scaffolds.)

Show the diff before overwriting anything the user may have hand-edited (`git diff` if tracked, otherwise compare against the `*.bak`), and finish with `--check`.

## Rules
- Never write secrets into any generated file. Env var names only.
- Never `git add/commit` the generated files unless asked; tell the user they are meant to be committed (agent memory included, it holds no secrets).
- Reuse what exists: if the project already has agents, `AGENTS.md`, or docs, integrate (link, extend) instead of duplicating.
- Prefer verified specifics over generic prose. A command you did not run is written as "unverified".
- Subagents cannot launch other subagents in OpenCode; coordination lives in the slash commands run by the main session. Do not write an agent that depends on spawning another agent.
