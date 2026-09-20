from accounts.models import User
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from labels.models import Access, Item, Label, Profile


class ObjectSheetTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = User.objects.create_user("sheetparent")
        self.client.force_login(self.user)
        self.a = Profile.objects.create(kind="child", name="Child A")
        self.b = Profile.objects.create(kind="child", name="Child B")
        for profile in [self.a, self.b]:
            Access.objects.create(profile=profile, user=self.user, controller=True)

    def create(self, name, profile, kind="item"):
        response = self.client.post(
            "/api/v1/objects/", {"profile": str(profile.pk), "name": name, "kind": kind}
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def preview(self, entries):
        return self.client.post("/api/v1/sheets/preview/", {"entries": entries}, format="json")

    def test_mixed_sheet_matches_quantities_and_preserves_object_qrs(self):
        objects = [
            self.create("Laptop", self.a),
            self.create("Calculator", self.a),
            self.create("Clothing", self.a, "group"),
            self.create("Clothing", self.b, "group"),
        ]
        entries = [{"object_id": o["id"], "quantity": q} for o, q in zip(objects, [1, 1, 4, 4])]
        response = self.preview(entries)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 10)
        self.assertEqual(len(data["sheets"]), 1)
        cells = data["sheets"][0]
        self.assertEqual(
            [sum(c["object_id"] == o["id"] for c in cells) for o in objects], [1, 1, 4, 4]
        )
        self.assertEqual(len({c["scan_url"] for c in cells}), 4)
        self.assertEqual({c["scan_url"] for c in cells}, {o["label"]["scan_url"] for o in objects})
        self.preview(entries)
        self.assertEqual(Item.objects.count(), 4)
        self.assertEqual(Label.objects.count(), 4)

    def test_pagination_uses_18_cells_per_sheet(self):
        obj = self.create("Clothing", self.a, "group")
        response = self.preview([{"object_id": obj["id"], "quantity": 37}])
        self.assertEqual([len(s) for s in response.json()["sheets"]], [18, 18, 1])

    def test_invalid_quantities_duplicates_and_empty_selection_rejected(self):
        obj = self.create("Laptop", self.a)
        for quantity in [-1, 0, 1.5, 181, "many"]:
            self.assertEqual(
                self.preview([{"object_id": obj["id"], "quantity": quantity}]).status_code, 400
            )
        entry = {"object_id": obj["id"], "quantity": 1}
        self.assertEqual(self.preview([entry, entry]).status_code, 400)
        self.assertEqual(self.preview([]).status_code, 400)

    def test_sheet_rejects_foreign_disabled_and_revoked_objects(self):
        obj = self.create("Laptop", self.a)
        entries = [{"object_id": obj["id"], "quantity": 1}]
        Label.objects.filter(item_id=obj["id"]).update(active=False)
        self.assertEqual(self.preview(entries).status_code, 400)
        Label.objects.filter(item_id=obj["id"]).update(active=True)
        Access.objects.filter(profile=self.a).update(active=False)
        self.assertEqual(self.preview(entries).status_code, 400)
        stranger = User.objects.create_user("unrelated")
        self.client.force_login(stranger)
        self.assertEqual(self.preview(entries).status_code, 400)
        self.assertEqual(self.client.get("/api/v1/objects/").json(), [])
        self.assertEqual(
            self.client.patch(f"/api/v1/objects/{obj['id']}/", {"name": "Changed"}).status_code, 404
        )

    def test_private_names_and_printed_text_are_not_scan_text(self):
        obj = self.create("Private laptop", self.a)
        token = Label.objects.get(item_id=obj["id"]).token
        self.assertEqual(self.client.get(f"/api/v1/scan/{token}/").json(), {"public_text": ""})
        response = self.client.patch(f"/api/v1/objects/{obj['id']}/", {"name": "Renamed laptop"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["label"]["scan_url"], obj["label"]["scan_url"])

    def test_print_preview_requires_authentication(self):
        self.client.logout()
        self.assertEqual(self.preview([]).status_code, 403)
