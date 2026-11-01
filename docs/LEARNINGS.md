# opencode-agent-team team learnings

System-level lessons every agent must know. Read before starting; **append a dated bullet whenever something cost you time** — not facts (those go in `PROJECT-CONTEXT.md`) but "what to check first next time".

## 2026-11-01 — bootstrap
- Windows CI จงใจไม่มี `PYTHONUTF8` — ถ้า test encoding พัง ให้เช็คก่อนว่า reproduce ได้บน windows-latest ด้วยหรือไม่ อย่าเพิ่งแก้ฝั่งโค้ด
- ไม่มี pyproject.toml/requirements.txt โดยเจตนา (stdlib-only) — ก่อนเสนอเครื่องมือ dev ใหม่ (ruff/mypy/pytest) ให้คิดถึง rule นี้ก่อน
