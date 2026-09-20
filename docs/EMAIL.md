# Email integration

The Django email interface is used for verification, guardian invitations and found-item
notifications. Default: file delivery to backend/dev-emails/, excluded from Git.
These local files contain sensitive links/addresses; delete them when no longer needed.
No email-provider API key or external account is required for local testing.

SMTP configuration: EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend,
EMAIL_HOST, EMAIL_PORT (587), EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS
(true), DEFAULT_FROM_EMAIL. PUBLIC_BASE_URL determines link destinations. Environment
variables are read at startup; `.env` files are not automatically loaded. Configure a
verified sending domain/SPF/DKIM/DMARC with the chosen provider before live delivery.
Provider, hosting region and data-processing arrangements are not selected.

Verification and invitation emails send synchronously with a ten-second timeout;
provider errors return a generic retry response without logging addresses or secrets.
Report requests only store the message and recipient snapshot; `make notifications`
dispatches found-item alerts separately. A failing recipient does not stop others.
Eligibility is checked again before sending: active grant/account, current join date,
verified email and opt-in. Email bodies contain a generic inbox link, no personal data.
Newly invited guardians do not gain access to old reports. Alerts are off by default.

Successful delivery rows are not sent again on normal retries. SMTP cannot guarantee
exactly-once delivery if a worker crashes after sending but before committing the status;
production needs provider idempotency/reconciliation, a supervised worker, scheduled
backoff and concurrency testing on PostgreSQL. Run only one worker in this SQLite
prototype. Five failed attempts stop automatic retries and remain visible in admin.

Future SMS/Twilio: add separately verified phone destinations, per-profile explicit
channel opt-in, generic notifications, provider credentials and an adapter using the
same permission/revocation checks. Do not reuse email verification as phone consent.
No Twilio dependency, credentials, phone data or SMS sends exist in this milestone.
