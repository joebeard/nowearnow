# nowearnow

Privacy-first lost-property labels for families. Django REST Framework + React/TypeScript.
Domain: **nowearnow.com**. This is a working local prototype, not a production deployment.

## Run locally

Prerequisites: Python 3.12, uv, Node.js 24/npm and Make.

```sh
cd /home/jbeard/git/nowearnow
make setup
make backend
# Another terminal, from the repository root:
make frontend
```

Open http://127.0.0.1:5173. Register or log in, then:

1. Add a child, adult or family profile.
2. Create objects under that profile: a specific item (laptop/calculator) or a reusable
   group (clothing/general belongings). Each object gets one stable QR.
3. Optionally add printed text and separately opt into online scan-page text.
4. In **Build your label sheets**, choose a quantity for each object across all profiles.
5. Preview the mixed sheet, then **Print / save PDF**.

Example: 1 laptop + 1 calculator + 4 clothing labels for one child + 4 for another =
10 labels on one sheet. Copies of one object share its QR. Reprinting or renaming the
object does not create a new code. **Make a sample QR** creates a sample object and
selects one copy; press **Preview sheets** to see its QR.

The private profile/object names, printed text and scan-page text are separate.
Printed text is optional. Online disclosure defaults off, even when a name is printed.

Sheets hold 18 labels (3 × 6, 60 × 40 mm); larger runs automatically split over pages.
Choose A4/Letter and up to 180 labels per run. Print quantities are transient page state,
not saved templates. Disabled/inaccessible objects cannot be added to a sheet preview.
Use full-sheet adhesive paper, print at 100% with browser headers/footers off, and cut
out. Pre-cut sticker-stock presets are not implemented. Browser Print / Save PDF uses
the browser's print dialog; use a regular browser if your embedded browser does not
expose printing. A physical printer test is still needed.

A finder opens `/s/<uuid>` without an account and submits a message. The guardians'
inbox shows it. Scanning alone does not send a notification.

## Email and shared guardians

No external mail is sent by default. Verification and invitation emails are saved
under the gitignored `backend/dev-emails/` folder. Open the latest file locally and
follow its link in the same browser where the intended account is logged in.
Verification links expire in 24 hours; invitations in 48 hours.

After verification, enable **Email me when something is found** for each relevant
profile. The profile creator can invite a co-guardian, who must accept while logged
into an account with the invited, verified email. A co-guardian sees only that profile
and reports submitted after joining. Each guardian chooses their own alerts.

Reports enqueue one delivery per guardian; deliver pending notifications with:

```sh
make notifications
```

Run again to retry failures (up to five attempts). This prototype command is a
single-worker, manual dispatcher; production scheduling/worker infrastructure is
not configured. The inbox works even without an email worker. Alerts contain only
a generic prompt to log in, never finder messages, child names or contact lists.

To send real email, export the SMTP variables documented in `.env.example` and restart
Django. Choose and configure your provider and domain authentication separately.
Do not commit credentials. Twilio/SMS is deferred; see `docs/EMAIL.md`.

## Django admin

Open http://127.0.0.1:8000/admin/ (also proxied through `/admin/` on the frontend).
The development database has the user-requested `admin` superuser. Its password was
provided in the task; credentials are not stored in source or migrations.
For another installation, create an account interactively:

```sh
uv run python backend/manage.py createsuperuser
```

Admin manages users/groups, profiles, guardian grants, objects (Items) and labels, and provides
read-only views of invitations, reports and deliveries. Assign staff model permissions
by role. Do not grant user/group administration to routine support staff: Django user
management can grant powerful privileges. Staff flag alone does not grant model access.
Creating an item in admin automatically creates its private label.
Labels/items/grants cannot be reassigned through admin after creation, to avoid moving
message history to another family. Changes use Django's standard admin audit log.
Support should only change disclosure with guardian authorization.

## Test a QR from a phone

Loopback URLs only work on the computer. On a trusted development network, replace
`192.168.1.10` below with this computer's actual LAN IP:

```sh
PUBLIC_BASE_URL=http://192.168.1.10:5173 DJANGO_ALLOWED_HOSTS=192.168.1.10 make backend
# Another terminal:
cd frontend
npm run dev -- --host 0.0.0.0
```

Use the same Wi-Fi and open the LAN URL. Reprint after changing PUBLIC_BASE_URL;
previously printed URLs do not change. Development settings trust the explicitly
configured public origin for CSRF. Use synthetic data over this HTTP development setup.
Nothing has been deployed to the registered domain.

## Checks and context

`make check` runs Ruff, Django system checks, migration drift, backend tests, TypeScript
checks and a Vite production build. CI uses the same checks. Lockfiles are checked in
as project files (the repository has not yet been committed).

- `backend/`: accounts, labels/permissions/returns, email delivery, admin, configuration.
- `frontend/`: mobile-first app, finder form and printable SVG QR labels.
- `docs/`: requirements, architecture, privacy boundaries, API, decisions and status.

Codex reads `AGENTS.md` on starting in this repository. `CLAUDE.md` imports it.
Open this folder as a Codex project and read `docs/STATUS.md` to resume.
Local settings use SQLite. WSGI/ASGI default to production settings, which deliberately
refuse startup until deployment is configured. No `.env` file is automatically loaded.

See `docs/STATUS.md` for remaining work and `docs/PRIVACY.md` for release gates.
