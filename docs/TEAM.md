# opencode-agent-team agent team (org chart)

All agents live in `./.opencode/agents/`; commands in `./.opencode/commands/`. OpenCode subagents cannot spawn subagents (nesting depth is one), so the roles that *coordinate* are slash commands run by the main session (you + OpenCode), acting as engineering manager. Profile: `balanced`. Every agent reads `docs/PROJECT-CONTEXT.md` and `docs/LEARNINGS.md` first and keeps per-role memory in `.opencode/agent-memory/<role>/` (commit it; it holds no secrets).

| Agent | Category | Model |
|---|---|---|
| `product-manager` | think | inherit (other · high effort) |
| `architect` | think | inherit (heavy · high effort) |
| `backend-dev` | build | inherit (heavy · high effort) |
| `test-engineer` | build | inherit (other · high effort) |
| `code-reviewer` | adversarial | inherit (heavy · high effort) |
| `bug-triager` | adversarial | inherit (other · high effort) |
| `tech-writer` | think | inherit (light · high effort) |

What each role does, in one line:
- `product-manager` PRD, user stories, acceptance criteria, backlog priority → `product/`
- `architect` ADR, technical design (file layout, renderer behavior, V1/V2 strategy), spikes → `adr/`, `design/`
- `backend-dev` implement from PRD + design in this repo (Python stdlib), prove with `python3 -m unittest discover -s tests`
- `test-engineer` permanent automated tests and test infrastructure; turns findings into regression tests
- `code-reviewer` read-only review of a diff · `bug-triager` reproduce → ticket → owner
- `tech-writer` README, runbooks, release notes; owns `PROJECT-CONTEXT.md`

## Commands
| Command | Flow |
|---|---|
| `/feature <idea>` | product-manager → architect → scrutiny → **checkpoint** → backend-dev + test-engineer → code-reviewer → tech-writer |
| `/fix <bug>` | bug-triager → backend-dev → code-reviewer → regression test → ticket closed |
| `/prd`, `/adr`, `/release`, `/review`, `/standup`, `/team` | single-role or utility flows |

ยังไม่ได้ติดตั้ง: `/test-all` (ต้องมี adversarial tester เช่น `api-tester`) และ `/security-audit` (ต้องมี `security-engineer`) — เพิ่มภายหลังด้วย `/agent-team add <role>` แล้ว re-render

## Working agreements
- The PRD says *what* and *why*; the design says *how*; devs do not widen scope beyond them.
- Nothing is "done" without: checks clean, a test (or written manual check), code-reviewer pass, docs touched if behaviour changed.
- No commits, deploys, or production calls unless the owner says so in that turn.
- Everyone reads the context file first and corrects it when it is wrong; lessons go to `LEARNINGS.md`.
