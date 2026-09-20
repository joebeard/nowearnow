from django.test import SimpleTestCase, override_settings
from django.urls import path
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView


class PrivateProbe(APIView):
    def get(self, request):
        return Response({"private": True})


urlpatterns = [path("private/", PrivateProbe.as_view())]


class BoundaryTests(SimpleTestCase):
    def test_health_is_public_and_minimal(self):
        response = self.client.get("/api/v1/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertEqual(response["Referrer-Policy"], "no-referrer")
        self.assertIn("noindex", response["X-Robots-Tag"])

    def test_new_api_views_deny_anonymous_by_default(self):
        response = PrivateProbe.as_view()(APIRequestFactory().get("/private/"))
        self.assertEqual(response.status_code, 403)

    @override_settings(ROOT_URLCONF="core.tests")
    def test_denied_responses_are_not_cacheable(self):
        response = self.client.get("/private/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response["Cache-Control"], "no-store")

    def test_health_does_not_accept_writes(self):
        self.assertEqual(self.client.post("/api/v1/health/", {}).status_code, 405)
