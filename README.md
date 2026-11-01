# agent-team — a software company of OpenCode agents, for any project

`@agent-team init` explores the current project, asks four questions (profile, roles, report language, docs location), then generates a team of OpenCode subagents (`.opencode/agents/`), pipeline commands (`.opencode/commands/`: `/feature`, `/fix`, `/test-all`, `/prd`, `/adr`, `/security-audit`, `/release`, `/standup`, `/review`, `/team`) and a shared docs folder (`PROJECT-CONTEXT.md`, `TEAM.md`, `LEARNINGS.md`, `product/BACKLOG.md`) — all grounded in that project's real code. Every agent reads the context file and its own persistent memory first, follows an expert protocol (plan → verify → self-review → leave lessons), and reports in your language.

Roles: product-manager · architect · ux-designer · ui-designer · backend-dev · mobile-dev · web-dev · test-engineer · api-tester · e2e-tester · mobile-tester · web-tester · code-reviewer · bug-triager · security-engineer · devops-engineer · tech-writer. Profiles: `max`, `balanced`, `economy`. Details: `reference/roles.md`.

This is the OpenCode port of [claude-agent-team](https://github.com/itsaraphapthanatka/claude-agent-team). Everything is rendered into OpenCode V2 formats: `mode: subagent` agents, ordered `permissions` instead of `tools:`, `provider/model#variant` model IDs, and `question` / `subagent` / `shell` tool names. No Claude Code runtime is required.

## Install (pick one)

**A. As a global skill (simplest)** — available in every project on that machine:

```sh
git clone https://github.com/itsaraphapthanatka/opencode-agent-team.git ~/.config/opencode/skills/agent-team
```

The directory name is the skill ID, so keep it `agent-team`. OpenCode also reads `~/.claude/skills` for compatibility, but prefer the OpenCode path.

**B. As a project skill** — committed with the project, so the whole team shares it:

```sh
git clone https://github.com/itsaraphapthanatka/opencode-agent-team.git .opencode/skills/agent-team
```

**C. Point OpenCode at a clone** — add the *parent* directory to your config. V2 uses a `skills` array; V1 uses `skills.paths`:

```jsonc
{ "$schema": "https://opencode.ai/config.json", "skills": ["~/Documents/project"] }
```

```jsonc
{ "$schema": "https://opencode.ai/config.json", "skills": { "paths": ["~/Documents/project"] } }
```

The skill ID is the folder name (`opencode-agent-team` here), so use `@opencode-agent-team`, or rename the folder to `agent-team`.

Then open the target project in OpenCode and say:

```text
@agent-team init
```

or just “สร้างทีม agent ให้โปรเจกต์นี้” — the skill advertises itself on those triggers.

**Optional `/agent-team` command.** OpenCode only discovers commands in `commands/` directories, not inside a skill. Copy the bundled wrapper to get `/agent-team init | add <role> | status | upgrade all`:

```sh
cp ~/.config/opencode/skills/agent-team/extras/commands/agent-team.md ~/.config/opencode/commands/agent-team.md
```

## Update

```sh
cd ~/.config/opencode/skills/agent-team && git pull
```

Projects already bootstrapped keep their generated files; use `/agent-team upgrade <role>` to re-render one role, or `/agent-team upgrade all` for every role plus the pipeline commands (a `.bak` is kept). Neither touches the hand-filled docs — only an explicit `render.py --scope docs` rewrites those.

## Layout

```
SKILL.md                  entry point (init | add | status | upgrade)
scripts/render.py         deterministic renderer + frontmatter checker (--check)
templates/agents/*.md     17 role templates ({{PLACEHOLDERS}}), OpenCode frontmatter
templates/commands/*.md   10 pipeline commands
templates/docs/           context file, team chart, learnings, backlog templates
templates/partials/       shared expert protocol
reference/roles.md        roles, profiles, permission mapping, config schema
extras/commands/          optional /agent-team command wrapper
tests/                    renderer regression tests
```

## How the port maps to OpenCode

| Claude Code | OpenCode |
|---|---|
| `.claude/agents/*.md` + `tools:` + `model:` + `effort:` | `.opencode/agents/*.md` + `mode: subagent` + `permissions:` + `model: provider/model#variant` |
| `.claude/commands/*.md` + `argument-hint:` | `.opencode/commands/*.md` (body is the prompt, `$ARGUMENTS` still works) |
| `AskUserQuestion` | `question` tool |
| Agent tool / `subagent_type` | `subagent` tool (`agent`, `description`, `prompt`, `background`) |
| Bash tool | `shell` tool |
| `memory: project` | `.opencode/agent-memory/<role>/` read/written by the agent itself |
| `skills:` frontmatter | skills referenced in the body, loaded with the `skill` tool |
| plugin marketplace | clone into `~/.config/opencode/skills/` (or a `skills` config entry) |

### If you are still on OpenCode V1

V1 ignores the V2 `permissions` list (unknown fields land in `options`), so the code-reviewer could edit files and testers could fetch the web. Set `"compat_v1": true` in `.opencode/agent-team.json` and re-render: the renderer adds the legacy `permission:` map, including the per-pattern `edit` object, so the same guarantees hold (read-only reviewer, docs-only writers, no web for testers). V2 ignores it, so leave the flag off once you upgrade. The skill sets it automatically when `opencode --version` reports a 1.x build.


## Model selection

OpenCode model IDs are `provider/model` with an optional `#variant` for effort. By default the renderer **omits** the model so every subagent inherits the session model — that works with any provider. To tier models, add a `models` map to `.opencode/agent-team.json`:

```json
{
  "profile": "balanced",
  "models": {
    "heavy": "anthropic/claude-opus-4-5#high",
    "other": "anthropic/claude-sonnet-4-5#high",
    "light": "anthropic/claude-haiku-4-5#high"
  }
}
```

Use exactly the IDs `opencode models` reports. Per-role override: `"overrides": {"code-reviewer": {"model": "anthropic/claude-opus-4-5#max"}}`.

## Optional skills the team picks up

Roles reference a skill only when it exists on the machine (OpenCode's `~/.config/opencode/skills` and `.opencode/skills`, plus the `~/.claude/skills` / `.agents/skills` compatibility roots); otherwise the reference degrades to a no-op.

| skill | roles | install |
| --- | --- | --- |
| [impeccable](https://impeccable.style/) | ux-designer, ui-designer, web-dev, mobile-dev | `npx impeccable install` |
| scrutinize | architect, code-reviewer | — |
| debug-mantra | backend-dev, mobile-dev, web-dev, bug-triager | — |
| post-mortem | tech-writer | — |

With `impeccable` installed, designers run its `audit` / `critique` / `shape` before writing a spec and front-end devs run `polish` on user-visible changes; its `DESIGN.md` and the ui-designer's `DESIGN-SYSTEM.md` are reconciled rather than kept as two sources of truth.

## Moving a generated team to another machine

The team lives in the project's `.opencode/` (agents, commands, `agent-team.json`, `agent-memory/`) and its docs folder — commit both. Generated paths are relative to the project root, so cloning the repo(s) in the same folder layout is all that is needed; the context file documents the required layout.

## ภาษาไทย

ติดตั้งบนเครื่องใหม่: `git clone https://github.com/itsaraphapthanatka/opencode-agent-team.git ~/.config/opencode/skills/agent-team` แล้วเปิดโปรเจกต์ใน OpenCode พิมพ์ `@agent-team init` (หรือบอกว่า “สร้างทีม agent ให้โปรเจกต์นี้”) ตอบคำถาม 4 ข้อ ระบบจะสำรวจโค้ดจริงและสร้างทีมให้ ทีมที่สร้างแล้วอยู่ใน `.opencode/` ของโปรเจกต์ commit ไปกับ repo ได้เลย — OpenCode โหลด agent/command ใหม่อัตโนมัติ ไม่ต้อง restart (ถ้าไม่เห็นให้สั่ง `/reload`)

หมายเหตุ: ค่าเริ่มต้นคือให้ทุก subagent ใช้โมเดลเดียวกับ session (ไม่ระบุ `model`) จึงใช้ได้กับ provider ใดก็ได้ ถ้าต้องการแบ่งโมเดลตาม profile ให้ใส่ `models` ใน `.opencode/agent-team.json`
