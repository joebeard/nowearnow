import uuid
from datetime import timedelta
from smtplib import SMTPException
from unittest.mock import patch

from accounts.models import User
from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Access, Delivery, Invitation, Label, Profile, Report


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class LabelFlowTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.owner = User.objects.create_user(
            "parentone", email="one@example.test", email_verified=True
        )
        self.other = User.objects.create_user(
            "parenttwo", email="two@example.test", email_verified=True
        )
        self.stranger = User.objects.create_user("stranger", email="outsider@example.test")
        self.profile = Profile.objects.create(kind="child", name="Private nickname")
        self.owner_access = Access.objects.create(
            profile=self.profile, user=self.owner, controller=True, email_alerts=True
        )
        self.other_access = Access.objects.create(
            profile=self.profile, user=self.other, email_alerts=True
        )
        self.label = Label.objects.create(
            profile=self.profile, public_text="Private until enabled", print_text="Printed name"
        )
        self.client.force_login(self.owner)

    def scan(self, token=None):
        return f"/api/v1/scan/{token or self.label.token}/"

    def report(self, submission=None):
        return self.client.post(
            self.scan(),
            {"message": "At reception", "submission_id": str(submission or uuid.uuid4())},
            format="json",
        )

    def test_scan_does_not_expose_printed_text_or_private_profile(self):
        self.client.logout()
        response = self.client.get(self.scan())
        self.assertEqual(response.json(), {"public_text": ""})
        self.assertNotContains(response, "Printed name")
        self.assertNotContains(response, "Private nickname")
        self.label.share_text = True
        self.label.save()
        self.assertEqual(
            self.client.get(self.scan()).json(), {"public_text": "Private until enabled"}
        )

    def test_generic_and_item_labels_for_all_profile_kinds(self):
        for kind in ("child", "adult", "family"):
            p = self.client.post("/api/v1/profiles/", {"name": "Private", "kind": kind}).json()[
                "id"
            ]
            for item in ("", "Laptop"):
                response = self.client.post(
                    "/api/v1/labels/", {"profile": p, "item_name": item, "print_text": "My label"}
                )
                self.assertEqual(response.status_code, 201)
                label = Label.objects.get(pk=response.json()["id"])
                self.assertEqual(label.item.name, item or "General belongings")
                self.assertFalse(label.share_text)
                self.assertEqual(label.token.version, 4)
                self.assertNotIn("Private", response.json()["scan_url"])

    def test_cross_profile_access_and_writes_denied(self):
        self.client.force_login(self.stranger)
        self.assertEqual(self.client.get("/api/v1/labels/").json(), [])
        self.assertEqual(
            self.client.post("/api/v1/labels/", {"profile": str(self.profile.pk)}).status_code, 404
        )
        self.assertEqual(
            self.client.patch(
                f"/api/v1/labels/{self.label.pk}/", {"public_text": "Leak"}
            ).status_code,
            404,
        )
        self.assertEqual(self.client.get(f"/api/v1/labels/{self.label.pk}/qr/").status_code, 404)

    def test_shared_child_does_not_expose_other_children(self):
        sibling = Profile.objects.create(kind="child", name="Other child")
        Access.objects.create(profile=sibling, user=self.owner, controller=True)
        Label.objects.create(profile=sibling)
        self.client.force_login(self.other)
        self.assertEqual(len(self.client.get("/api/v1/profiles/").json()), 1)
        self.assertEqual(len(self.client.get("/api/v1/labels/").json()), 1)

    def test_guardian_can_restrict_but_not_broaden_disclosure(self):
        self.client.force_login(self.other)
        path = f"/api/v1/labels/{self.label.pk}/"
        self.assertEqual(self.client.patch(path, {"share_text": True}).status_code, 403)
        self.assertEqual(self.client.patch(path, {"public_text": "Changed"}).status_code, 403)
        self.assertEqual(self.client.patch(path, {"share_text": False}).status_code, 200)
        self.assertEqual(self.client.patch(path, {"active": False}).status_code, 200)

    def test_disabled_and_unknown_labels_have_same_response(self):
        self.label.active = False
        self.label.save()
        self.client.logout()
        a = self.client.get(self.scan())
        b = self.client.get(self.scan(uuid.uuid4()))
        self.assertEqual((a.status_code, a.json()), (b.status_code, b.json()))
        self.assertEqual(self.report().status_code, 404)

    def test_reports_are_idempotent_and_notify_multiple_guardians_privately(self):
        submission = uuid.uuid4()
        self.assertEqual(self.report(submission).status_code, 202)
        self.assertEqual(self.report(submission).status_code, 202)
        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(Delivery.objects.count(), 2)
        call_command("send_notifications", verbosity=0)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            {tuple(m.to) for m in mail.outbox}, {(self.owner.email,), (self.other.email,)}
        )
        for email in mail.outbox:
            self.assertNotIn("At reception", email.body)
            self.assertNotIn("Private nickname", email.body)
        call_command("send_notifications", verbosity=0)
        self.assertEqual(len(mail.outbox), 2)

    def test_revoked_guardian_gets_no_queued_email_or_inbox(self):
        self.report()
        self.other_access.active = False
        self.other_access.save()
        call_command("send_notifications", verbosity=0)
        self.assertEqual(len(mail.outbox), 1)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get("/api/v1/inbox/").json(), [])
        self.assertEqual(self.client.get(f"/api/v1/labels/{self.label.pk}/qr/").status_code, 404)

    def test_failed_recipient_does_not_block_other_and_can_retry(self):
        self.report()
        with patch(
            "labels.management.commands.send_notifications.send_mail",
            side_effect=[SMTPException(), 1],
        ):
            call_command("send_notifications", verbosity=0)
        self.assertEqual(Delivery.objects.filter(status="failed").count(), 1)
        self.assertEqual(Delivery.objects.filter(status="sent").count(), 1)
        call_command("send_notifications", verbosity=0)
        self.assertEqual(Delivery.objects.filter(status="sent").count(), 2)

    def test_unverified_and_opted_out_receive_no_email(self):
        self.other.email_verified = False
        self.other.save()
        self.owner_access.email_alerts = False
        self.owner_access.save()
        self.report()
        call_command("send_notifications", verbosity=0)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(len(self.client.get("/api/v1/inbox/").json()), 1)

    def test_print_qr_requires_auth_and_has_svg(self):
        path = f"/api/v1/labels/{self.label.pk}/qr/"
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/svg+xml")
        self.assertIn(b"<svg", response.content)
        self.client.logout()
        self.assertEqual(self.client.get(path).status_code, 403)

    def test_public_submission_requires_csrf_and_limits_input(self):
        client = APIClient(enforce_csrf_checks=True)
        fields = {"message": "Hello", "submission_id": str(uuid.uuid4())}
        self.assertEqual(client.post(self.scan(), fields).status_code, 403)
        csrf = client.get("/api/v1/auth/session/").json()["csrf"]
        self.assertEqual(client.post(self.scan(), fields, HTTP_X_CSRFTOKEN=csrf).status_code, 202)
        fields["message"] = "x" * 1501
        self.assertEqual(client.post(self.scan(), fields, HTTP_X_CSRFTOKEN=csrf).status_code, 400)

    def test_invitation_is_email_bound_expiring_and_does_not_grant_history(self):
        self.report()
        response = self.client.post(
            f"/api/v1/profiles/{self.profile.pk}/invitations/", {"email": self.stranger.email}
        )
        self.assertEqual(response.status_code, 201)
        invite = Invitation.objects.get()
        self.assertNotIn(self.profile.name, mail.outbox[0].body)
        self.client.force_login(self.other)
        self.assertEqual(
            self.client.post(f"/api/v1/invitations/{invite.pk}/accept/").status_code, 404
        )
        self.stranger.email_verified = True
        self.stranger.save()
        self.client.force_login(self.stranger)
        self.assertEqual(
            self.client.post(f"/api/v1/invitations/{invite.pk}/accept/").status_code, 200
        )
        self.assertEqual(
            self.client.post(f"/api/v1/invitations/{invite.pk}/accept/").status_code, 404
        )
        self.assertEqual(self.client.get("/api/v1/inbox/").json(), [])
        expired = Invitation.objects.create(
            profile=self.profile, created_by=self.owner, email=self.stranger.email
        )
        Invitation.objects.filter(pk=expired.pk).update(
            created_at=timezone.now() - timedelta(days=3)
        )
        self.assertEqual(
            self.client.post(f"/api/v1/invitations/{expired.pk}/accept/").status_code, 404
        )

    def test_rejoining_cannot_read_previous_messages(self):
        self.report()
        self.other_access.joined_at = timezone.now()
        self.other_access.save()
        self.client.force_login(self.other)
        self.assertEqual(self.client.get("/api/v1/inbox/").json(), [])


class FamilyManagementTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.owner = User.objects.create_user("manager", email_verified=True)
        self.other = User.objects.create_user("guardian")
        self.client.force_login(self.owner)
        self.family = Profile.objects.create(name="Family", kind="family")
        self.child = Profile.objects.create(name="Child", kind="child")
        for profile in [self.family, self.child]:
            Access.objects.create(profile=profile, user=self.owner, controller=True)
        self.label = Label.objects.create(profile=self.child, print_text="Printed")

    def test_memberships_do_not_grant_access_or_disclose_hidden_members(self):
        path = f"/api/v1/families/{self.family.pk}/members/"
        self.assertEqual(self.client.post(path, {"profile": str(self.child.pk)}).status_code, 201)
        Access.objects.create(profile=self.family, user=self.other)
        self.client.force_login(self.other)
        profiles = self.client.get("/api/v1/profiles/").json()
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["members"], [])
        self.assertEqual(self.client.get("/api/v1/objects/").json(), [])
        self.assertEqual(self.client.post(path, {"profile": str(self.child.pk)}).status_code, 403)

    def test_child_can_belong_to_multiple_families_without_changing_access(self):
        from .models import FamilyMembership

        second = Profile.objects.create(name="Second family", kind="family")
        Access.objects.create(profile=second, user=self.owner, controller=True)
        for family in [self.family, second]:
            self.assertEqual(
                self.client.post(
                    f"/api/v1/families/{family.pk}/members/",
                    {"profile": str(self.child.pk)},
                ).status_code,
                201,
            )
        self.assertEqual(FamilyMembership.objects.filter(member=self.child).count(), 2)
        self.assertEqual(Access.objects.filter(profile=self.child).count(), 1)
        self.assertEqual(
            self.client.delete(
                f"/api/v1/families/{second.pk}/members/{self.child.pk}/"
            ).status_code,
            204,
        )
        self.assertTrue(Access.objects.filter(profile=self.child, user=self.owner).exists())

    def test_archiving_disables_labels_alerts_and_pending_invitations(self):
        access = Access.objects.get(profile=self.child, user=self.owner)
        access.email_alerts = True
        access.save()
        report = Report.objects.create(label=self.label, submission_id=uuid.uuid4(), message="Here")
        delivery = Delivery.objects.create(report=report, access=access)
        Invitation.objects.create(profile=self.child, created_by=self.owner, email="a@example.test")
        path = f"/api/v1/profiles/{self.child.pk}/"
        self.assertEqual(
            self.client.patch(path, {"archived": True}, format="json").status_code, 200
        )
        self.label.refresh_from_db()
        access.refresh_from_db()
        delivery.refresh_from_db()
        self.assertFalse(self.label.active)
        self.assertFalse(access.email_alerts)
        self.assertEqual(delivery.status, "skipped")
        self.assertFalse(Invitation.objects.exists())
        self.assertEqual(self.client.get(f"/api/v1/scan/{self.label.token}/").status_code, 404)
        self.assertEqual(
            self.client.post(
                "/api/v1/objects/", {"profile": str(self.child.pk), "name": "Bag", "kind": "item"}
            ).status_code,
            404,
        )
        self.client.patch(path, {"archived": False}, format="json")
        self.label.refresh_from_db()
        self.assertFalse(self.label.active)
        self.assertTrue(Report.objects.filter(pk=report.pk).exists())

    def test_only_controller_can_rename_archive_and_names_stay_private(self):
        path = f"/api/v1/profiles/{self.child.pk}/"
        Access.objects.create(profile=self.child, user=self.other)
        self.client.force_login(self.other)
        self.assertEqual(self.client.patch(path, {"name": "New"}).status_code, 403)
        self.assertEqual(self.client.patch(path, {"archived": True}).status_code, 403)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.patch(path, {"name": "New"}).status_code, 200)
        self.label.refresh_from_db()
        self.assertEqual(self.label.print_text, "Printed")
        self.assertEqual(
            self.client.get(f"/api/v1/scan/{self.label.token}/").json(), {"public_text": ""}
        )
        self.client.patch(f"/api/v1/profiles/{self.family.pk}/", {"archived": True})
        self.child.refresh_from_db()
        self.assertFalse(self.child.archived)

    def test_cancelled_invitation_cannot_be_accepted(self):
        self.other.email = "guardian@example.test"
        self.other.email_verified = True
        self.other.save()
        invitation = Invitation.objects.create(
            profile=self.child, created_by=self.owner, email=self.other.email
        )
        path = f"/api/v1/profiles/{self.child.pk}/invitations/"
        self.assertEqual(len(self.client.get(path).json()), 1)
        self.assertEqual(self.client.delete(f"{path}{invitation.pk}/").status_code, 204)
        self.client.force_login(self.other)
        self.assertEqual(
            self.client.post(f"/api/v1/invitations/{invitation.pk}/accept/").status_code, 404
        )
