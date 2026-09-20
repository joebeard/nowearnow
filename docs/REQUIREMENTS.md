# Product requirements

## Confirmed by the user
- Mobile-first Django/Python API and React application for nowearnow.com.
- QR stickers and clothing labels help return children's lost belongings.
- Parents control public disclosure; the most private settings are the default.
- Make it easy for multiple parents/guardians to manage multiple children, including
  divorced co-parents and remarried/blended families.
- Alert multiple parents/guardians when an item is reported found.
- Scanning an item opens a page with information and a form for the finder to send
  a message to the item's guardians.

## Intended journeys
A guardian uses their own account and sees the children they are authorized to
manage in one place. Each child can have multiple guardians. A parent may share
one child with an ex-partner and another with a current partner; neither partner
receives access to the other child automatically. Switching children should be easy
on mobile without switching accounts. Invitation details and roles remain to design.

A finder scans without needing an account or installed app. A valid active label
opens a mobile page with generic return guidance, any information explicitly approved
for public display, and a message form. With private defaults, no personal details
appear and the finder can still send a message. Provisional form: a required bounded
plain-text message, with optional return location/instructions; any reply/contact
mechanism needs a separate privacy decision and must not be required just to report.

An accepted report generates notifications for multiple eligible guardians of that
child/item. A page view alone is not a found-item report and must not generate an
alert by default. Recipients access the report securely; the finder sees a generic
acknowledgement, not guardian contact details or delivery information.

## Acceptance criteria for implementation
- Two guardians can manage the same child from separate accounts.
- One guardian can manage several children with different co-guardians.
- Shared access to one child exposes no other children or unrelated account data.
- Accepted invitations and action-specific grants control all server-side access.
- Revoked guardians lose access and receive no subsequently dispatched alerts,
  including queued retries; already received messages cannot be recalled.
- Multiple eligible guardians receive separate alerts for one submitted report;
  one delivery failure does not prevent other recipients receiving theirs.
- Retry/deduplication prevents duplicate alerts for the same accepted submission.
- Scanning reveals only the effective explicit disclosure allowlist, with no personal
  fields shown by default; turning off disclosure does not disable the message form.
- Invalid/revoked tokens disclose no child or guardian details and cannot submit reports.
- Anonymous submissions have validation, abuse protection and safe acknowledgement.
- Mobile UI clearly shows the selected child and previews public disclosure before saving.

Implementation details are provisional until recorded in an accepted decision.
The scaffold does not implement these journeys yet.
