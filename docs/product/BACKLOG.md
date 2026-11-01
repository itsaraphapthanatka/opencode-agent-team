# opencode-agent-team backlog

Ordered by what to do next · owner = agent role · source = QA report / ticket / PRD

## P0 — users blocked, money or data at risk
| # | Item | Owner | Notes |
|---|---|---|---|
| — | (ว่าง — ไม่มี blocker) | | |

## P1 — wrong behaviour
| # | Item | Owner | Notes |
|---|---|---|---|

## P2 — quality, debt, docs
| # | Item | Owner | Notes |
|---|---|---|---|
| 1 | เพิ่ม LICENSE file (repo open source บน GitHub แต่ยังไม่มี license) | product-manager | ตัดสินใจ MIT หรือ Apache-2.0 |
| 2 | push ขึ้น origin ครั้งแรก + ดูผล CI จริง (ubuntu+windows matrix ยังไม่เคยรัน) | devops-engineer | `git push -u origin main` |
| 3 | เพิ่ม lint/typecheck (ruff/mypy) — ตอนนี้ไม่มีเลย ทั้งในเครื่องและ CI | test-engineer | ขัด rule stdlib-only ถ้าจะเพิ่มต้องขอ user ก่อน |

## Ideas (not yet assessed)
- add via `/prd <idea>`; product-manager prioritises
