# Current project status

Updated: 2026-09-20.

## Implemented
- Django/DRF and React/TypeScript/Vite development scaffold.
- Adult account model, minimal versioned health endpoint, API privacy defaults.
- Responsive placeholder page, local commands, dependency locks and CI definition.
- AGENTS.md, Claude compatibility import, architecture, privacy requirements and ADR.

## Next work
1. Design per-child guardian grants, invitations/revocation, disclosure authority and
   the permitted public fields; confirmed journeys are in REQUIREMENTS.md.
2. Design registration, verified contact, session login and account recovery.
3. Implement child-linked items/labels with guardian permissions and separate claim
   credentials and scan tokens.
4. Implement the approved-info scan page and finder message form, private relay,
   multi-guardian alerts and explicit disclosure settings with boundary tests.
5. Design commerce/printing and production infrastructure after those boundaries.

## Open questions
Launch countries and hosting region; minimum private child record fields;
field-level disclosure catalogue and authority/conflict rules; guardian invitation/
removal authority and historical message access; label activation/fulfilment;
email/SMS relay and notification preferences; retention periods; school involvement.

## Latest requirements update
Confirmed multi-guardian/multi-child management, co-parenting and blended families,
multi-recipient alerts, and a scan page combining approved info with a finder form.
Recorded in REQUIREMENTS.md and ADR 0002; these workflows are not yet implemented.
Documentation checked for consistency; no executable code changed in this update.

## Validation
Passed initial verification:
- Dependency installation and frozen Python lockfile sync.
- Database migration on a fresh local SQLite database; no migration drift.
- Ruff lint and formatting; Django system checks.
- Four API boundary tests: minimal public health response, anonymous denial by
  default, no-store on denied responses, and health write rejection.
- TypeScript type checking and Vite production build.
- npm install audit reported zero known vulnerabilities at installation time.

No browser/device QA or production infrastructure validation has been performed.

## Limits
No business workflow or production deployment exists. No Git remote selected.
Production entry points deliberately fail closed. This is not ready for real family data.
