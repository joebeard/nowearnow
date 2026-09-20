# Architecture

## Confirmed requirements
Django/Python API + React; mobile-first; nowearnow.com; local root
/home/jbeard/git/nowearnow. Private defaults and parent-controlled disclosure.
Many guardians per child and many children per guardian, including blended families.
Generic child/adult/family labels and item-specific labels; opaque UUID QR links.
Optional human-readable printed names/text with playful nowearnow branding.
Scan page with approved information and a finder message form; multi-guardian alerts.
Django built-in administration. Email first; Twilio/SMS secondary.

## Implemented stack
Monorepo: Django 5.2 LTS/DRF with Python 3.12, React/TypeScript/Vite. uv and npm
lockfiles pin resolved versions. SQLite for local development; PostgreSQL intended
for deployment but not configured. qrcode generates SVGs on the server.

Browser API requests use relative `/api/v1/` URLs via Vite's proxy. Django sessions
and CSRF protect login, registration, mutations and anonymous report submission.
Development explicitly trusts the local Vite origins; never allow arbitrary origins.
Admin uses same-origin referrers for native form CSRF; scan/API responses use no-referrer.
Production should serve frontend/API under one origin. Native-app auth is undecided.

## Object model
- `accounts.User`: independent adult account, case-insensitive unique non-empty email,
  email_verified flag. Child profiles do not have logins.
- `Profile`: UUID, kind child/adult/family, private dashboard name. A family is itself
  a label target, not an implicit access boundary for child profiles.
- `Access`: explicit user/profile grant, active state, controller flag, opted-in email
  alerts and join timestamp. One active controller per profile. Partner relationships
  do not confer other profile access.
- `Invitation`: recipient email bound to verified account, expires after 48 hours,
  single-use acceptance. Private profile details are not included in invitation email.
- `Item` (object in the UI): UUID, profile, private name and kind (specific item or
  reusable group). Clothing/general belongings are group objects. Every object
  created through the app or admin gets one canonical Label.
- `Label`: UUID management ID, separate random UUIDv4 scan token, profile, one-to-one item,
  printed text, public text, explicit sharing switch and active flag. Item/profile
  consistency validated by the model. Label assignment is immutable through APIs/admin.
- `Report`: UUID, label, bounded finder message and per-label submission UUID for retry
  deduplication. No account needed to submit. A page view does not create a report.
- `Delivery`: per-report/per-grant recipient snapshot and delivery state. Inbox queries
  require current access and a report date after the grant's latest join date.

Public responses contain only explicitly allowed public text. Private/printed text,
profile IDs, item names and contact addresses are never serialized on the scan API.
Print QR SVG endpoints require profile access. The payload is configured PUBLIC_BASE_URL
plus `/s/<UUID>`, not a request-host-derived URL or any personal information.

## Provisional access policy
The profile creator is the disclosure/access controller. Invited guardians can create
private labels, edit printed text, view new messages and restrict disclosure/disable
labels. Only the controller can enable or change public scan text and invite/remove
other guardians. Controller changes must be handled by authorized site management.
This deliberately small role model requires product review before launch; it is not a
claim that an invitation establishes legal guardianship. See ADR 0003.

## Email and administration
Django file email backend for development; configurable SMTP. Found-item delivery is
an explicit management command, one worker, with five-attempt retries and access checks
at dispatch. Production needs durable scheduling, backoff and provider-level idempotency.
Django admin uses staff/model permissions; no automatic account backdoor is seeded.
The requested development superuser exists only in the ignored local database.

## References
- https://docs.djangoproject.com/en/5.2/topics/email/
- https://docs.djangoproject.com/en/5.2/howto/csrf/
- https://www.django-rest-framework.org/api-guide/permissions/
- https://pypi.org/project/qrcode/

## Object-first printing (ADR 0004)
Create and name objects first; quantities belong to a print run, not object identity.
The sheet builder combines all currently accessible profiles, validates each object
server-side, and expands quantities into ordered pages of 18. It neither creates new
objects nor rotates QR codes. UI changes invalidate an existing preview; QR downloads
also recheck access. Object names and printed text remain separate from public text.
Legacy generic labels were attached to group objects by a data migration without
changing IDs, scan tokens, reports or notification grants.
