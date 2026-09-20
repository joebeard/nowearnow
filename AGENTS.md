# nowearnow — working instructions

## Read before changing code
Read `docs/STATUS.md`, `docs/ARCHITECTURE.md`, `docs/REQUIREMENTS.md`, and `docs/PRIVACY.md`. Consult
`docs/decisions/` before revisiting a decision. `README.md` contains setup commands.

## Product and stack
nowearnow.com helps parents recover children's lost belongings using QR stickers
and clothing labels. Mobile-first React + TypeScript; Python/Django with a versioned
REST API. Repository root: /home/jbeard/git/nowearnow.

## Non-negotiable privacy boundaries
- Parents control disclosure. Default to no personal information shared.
- Enforce disclosure and ownership on the server, never only in React.
- Each public field requires explicit opt-in; new fields default to hidden.
- Printed names/text are a separate, optional physical disclosure; never copy them
  into the public scan response automatically.
- QR codes contain opaque random tokens, never personal data or sequential IDs.
- A scan is not authentication, ownership proof, or permission to claim a label.
- Keep child profiles separate from adult accounts; do not build child logins.
- Support many guardians per child and many children per guardian, including co-parenting
  and blended families. Do not assume one household or a single parent owner.
- Use explicit per-child access grants; partnership does not confer access automatically.
- Scan pages combine approved information with a private finder-to-guardian message form.
- Deliver found-item alerts to multiple eligible guardians without exposing contacts.
- Do not log QR tokens, message contents, child details, or contact information.
- No trackers, advertising pixels, session replay, or third-party assets on scan pages.
- Do not add real family data to fixtures, screenshots, prompts, or tests.
- See PRIVACY.md for future feature acceptance criteria and unresolved decisions.

## Engineering
- API prefix: /api/v1/. Default DRF permissions require authentication.
- Explicitly review any AllowAny view and allowlist every public response field.
- Use Django session authentication with CSRF for the web app; never disable CSRF
  to make integration work. Native-app authentication is undecided.
- Scope profile/item queries and writes to active guardian grants and action permissions.
  Profiles may represent a child, adult or family; family grants do not imply child access.
  Keep purchaser ownership separate from child-management access.
- Keep secrets out of Git; no production defaults or silent development fallbacks.
- Keep dependencies and lockfiles aligned. Run `make check` for code changes.
- Add meaningful tests for disclosure, guardian access, revocation, notification recipients, and CSRF
  as the corresponding capabilities are built.

## Session continuity
Update docs/STATUS.md after substantive work: what exists, checks performed, next
steps, and known gaps. Record significant decisions in docs/decisions/ with rationale,
consequences, and status. Distinguish user requirements from provisional choices.
Do not rely on previous chat history being available. Keep this file concise.
