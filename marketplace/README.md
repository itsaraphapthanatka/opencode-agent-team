# opencode-agent-team

Turn any OpenCode project into a working software company — in one command.

This skill bootstraps a **project-grounded agent team** inside your repo: subagents (product manager, architect, devs, testers, code reviewer, bug triager, security, devops, tech writer), pipeline slash commands, a shared context file, and per-role memory. The team is grounded in **your project's real code** — its stack, its tests, its architecture, its conventions — not generic prompts.

## What you get

```
<your-project>/
├── .opencode/
│   ├── agents/<role>.md        # subagents (mode: subagent)
│   ├── commands/<name>.md      # /feature, /fix, /test-all, /prd, /adr, …
│   ├── agent-team.json         # the config (edit to extend the team)
│   └── agent-memory/<role>/    # per-role persistent memory
└── docs/
    ├── PROJECT-CONTEXT.md      # the verified context every agent reads first
    ├── TEAM.md                 # org chart
    ├── LEARNINGS.md            # system-level lessons, appended over time
    └── product/BACKLOG.md      # prioritised backlog
```

- **17 roles** — pick `core` (PM, architect, one dev per stack, test-engineer, code-reviewer, bug-triager) or `full`.
- **10 pipeline commands** — `/feature`, `/fix`, `/test-all`, `/prd`, `/adr`, `/security-audit`, `/release`, `/standup`, `/review`, `/team`.
- **V1 + V2 compatible** — the skill detects your OpenCode version and emits the right permission format (`permissions:` list for V2, legacy `permission:` map for V1 via `compat_v1`).
- **Any provider** — subagents inherit your session model by default, so it works with whatever provider you run. Pin models per tier or per role if you want.

## Requirements

- OpenCode (V1 1.x or V2)
- Python 3.8+ on PATH (stdlib only — nothing to install)

## How it works

1. The skill explores your repo: stack, test commands, architecture, conventions, hygiene red flags.
2. It asks you four quick questions (profile, role set, report language, docs location).
3. It writes a config and runs the self-contained renderer, which generates every agent, command and doc.
4. It fills `PROJECT-CONTEXT.md` with verified facts about *your* project.

After that, mention an agent by name (`@code-reviewer review this diff`) or run a command (`/feature add JWT login`).

## Files

| File | What it is |
|---|---|
| `scripts/agent-team-render.py` | Self-contained renderer (all templates embedded; runs alone) |
| `reference/roles.md` | The 17 roles, profiles, and config schema |
| `extras/commands/agent-team.md` | Optional `/agent-team` command wrapper |

## Source

Built from [`opencode-agent-team`](https://github.com/itsaraphapthanatka/opencode-agent-team) by itsaraphap. MIT-licensed — see `LICENSE`.
