# ADR 0002: Shared guardians and finder messaging

Date: 2026-09-20. Status: accepted requirements and architecture direction;
permission roles and disclosure-conflict rules remain open. Not implemented.

Context: the user requires easy multi-parent/multi-child management for divorced
co-parents and remarried families, alerts to multiple guardians, and a QR destination
combining information with a finder-to-guardian message form.

Decision: use independent adult accounts and explicit per-child many-to-many guardian
grants. Associate items/labels with a child; separate commerce ownership from child
access. Do not make a household, marriage, or single parent foreign key the access
boundary. A guardian can see only children covered by their active grants.

The scan page exposes generic guidance and an explicit public field allowlist, plus
an anonymous message form using a private relay. Public personal information remains
hidden by default. Accepted reports fan out to multiple eligible guardians with
separate deliveries and per-recipient retry state; recheck permission before dispatch.

Consequences: replace ADR 0001's tentative single-owner framing with guardian-scoped
authorization. Invitation/acceptance, permission changes, notification preferences,
and revocation need first-class implementation and tests. Exact roles, who can grant
or remove access, historical messages and authority to increase disclosure must be
settled before shipping. Shared guardianship must not silently broaden disclosure.

See ../REQUIREMENTS.md and ../PRIVACY.md for acceptance criteria and safeguards.
