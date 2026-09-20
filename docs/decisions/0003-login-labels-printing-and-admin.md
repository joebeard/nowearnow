# ADR 0003: Working local label and return flow

Date: 2026-09-20. Status: implemented local milestone; role/deployment choices provisional.

User requirements: login, sample QR, printable sheets, generic child/adult/family or
specific item labels, UUID-based non-PII QR payloads, backend-controlled scan display
and notifications, email integration, Django admin and optional printed names with
fun branding. Twilio/SMS is secondary. A local admin superuser was explicitly requested;
it is created only in the ignored development database, not source or migrations.

Decisions:
- Generalize the per-child model to Profile(kind child/adult/family), with explicit
  Access grants. Family profiles do not automatically include children or partners.
- Item is optional; Label has a separate UUIDv4 scan token and management UUID.
  UUIDv4 has 122 random bits (128 total), replacing the earlier tentative 128-random-bit
  threshold to meet the user's UUID request. Tokens confer only limited scan capability.
- Distinguish private name, optional printed text, and explicitly opted-in public text.
  Nothing printed becomes public online automatically; both texts default blank/hidden.
- Server-generated SVG QRs include a white quiet zone. 18-up A4/Letter cut-out labels,
  60 × 40 mm, with repeated codes, custom text and native CSS nowearnow branding.
- Register/login with Django sessions and CSRF. Email verification is required for
  invitations and email alert opt-ins, but users can create labels before verification.
- Profile creator controls invitations and broader disclosure. Invited guardians
  manage labels/new reports and may restrict disclosure, but cannot broaden it.
  One active controller; no automatic controller transfer. This is a provisional
  product authority model; resolve disputes/controller succession before launch.
- Recipient-bound invitations expire; rejoining starts a new history boundary.
  Report submissions create per-guardian delivery snapshots. Email defaults off.
- Django file email backend locally, SMTP configuration available, manually run
  single-worker dispatcher. Twilio deferred. SMTP crash duplicates are a documented limit.
- Django admin with staff/model permissions, immutable existing assignments, read-only
  reports/deliveries and audit logs. Admin forms use same-origin referrers; public scans
  retain no-referrer. Do not trust Origin:null or disable CSRF to make forms work.

Consequences: runnable local end-to-end flow, but not production-ready. Registration
has no password recovery yet. Native authentication, production hosting/PostgreSQL,
durable jobs/abuse control, legal/privacy review, retention and stock-specific print
presets remain. Printed PII requires physical reprinting to change; online text can be hidden.

Follow-up: ADR 0004 replaces optional item linkage with first-class objects and
mixed-quantity sheet building, preserving existing QR codes.
