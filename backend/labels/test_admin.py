from accounts.models import User
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.test import TestCase

from labels.models import Item, Label, Profile


class AdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("regular")
        self.staff = User.objects.create_user("staff", is_staff=True)
        self.admin = User.objects.create_superuser("admin", "admin@example.test", "test-secret")

    def test_admin_form_keeps_same_origin_referrer_for_csrf(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response["Referrer-Policy"], "same-origin")
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_staff_flag_and_model_permissions_are_required(self):
        self.assertEqual(self.client.get("/admin/").status_code, 302)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get("/admin/").status_code, 302)
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get("/admin/labels/label/").status_code, 403)
        self.staff.user_permissions.add(Permission.objects.get(codename="view_label"))
        self.assertEqual(self.client.get("/admin/labels/label/").status_code, 200)

    def test_superuser_can_open_management_pages(self):
        self.client.force_login(self.admin)
        for path in (
            "",
            "accounts/user/",
            "labels/profile/",
            "labels/access/",
            "labels/item/",
            "labels/label/",
            "labels/report/",
            "labels/delivery/",
        ):
            self.assertEqual(self.client.get(f"/admin/{path}").status_code, 200)

    def test_label_item_must_belong_to_same_profile(self):
        child = Profile.objects.create(name="Child", kind="child")
        family = Profile.objects.create(name="Family", kind="family")
        item = Item.objects.create(profile=child, name="Laptop")
        with self.assertRaises(ValidationError):
            Label.objects.create(profile=family, item=item)
