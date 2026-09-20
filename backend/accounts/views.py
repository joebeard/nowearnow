from smtplib import SMTPException

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core import signing
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.db import IntegrityError
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from .models import User


class AuthThrottle(AnonRateThrottle):
    rate = "20/hour"

    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": "auth", "ident": self.get_ident(request)}


@method_decorator(csrf_protect, name="dispatch")
class PublicAuthView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]


def account(user):
    return {
        "username": user.username,
        "email_verified": user.email_verified,
        "is_staff": user.is_staff,
    }


class SessionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "csrf": get_token(request),
                "user": account(request.user) if request.user.is_authenticated else None,
            }
        )


class Credentials(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, trim_whitespace=False)


class Registration(Credentials):
    email = serializers.EmailField()


class RegisterView(PublicAuthView):
    def post(self, request):
        data = Registration(data=request.data)
        data.is_valid(raise_exception=True)
        fields = data.validated_data
        user = User(username=fields["username"], email=fields["email"].lower())
        try:
            user.full_clean(exclude=["password"])
            validate_password(fields["password"], user)
        except DjangoValidationError:
            return Response(
                {"detail": "Choose an available username and a stronger password."}, status=400
            )
        user.set_password(fields["password"])
        try:
            user.save()
        except IntegrityError:
            return Response({"detail": "Unable to create this account."}, status=400)
        login(request, user)
        return Response({"user": account(user), "csrf": get_token(request)}, status=201)


class LoginView(PublicAuthView):
    def post(self, request):
        data = Credentials(data=request.data)
        data.is_valid(raise_exception=True)
        user = authenticate(request, **data.validated_data)
        if user is None:
            return Response({"detail": "Username or password was not recognized."}, status=400)
        login(request, user)
        return Response({"user": account(user), "csrf": get_token(request)})


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"csrf": get_token(request)})


class EmailThrottle(UserRateThrottle):
    rate = "5/hour"


class VerificationView(APIView):
    throttle_classes = [EmailThrottle]

    def post(self, request):
        token = signing.dumps({"user": request.user.pk, "email": request.user.email}, salt="email")
        # Fragment keeps the verification token out of HTTP access logs/referrers.
        link = f"{settings.PUBLIC_BASE_URL}/verify#{token}"
        try:
            send_mail(
                "Verify your nowearnow email",
                f"Confirm your email within 24 hours:\n{link}",
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
            )
        except (OSError, SMTPException):
            return Response({"detail": "Email unavailable. Please try again later."}, status=503)
        return Response({"detail": "Verification email sent."})


class ConfirmVerificationView(APIView):
    def post(self, request):
        try:
            value = signing.loads(str(request.data.get("token", "")), salt="email", max_age=86400)
            if value != {"user": request.user.pk, "email": request.user.email}:
                raise signing.BadSignature()
        except signing.BadSignature:
            return Response({"detail": "Verification link is invalid or expired."}, status=400)
        request.user.email_verified = True
        request.user.save(update_fields=["email_verified"])
        return Response({"user": account(request.user)})
