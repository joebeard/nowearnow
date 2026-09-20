# Architecture

## Confirmed requirements
- User-owned domain: nowearnow.com.
- Local root: /home/jbeard/git/nowearnow.
- Django/Python backend and React frontend; mobile-first, future app possible.
- Parents control exactly what scans disclose; defaults are the most private.
- Multiple guardians can manage multiple children across co-parenting and blended families.
- Found-item messages can alert multiple authorized guardians.
- A finder scan page includes approved information and a form to message guardians.
- See REQUIREMENTS.md for user journeys and acceptance criteria.

## Initial implementation choices
A monorepo contains Django REST Framework under `backend/` and React + TypeScript
with Vite under `frontend/`. Django 5.2 LTS and Python 3.12 are the conservative
baseline. Exact resolved versions are in uv.lock and frontend/package-lock.json.
SQLite supports zero-service local development. PostgreSQL is the intended deployed
database, pending deployment design; no production database adapter is configured.

The browser uses relative `/api/v1/` URLs. Vite proxies them during development;
a future production reverse proxy should serve React and Django under one origin.
This avoids unnecessary CORS and supports Django sessions with CSRF protection.
There is no login endpoint yet. Login itself must have explicit CSRF protection;
DRF's session checks alone do not protect anonymous login requests.
Native clients can reuse the API; native authentication remains a future decision.

A custom `accounts.User` extends AbstractUser before the first migration. It is for
adult account holders only. Registration, verification and parent authority are not
implemented. Do not interpret the model docstring as age verification.

## Planned domain boundaries (not implemented)
- Accounts: parent identity, verified contact channel, account lifecycle.
- Children and guardian grants: minimal private child records with explicit many-to-many
  adult access, invitation/acceptance, permissions and revocation. A shared child does
  not confer access to either guardian’s other children.
- Items and labels: child association, opaque scan token, activation and revocation;
  claim credentials separate from public scan credentials. Purchase ownership does
  not automatically determine who may manage a child or receive alerts.
- Disclosure: per-label explicit field allowlist, all hidden initially; child
  details minimized and separate from accounts.
- Returns: public approved-info page and finder message form; private relay and
  notification fan-out to eligible guardians, with per-recipient delivery state.
  Recheck active permissions before delivery and when viewing messages.
- Commerce: ordering and fulfilment, separately scoped from scan data.

Avoid creating speculative child fields or collecting data before its necessity is
agreed. API versions are a compatibility boundary, not permission to expose models.

## References
- https://www.djangoproject.com/download/
- https://www.django-rest-framework.org/api-guide/permissions/
- https://vite.dev/guide/
