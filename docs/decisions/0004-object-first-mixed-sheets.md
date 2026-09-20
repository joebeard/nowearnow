# ADR 0004: Object-first management and mixed label sheets

Date: 2026-09-20. Status: implemented local milestone.

User refinement: create objects first, then choose quantities of multiple objects on
one sheet (1 laptop, 1 calculator, 4 clothing labels for each of two children).

Decision: use Item as the first-class object (specific item or reusable group), linked
to a Profile. Every object has one canonical Label. Generic belongings are group objects,
not an absent item. A migration attaches existing generic labels to group objects and
preserves their IDs, scan tokens and reports. This supersedes ADR 0003's optional-item
representation; the legacy label-create endpoint remains compatible.

The frontend sheet builder spans all accessible profiles, takes quantities per object,
and requests a validated server preview. The server rejects unauthorized/disabled
objects, duplicate entries, non-positive/non-integer quantities and runs above 180.
It expands valid entries in order into sheets of 18; remaining cells stay blank on the
last sheet. No new identity/token is minted when printing. Quantity changes invalidate
the preview. Print quantities are local page state, not persisted sheet templates.

Printed text is still explicitly chosen and independent of private object/profile
names or public scan text. No automatic name disclosure occurs in this refactor.

Validation: backend tests cover the 1/1/4/4 mix, stable QR URLs, 18/18/1 pagination,
authorization/revocation, disabled objects, bounds and naming privacy. Browser tests
reproduced a 10-label mixed sheet across a family and two synthetic child profiles.
Physical print/scanner testing and stock-specific layouts remain follow-up work.
