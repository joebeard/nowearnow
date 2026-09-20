import time
from unittest.mock import patch

from django.core import mail, signing
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .models import User


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AuthTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient(enforce_csrf_checks=True)
        self.user = User.objects.create_user(
            "guardian", email="guardian@example.test", password="Long-test-Phrase-749!"
        )

    def token(self):
        return self.client.get("/api/v1/auth/session/").json()["csrf"]

    def test_login_requires_csrf_and_rotates_session(self):
        payload = {"username": "guardian", "password": "Long-test-Phrase-749!"}
        self.assertEqual(self.client.post("/api/v1/auth/login/", payload).status_code, 403)
        response = self.client.post("/api/v1/auth/login/", payload, HTTP_X_CSRFTOKEN=self.token())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["username"], "guardian")
        self.assertEqual(self.client.get("/api/v1/profiles/").status_code, 200)
        self.assertEqual(self.client.post("/api/v1/auth/logout/").status_code, 403)
        self.assertEqual(
            self.client.post(
                "/api/v1/auth/logout/", HTTP_X_CSRFTOKEN=response.json()["csrf"]
            ).status_code,
            200,
        )
        self.assertEqual(self.client.get("/api/v1/profiles/").status_code, 403)

    def test_registration_password_validation_and_private_default(self):
        payload = {"username": "newguardian", "email": "new@example.test", "password": "123"}
        self.assertEqual(
            self.client.post(
                "/api/v1/auth/register/", payload, HTTP_X_CSRFTOKEN=self.token()
            ).status_code,
            400,
        )
        payload["password"] = "Another-long-test-phrase-573!"
        response = self.client.post(
            "/api/v1/auth/register/", payload, HTTP_X_CSRFTOKEN=self.token()
        )
        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.json()["user"]["email_verified"])

    def test_email_is_unique_case_insensitively(self):
        payload = {
            "username": "another",
            "email": "GUARDIAN@example.test",
            "password": "Another-long-test-phrase-573!",
        }
        self.assertEqual(
            self.client.post(
                "/api/v1/auth/register/", payload, HTTP_X_CSRFTOKEN=self.token()
            ).status_code,
            400,
        )

    def test_verification_binds_to_logged_in_account_and_expires(self):
        self.client.force_login(self.user)
        response = self.client.post("/api/v1/auth/verify/", HTTP_X_CSRFTOKEN=self.token())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        token = mail.outbox[0].body.split("#")[1]
        response = self.client.post(
            "/api/v1/auth/verify/confirm/", {"token": token}, HTTP_X_CSRFTOKEN=self.token()
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)
        bad = signing.dumps({"user": 999, "email": self.user.email}, salt="email")
        self.assertEqual(
            self.client.post(
                "/api/v1/auth/verify/confirm/", {"token": bad}, HTTP_X_CSRFTOKEN=self.token()
            ).status_code,
            400,
        )

    def test_anonymous_auth_attempts_are_throttled(self):
        for _ in range(20):
            self.client.post(
                "/api/v1/auth/login/",
                {"username": "missing", "password": "wrong"},
                HTTP_X_CSRFTOKEN=self.token(),
            )
        self.assertEqual(
            self.client.post("/api/v1/auth/login/", {}, HTTP_X_CSRFTOKEN=self.token()).status_code,
            429,
        )

    def test_verification_rejects_expired_token(self):
        self.client.force_login(self.user)
        with patch("django.core.signing.time.time", return_value=time.time() - 90000):
            token = signing.dumps({"user": self.user.pk, "email": self.user.email}, salt="email")
        response = self.client.post(
            "/api/v1/auth/verify/confirm/", {"token": token}, HTTP_X_CSRFTOKEN=self.token()
        )
        self.assertEqual(response.status_code, 400)

    def test_login_rejects_untrusted_origin(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {
                "username": "guardian",
                "password": "Long-test-Phrase-749!",
            },
            HTTP_X_CSRFTOKEN=self.token(),
            HTTP_ORIGIN="https://untrusted.example",
        )
        self.assertEqual(response.status_code, 403)
