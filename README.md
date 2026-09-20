# nowearnow

Privacy-first lost-property QR stickers and clothing labels for families.
Domain: **nowearnow.com**. This repository is an initial development scaffold.

## Run locally

Prerequisites: Python 3.12, uv, Node.js 24 and npm, and Make.

```sh
cd /home/jbeard/git/nowearnow
make setup
make backend
# In a second terminal, from the repository root:
make frontend
```

Open http://127.0.0.1:5173. Vite proxies `/api` to Django on port 8000.
`GET /api/v1/health/` returns `{"status":"ok"}` (liveness only; no database probe).
`make check` runs Python lint/format, Django checks, migration drift, API boundary
tests, TypeScript checks and the frontend production build.

Local development explicitly uses development settings and SQLite. No `.env` file
is required or automatically loaded; export environment variables in your shell if
needed. `.env.example` documents the convention. WSGI/ASGI entry points default to
production settings, which deliberately refuse startup until deployment is designed.
Do not use `runserver` or the Vite server in production.

## Layout

- `backend/`: Django configuration, custom adult user model, minimal REST health API.
- `frontend/`: React/TypeScript/Vite, responsive development landing page.
- `docs/`: product requirements, architecture, privacy requirements, status, and decision records.
- `.github/workflows/ci.yml`: checks ready for a future GitHub remote.

## Working with coding agents

Codex reads `AGENTS.md` automatically when a task starts in this repository.
Open this folder as a Codex project and start subsequent tasks there. Ask it to read
`docs/STATUS.md` when resuming work. Existing projectless tasks should not be assumed
to reload instructions merely because files were created elsewhere.
`CLAUDE.md` imports the same instructions for Claude Code; avoid duplicate policies.

See the [official Codex guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Scope

No registration, label generation, scan routes, disclosure preferences, messaging,
checkout, print fulfilment, or deployment exists yet. The page is an honest placeholder.
No secrets or real family records are included. Production readiness is tracked in
[privacy requirements](docs/PRIVACY.md) and [current status](docs/STATUS.md).
