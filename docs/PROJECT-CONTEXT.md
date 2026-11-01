# opencode-agent-team — system context for the agent team

Single source of truth for every agent in `./.opencode/agents/`. Read this before touching any repo. Facts were verified on 2026-11-01; when you find one that is wrong, fix it here (tech-writer owns this file, anyone may correct a fact).

## Product in one paragraph
`opencode-agent-team` คือ CLI code generator ที่ port มาจาก `claude-agent-team` ของ Claude Code ให้ทำงานกับ OpenCode — ทำงานโดยอ่าน `.opencode/agent-team.json` (config) + `templates/` (markdown + YAML frontmatter) แล้วเขียน agent definitions (`.opencode/agents/*.md`, `mode: subagent`), slash commands (`.opencode/commands/*.md`), memory dirs (`.opencode/agent-memory/<role>/`) และเอกสารทีม (`docs/`: PROJECT-CONTEXT, TEAM, LEARNINGS, product/BACKLOG) ลงในโปรเจกต์ปลายทาง ผู้ใช้หลักคือ developer ที่ใช้ OpenCode (รองรับทั้ง V1 1.x และ V2) — ข้อจำกัดเดียวที่ออกแบบมาเพื่อแก้: V1 ไม่ enforce V2 `permissions:` จึงมี flag `compat_v1` ให้ renderer emit legacy `permission:` map ด้วย ไม่มี state ที่เปลี่ยนไปมาระหว่างรัน (ไม่มี entity state machine), ไม่มีเงินหรือ PII เกี่ยวข้อง, ไม่มี multi-tenant — เป็น pure function ของ config + templates

## Repos
| Repo | Path | Stack | Verified checks |
|---|---|---|---|
| Renderer | `.` | Python 3.14 stdlib-only (scripts/render.py 376 lines), unittest (tests/test_render.py 418 lines), templates/*.md, GitHub Actions CI | `python3 -m unittest discover -s tests` (47 tests, ~1.2s, ผ่าน — verified 2026-11-01) |

Owner(s): itsaraphap (itsaraphap.top@gmail.com) — single contributor, commit `ef1b33b` "Port claude-agent-team to OpenCode". Default branch: `main`. Remote: `https://github.com/itsaraphapthanatka/opencode-agent-team.git` (ยังไม่ได้ push). Shared docs: `docs` (`product/` PRD + BACKLOG, `adr/`, `design/`, `tickets/`, `runbooks/`, `qa/`, `releases/`).

## Architecture map
Entry point: `scripts/render.py` — single-file argparse CLI ไม่มี package/module แยกชั้น ไม่มี server, route, หรือ auth:

1. **อ่าน config** `.opencode/agent-team.json` — schema ทั้งหมดอยู่ใน `reference/roles.md` (project, project_root, docs_dir, report_language, profile, roles, repos, models?, compat_v1?, specifics?, overrides?)
2. **เลือกเทมเพลต** จาก `templates/agents/<role>.md`, `templates/commands/<name>.md`, `templates/docs/*`, `templates/partials/*` — partials ถูก compose เข้าตัว agent ตอน render (expert-protocol, protocol-think/build/adversarial)
3. **Substitute variables** (`{{LANG}}`, `{{DOCS_DIR}}`, `{{TESTERS}}` ฯลฯ) แล้วเขียนไฟล์ลง `AGENT_DIR`/`COMMAND_DIR`/`MEMORY_DIR`/`docs_dir` — ไม่เขียนทับไฟล์เดิมโดยไม่มี `--force`
4. **Frontmatter emit**: V2 เป็น `mode: subagent` + `permissions:` list; เมื่อ `compat_v1: true` จะ emit legacy `permission:` map เพิ่มให้ V1 enforce ได้ — ตรวจพบ V1 ผ่าน `opencode --version` (1.x)
5. **`--check`**: validate frontmatter ของไฟล์ที่เขียนแล้ว — ห้ามมี key ต้องห้าม (`argument-hint`, `allowed-tools`, `template`), model format ต้องตรง `provider/model[#variant]`, ตรวจ YAML hazards

Constraints สำคัญที่ห้ามลืม:
- OpenCode subagent **รันขนานกันไม่ได้และ spawn subagent ตัวอื่นไม่ได้** — coordination ทั้งหมดต้องอยู่ใน slash commands ที่ main session รัน ห้ามเขียน agent ที่ depend on การเรียก agent อื่น
- Rules ของ renderer: ห้ามเขียน secret ลงไฟล์ที่ generate (env var ชื่อเท่านั้น), ห้าม `git add/commit` ไฟล์ที่ generate โดยไม่บอกผู้ใช้, ใช้ของที่มีอยู่แล้วแทนการ duplicate
- `CODE_WRITERS` = product-manager, architect, backend-dev, mobile-dev, web-dev, devops-engineer, test-engineer, tech-writer; `NO_WRITE` = code-reviewer; ที่เหลือ docs+memory เท่านั้น

## Environments
- **Production**: ไม่มี — เป็น CLI tool ไม่มี service ให้ deploy **Agents never call, deploy to, or migrate production.**
- **Local dev**: `python3` 3.14.3 (ไม่มี venv, ไม่มี external deps — stdlib ล้วน) — ไม่มี service ต้องรัน
- **Isolated test recipe** (อะไรก็ตามที่แตะ repo ใช้สูตรนี้; ห้ามแตะไฟล์นอก temp dir):
  ```bash
  python3 -m unittest discover -s tests   # ~1.2s, tests เขียนลง temp dir เท่านั้น ไม่มี side effect ถาวร
  ```
  Port allocation สำหรับ temp services: ไม่จำเป็น — tests ไม่เปิด port (ใช้ temp dirs ผ่าน `tempfile`)

## Conventions for the team
- Reports and documents addressed to the owner are written in Thai; code identifiers, paths, commands, and HTTP details stay in English. Code comments and commit messages in English.
- Never `git add/commit/push/stash/checkout/reset` unless the user explicitly asks in that turn. Never edit `.env*`, never print secret values, never add secrets to tracked files.
- **Stdlib-only** — ห้ามเพิ่ม external dependency (ไม่มี pyproject.toml/requirements.txt โดยเจตนา) ถ้าจะเพิ่มต้องขอผู้ใช้ก่อนและเพิ่ม manifest ด้วย
- **ต้องทำงานบน Python 3.12 ด้วย** — เครื่อง dev เป็น 3.14 แต่ CI ใช้ 3.12 ห้ามใช้ syntax ใหม่กว่า 3.12
- **Encoding เป็นเรื่องจริงจัง**: CI จงใจไม่ตั้ง `PYTHONUTF8` — บั๊กที่ tests จับคือ Windows default encoding ห้ามแก้ test ให้ pass ด้วยการ hardcode `encoding=` และอย่าเพิ่ม `PYTHONUTF8` เข้า CI
- Templates ทุกไฟล์เป็น markdown + YAML frontmatter — command ห้ามมี `argument-hint`/`allowed-tools`/`template` keys
- Documents: PRD `docs/product/PRD-<slug>.md`, ADR `docs/adr/ADR-NNN-<slug>.md`, tickets `docs/tickets/BUG-NNN-<slug>.md`, runbooks `docs/runbooks/`, release notes `docs/releases/`, backlog `docs/product/BACKLOG.md`, team chart `docs/TEAM.md`, lessons `docs/LEARNINGS.md`.

## Known state / hygiene red flags
- **ไม่มี LICENSE file** — repo ตั้งใจ open source (GitHub) แต่ยังไม่มี license; ถ้าจะให้คนนอกใช้ต้องเพิ่ม (backlog แล้ว)
- **ยังไม่ได้ push ขึ้น origin** — remote ตั้งไว้ที่ `github.com/itsaraphapthanatka/opencode-agent-team.git` แต่ commit `ef1b33b` ยัง local อยู่
- ไม่มี lint/typecheck config (ruff/mypy ไม่ได้ติดตั้ง, ไม่มีใน CI) — style ขึ้นกับคนเขียน
- ไม่มี secrets tracked ใน git, ไม่มี `.env`, ไม่มี vendored deps, ไม่มี unpinned deps (ไม่มี deps เลย) — อื่น ๆ สะอาด
- Checks ทั้งหมด verified ผ่าน ณ วัน bootstrap (47/47 tests OK, CI workflow ถูกต้อง)

## Baseline
- ยังไม่มี QA report (`docs/qa/` ยังว่าง) — baseline ปัจจุบันคือ `python3 -m unittest discover -s tests` = **47 tests, OK, ~1.2s** (verified 2026-11-01)
- CI (`.github/workflows/test.yml`): matrix ubuntu-latest + windows-latest, Python 3.12, รัน `python -m unittest discover -s tests -v` — ไม่เคยรันบน origin จึงยังไม่รู้ผล CI จริง (ยังไม่ได้ push)
- คำสั่งที่ generate ไม่ได้เพราะไม่ตรง role set: `security-audit` (ต้องมี security-engineer), `test-all` (ต้องมี adversarial tester เช่น api-tester/e2e-tester) — เพิ่มได้ภายหลังด้วย `/agent-team add <role>` แล้ว re-render
