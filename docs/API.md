# API v1

JSON API. GET `/auth/session/` obtains a CSRF token and current user; send that token
as X-CSRFToken on mutations, with the session cookie. Login/logout rotate the token;
use the returned value. Prefix all routes below with `/api/v1/`.

| Route | Methods | Access / purpose |
| --- | --- | --- |
| auth/session/ | GET | Public; session and CSRF bootstrap |
| auth/register/ | POST | Public + CSRF; username/email/password |
| auth/login/ | POST | Public + CSRF; username/password |
| auth/logout/ | POST | Session + CSRF |
| auth/verify/ | POST | Session; send email verification link |
| auth/verify/confirm/ | POST | Session; accept signed email token |
| profiles/ | GET, POST | Current grants; create private name and kind |
| profiles/{id}/preferences/ | PATCH | Own email_alerts opt-in; verified email required |
| profiles/{id}/invitations/ | POST | Controller; invite email |
| invitations/{id}/accept/ | POST | Invited verified account; single-use |
| profiles/{id}/access/ | GET | Controller; list active guardian usernames |
| profiles/{id}/access/{grant}/ | DELETE | Controller; revoke another guardian |
| objects/ | GET, POST | Active grants; profile UUID, name, kind=item/group, optional print_text/public_text/share_text |
| objects/{id}/ | PATCH | Active grant; rename private object name without changing its QR |
| sheets/preview/ | POST | Active grants; entries=[{object_id, quantity}], paper=A4/Letter; max 180 labels, ordered pages of 18 |
| labels/ | GET, POST | Active grant; profile UUID, optional item_name, print_text, public_text, share_text |
| labels/{id}/ | PATCH | Active grant; text/active changes subject to controller policy |
| labels/{id}/qr/ | GET | Active grant; SVG encoding scan URL |
| scan/{token}/ | GET | Public; only opted-in public_text |
| scan/{token}/ | POST | Public + CSRF; message and submission_id UUID |
| inbox/ | GET | Current guardian; latest 100 reports within grant dates |
| health/ | GET | Public minimal liveness |

Django admin is separately served at `/admin/`. Missing/revoked scan tokens return
indistinguishable 404 responses. POSTing the same label/submission UUID is idempotent.
Responses never reveal notification recipient identities to finders. UUID tokens are
not account credentials. Draft scan text and print text never appear on the public API.

Use objects/ for the main object-first UI. The earlier labels/ create endpoint is kept
for compatibility; blank item_name creates a generic group object. Sheet quantities
must be positive integers; omit zero selections. Duplicate object entries, invalid
quantities, disabled codes and unauthorized objects are rejected. Sheet preview is
transient: it does not create database sheet records or new QR codes.
