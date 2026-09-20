# ADR 0001: Initial foundation

Date: 2026-09-20. Status: accepted scaffold; provisional choices identified below.

User requirements: Django/Python + React, mobile first, future app potential,
parent-controlled disclosure with private defaults, durable repository context.

Decision: monorepo; Django REST Framework API `/api/v1/`; React/TypeScript/Vite;
Django 5.2 LTS with Python 3.12; custom adult user model before first migration.
Use AGENTS.md as canonical agent guidance, CLAUDE.md as an import, docs/STATUS.md
for handoff, and numbered ADRs for decisions.

Provisional implementation choices: same-origin browser sessions with CSRF, SQLite
locally and PostgreSQL planned for deployment, uv/npm lockfiles. These reduce local
setup work and keep the API independent from a possible future native application.
No hosting, payment, fulfilment or messaging provider is selected.

Consequences: mobile applications can reuse API contracts but need a separate auth
decision. Deployment/database work remains. Parent contact relay is the proposed
private return mechanism; no public personal fields are enabled or implemented.
Changing a privacy requirement requires explicit discussion and an updated decision,
not an incidental serializer or UI change.

Follow-up: ADR 0002 refines the domain around shared guardianship and confirms the
finder message form and multi-guardian alerts. Consult it before implementing access.
