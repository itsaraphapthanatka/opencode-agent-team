# {{PROJECT}} — system context for the agent team

Single source of truth for every agent in `{{PROJECT_ROOT}}/.opencode/agents/`. Read this before touching any repo. Facts were verified on {{DATE}}; when you find one that is wrong, fix it here (tech-writer owns this file, anyone may correct a fact).

## Product in one paragraph
TODO — what the product does, who its users/roles are, the core entity and its state machine (e.g. `pending → accepted → completed | cancelled`), where money or personal data moves, languages/markets.

## Repos
| Repo | Path | Stack | Verified checks |
|---|---|---|---|
{{REPO_TABLE}}

Owner(s): TODO (from `git shortlog -sne`). Default branch: TODO. Shared docs: `{{DOCS_DIR}}` (`product/` PRD + BACKLOG, `adr/`, `design/`, `tickets/`, `runbooks/`, `qa/`, `releases/`).

## Architecture map
TODO per repo — entry point, layers (e.g. routers → services → models → schemas), route prefixes or page routes, auth pattern (how the current user is resolved and how roles are checked), state/data layer, i18n, background jobs, external services (maps, payments, SMS, push).

## Environments
- **Production**: TODO URLs. **Agents never call, deploy to, or migrate production.**
- **Local dev**: TODO (compose services, ports, what is usually running).
- **Isolated test recipe** (what testers and devs use; must not touch dev or prod data):
  ```bash
  TODO — e.g. temporary database on a free port, in-process test client, seeded fixtures; include teardown
  ```
  Port allocation for temporary services: TODO (e.g. 55433 api-tester, 55434 e2e-tester, 55440+ devs, 55445 bug-triager, 55450 security-engineer, 55460 architect spikes).

## Conventions for the team
- {{LANG_RULE}} Code comments and commit messages in English.
- Never `git add/commit/push/stash/checkout/reset` unless the user explicitly asks in that turn. Never edit `.env*`, never print secret values, never add secrets to tracked files.
- TODO — project rules devs must follow (auth on every endpoint, ownership checks, i18n for every string, schema change = migration + test, shared code kept in sync, error format).
- Documents: PRD `{{DOCS_DIR}}/product/PRD-<slug>.md`, ADR `{{DOCS_DIR}}/adr/ADR-NNN-<slug>.md`, tickets `{{DOCS_DIR}}/tickets/BUG-NNN-<slug>.md`, runbooks `{{DOCS_DIR}}/runbooks/`, release notes `{{DOCS_DIR}}/releases/`, backlog `{{BACKLOG_PATH}}`, team chart `{{TEAM_PATH}}`, lessons `{{LEARNINGS_PATH}}`.

## Known state / hygiene red flags
TODO — vendored dependencies or secrets tracked in git, broken migrations, unpinned deps, services not installed locally, failing checks found during bootstrap.

## Baseline
TODO — link the latest QA report (`{{DOCS_DIR}}/qa/`) and summarise verdict, blockers, what passed, what was not tested.
