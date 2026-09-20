# Privacy requirements and threat model

These are product/engineering requirements, not a claim of legal compliance.

## Default scan experience
A finder should be able to offer a return through a private relay without seeing
any child's identity, school/class, photograph, location, parent identity or contact
details. Do not collect these fields merely because they might be useful later.
The scan page must include generic return guidance, explicitly approved information
(if any), and a form to message the guardians. The form must remain usable when all
personal disclosure is disabled. The initial scaffold has no scan route or personal-data API.

Parents must explicitly enable each supported public field, with a preview of exactly
what an anonymous scanner sees. Settings must be enforced server-side for every
response. Never return hidden data to the browser. Missing settings, new fields and
unknown policy versions must fail closed. General acceptance of terms is not
field-level disclosure consent. The allowed field catalogue is still undecided.

Revoking disclosure must take effect on subsequent scans immediately. Explain that
previous viewers may have retained information; no system can retract screenshots.

## Threats and required controls before scan features ship
- Enumeration: use cryptographically random high-entropy tokens (at least 128 bits),
  no sequential identifiers, rate limits and uniform unavailable responses.
- Token leakage: treat printed tokens as public bearer capabilities with strictly
  limited scope. A copied label must never grant account or label management access.
  Redact tokens at proxy, application, error-reporting and analytics layers.
- Cross-family access: active per-child guardian grants and action checks for read/
  list/create/update/delete; server-controlled associations. Test unrelated guardians,
  shared children, non-shared siblings and revoked grants. Never infer access from
  marital status, address, email domain, or being a partner of an authorized guardian.
- Unwanted disclosure: dedicated public serializers with explicit allowlists;
  regression tests for every opt-in and combinations, plus unknown/new fields.
- Claiming printed labels: separate single-use activation credentials or a verified
  purchase association; a scan token alone cannot claim or transfer ownership.
- Revocation: disable lost/abused labels and rotate/reissue credentials; explain the
  implications for physical stickers. Test cached and revoked scan paths.
- Harassment/spam: bounded input, rate limits beyond process-local counters,
  reporting, blocking and abuse handling; no arbitrary finder HTML or attachments
  in the initial relay. Relay and additional disclosure are separate choices.
- Browser leakage: HTTPS, no-store, no-referrer, no third-party scripts/assets on
  scan pages, no search indexing. Robots directives are not access control.
- CSRF/session abuse: protected login and mutations, secure HttpOnly session cookies,
  CSRF tokens, account recovery and verified contacts before relay delivery.

## Data lifecycle and operations decisions still required
Before real family data: decide launch jurisdictions, hosting/data region, processors,
retention by data category, backup expiry, deletion/export, support access and audit
policy. Review applicable privacy obligations and whether a formal impact assessment
is needed. Do not retain IP/location history as an incidental scan analytics feature.

Before deployment: PostgreSQL configuration, HTTPS termination and trusted proxy
configuration, secure cookies/HSTS, CSP, logging redaction, production secret handling,
backup/restore tests, distributed abuse controls and Django deployment checks.
The current production settings intentionally refuse startup until this work is done.
Vite's static build does not inherit Django headers: configure the frontend host too.

## Current enforced controls
Authenticated-by-default DRF views; explicit public minimal health exception; JSON
rendering; Django CSRF middleware/session authentication; no-store and no-referrer
responses; noindex headers; no trackers; development isolated from production startup.
No claim is made that future label, ownership or consent workflows are implemented.

## Shared guardianship requirements
Each guardian uses their own account. An invitation is not access until securely
accepted; it must not reveal child information to an unverified recipient. Adding a
new partner must never automatically expose other children, guardian contacts,
billing details or historical messages. Permissions to invite/remove guardians,
manage labels, change disclosure and receive messages must be distinguished.
Exact roles and historical-message access remain design decisions.

Notification recipients must be authorized for the relevant child/item, opted into
the applicable notification channel, and have verified destinations. Re-evaluate
eligibility at delivery time, including retries, so queued alerts cannot continue
after revocation. Use separate deliveries, never group email CC lists. External
alert previews should contain minimal detail and link to an authenticated inbox.
Do not tell the finder guardian identities, recipient counts, or delivery status.

A shared child needs one effective public disclosure policy, not the union of each
guardian's preferences. Who can broaden disclosure and how conflicts are resolved
must be agreed before this feature ships; do not silently choose the most permissive
setting. A conservative proposed rule is that restrictive changes apply immediately
and broader disclosure remains hidden until the agreed consent process completes.
