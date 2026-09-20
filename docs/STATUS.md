# Current project status

Updated: 2026-09-20.

## Implemented locally
- Registration/login/logout with Django sessions, password validation, CSRF and throttling.
- Email verification, recipient-bound co-guardian invitations, access revocation and
  per-profile opted-in alerts. Custom adult user model; case-insensitive unique email.
- Child/adult/family Profile, Access, first-class Item (specific/group), one-to-one Label,
  Report and Delivery models. Existing generic labels migrated with QR tokens preserved.
- Sample QR creation; generic/item-specific labels; separate UUID scan token containing
  no PII; private-by-default online text; optional human-readable printed names/text.
- Object creation/renaming, editable printed/online text, disable/hide controls.
- Mixed-quantity branded 18-up A4/Letter sheets across profiles, automatic pagination
  and a server-validated preview (up to 180 labels). Quantities are not persisted.
- Public scan page and finder message form; private guardian inbox and idempotent reports.
- Configurable SMTP email integration with file delivery as the local default. Explicit
  `make notifications` worker checks current permission and retries recipient failures.
- Django admin for site management. User-requested local `admin` superuser created in
  the ignored database; no test credentials are seeded by source or migrations.
- Documentation, migrations, lockfiles and CI/check commands updated.

## Validation
- `make check` passed: Ruff, formatting, Django system/migration checks, 35 backend tests,
  TypeScript and production frontend build. Migrations applied to the local database.
- Backend tests cover auth/CSRF, verification, guardian isolation/invitations/revocation,
  disclosure, idempotent reports, multi-recipient delivery/retries, admin permissions,
  object/QR identity, mixed 1/1/4/4 sheets, pagination and invalid selections.
- Browser verified login, sample QR, optional printed text, hidden scan text, finder
  submission/inbox, real local admin login, object creation and a 10-label mixed preview
  across a family and two synthetic children.
- Generated SVG was rasterized and decoded successfully to its exact UUID scan URL,
  with no printed/public text embedded. Temporary QA libraries were not added to runtime.
- Desktop preview visually inspected. Embedded browser viewport overrides did not take
  effect, so mobile device QA remains unverified. Physical printing is unverified.

## Next work / release gates
- Product review of controller authority, custody/disputes, guardian removal/succession.
- Account recovery, email change/reverification and full account/profile lifecycle.
- Production PostgreSQL, hosting/HTTPS/secrets, shared rate limits (including admin),
  queue supervision/backoff/provider idempotency, proxy log redaction and security review.
- Decide jurisdiction/data region, retention/deletion/export, staff support access,
  processors, privacy obligations and school involvement before real family data.
- Select SMTP provider/domain authentication; Twilio/SMS remains deferred.
- Test physical printer/scanner output and add pre-cut label-stock presets if desired.
- Commerce, ordering, label claims for purchased stock and fulfilment remain future work.

## Local notes
No deployment to nowearnow.com, Git remote or commit. Production settings deliberately
refuse startup. Existing frontend/backend local processes were already running and
were left in place. Use README.md for setup, phone scanning, print and email instructions.

Synthetic local test data: the admin account has sample family/child profiles and
objects used to verify mixed sheets. No real child data was entered. A separate QA
account used for finder-flow verification is now inactive with an unusable password.
