# Roles, profiles, config schema (OpenCode)

## Roles (`templates/agents/<role>.md`)
| role | category | when to include | edit access | web |
|---|---|---|---|---|
| product-manager | think | always | repo code | yes |
| architect | think | always | repo code + spikes | yes |
| ux-designer | think | any UI | docs + own memory | yes |
| ui-designer | think | any UI (design system, component specs, visual QA) | docs + own memory | yes |
| backend-dev | build | server code | repo code | yes |
| mobile-dev | build | RN/Expo/Flutter/native | repo code | yes |
| web-dev | build | web front-end | repo code | yes |
| devops-engineer | build | always (CI/Docker/deploy) | repo code | yes |
| test-engineer | build | always | repo code | yes |
| api-tester | adversarial | server code | docs + own memory | no |
| e2e-tester | adversarial | server + clients | docs + own memory | no |
| mobile-tester | adversarial | mobile stack | docs + own memory | no |
| web-tester | adversarial | web front-end | docs + own memory | no |
| code-reviewer | adversarial | always | none (read-only) | no |
| bug-triager | adversarial | always | docs + own memory | yes |
| security-engineer | adversarial | always (money/PII → mandatory) | docs + own memory | yes |
| tech-writer | think | always | repo code | yes |

Heavy roles (get the top effort tier in every profile): architect, security-engineer, code-reviewer, backend-dev, e2e-tester.

Edit access becomes OpenCode permission rules in the agent frontmatter: repo writers get no `edit` restriction, docs-only roles get `edit * deny` followed by an allow for the docs folder and their own memory, and the code-reviewer gets no edit at all. Roles without web tools get `webfetch`/`websearch` denied. Every generated subagent also denies the `subagent` action, since OpenCode subagents cannot nest anyway.

## Profiles
A profile picks the effort tier per role. OpenCode expresses effort as a model variant (`provider/model#variant`), so a profile only changes the model when the config supplies tier models.

| profile | heavy tier | other tier | light tier |
|---|---|---|---|
| max | max | xhigh | xhigh |
| balanced | high | high | high |
| economy | medium | medium | medium |

Light roles: mobile-tester, web-tester, tech-writer. Everything not heavy is "other".

Model resolution per role, first match wins:
1. `overrides.<role>.model`
2. `models.<tier>`
3. top-level `model`
4. none → the subagent inherits the session model (recommended default; works with any provider)

Per-role override: `"overrides": {"code-reviewer": {"model": "anthropic/claude-sonnet-4-5#high"}}`.

## Default skills (loaded with the `skill` tool, only when installed)
architect, code-reviewer → scrutinize · backend-dev, bug-triager → debug-mantra · mobile-dev, web-dev → debug-mantra + impeccable · ux-designer, ui-designer → artifact-design + impeccable · tech-writer → post-mortem

The renderer checks OpenCode's skill roots — `~/.config/opencode/skills`, `.opencode/skills`, plus the compatibility roots `~/.claude/skills`, `.claude/skills`, `~/.agents/skills`, `.agents/skills` — and drops any skill that is not there. OpenCode has no per-agent skill preload, so a skill is referenced in the agent body and loaded on demand.

`impeccable` ([impeccable.style](https://impeccable.style/)) is the design-craft skill: designers use `audit`/`critique`/`shape`, front-end devs use `polish` on user-visible changes. Absent on the machine, every reference to it degrades to a no-op.

## Config schema (`.opencode/agent-team.json`)
```json
{
  "project": "PetGo",
  "project_root": "/abs/path/to/main/repo",
  "docs_dir": "/abs/path/to/docs",
  "report_language": "Thai",
  "context_file": "PROJECT-CONTEXT.md",
  "absolute_paths": false,
  "profile": "balanced",
  "compat_v1": false,
  "roles": ["product-manager", "architect", "..."],
  "models": {
    "heavy": "anthropic/claude-opus-4-5#high",
    "other": "anthropic/claude-sonnet-4-5#high",
    "light": "anthropic/claude-haiku-4-5#high"
  },
  "repos": [
    {"name": "Backend API", "path": "/abs/path", "stack": "FastAPI 0.123, Postgres", "checks": ["venv/bin/pytest -q tests/"], "run": "venv/bin/uvicorn app.main:app --reload"}
  ],
  "specifics": {"backend-dev": "Layered layout: app/routers → app/crud → app/models → app/schemas. ..."},
  "overrides": {"code-reviewer": {"model": "anthropic/claude-opus-4-5#max"}},
  "skills": {"tech-writer": ["post-mortem"]}
}
```

`models` and `model` are optional. Omit both to inherit the session model. Model IDs must be exactly what `opencode models` reports — the renderer only checks the `provider/model[#variant]` shape.

`compat_v1` is for installs that still run the V1 runner (a 1.x `opencode --version`). V1 ignores V2 `permissions` and routes unknown fields into `options`, so the renderer can additionally emit the legacy `permission:` map — including the per-pattern `edit` object — which V1 enforces. Leave it off on V2.

## Portability
Generated agents reference paths relative to `project_root` (docs, other repos, `.opencode/agent-memory`) so the same `.opencode/` works on any machine that clones the repos in the same layout. Set `"absolute_paths": true` only for single-machine setups. Permission rules use Location-relative paths for the same reason; a docs folder outside the project root is emitted as an absolute path because permission patterns cannot express `..`.
