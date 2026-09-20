from accounts import views as accounts
from core.views import HealthView
from django.contrib import admin
from django.urls import path
from labels import views as labels

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/health/", HealthView.as_view(), name="health"),
    path("api/v1/auth/session/", accounts.SessionView.as_view()),
    path("api/v1/auth/register/", accounts.RegisterView.as_view()),
    path("api/v1/auth/login/", accounts.LoginView.as_view()),
    path("api/v1/auth/logout/", accounts.LogoutView.as_view()),
    path("api/v1/auth/verify/", accounts.VerificationView.as_view()),
    path("api/v1/auth/verify/confirm/", accounts.ConfirmVerificationView.as_view()),
    path("api/v1/profiles/", labels.ProfilesView.as_view()),
    path("api/v1/profiles/<uuid:pk>/preferences/", labels.PreferencesView.as_view()),
    path("api/v1/profiles/<uuid:pk>/invitations/", labels.InvitationsView.as_view()),
    path("api/v1/profiles/<uuid:pk>/access/", labels.AccessView.as_view()),
    path("api/v1/profiles/<uuid:pk>/access/<int:access_id>/", labels.AccessView.as_view()),
    path("api/v1/invitations/<uuid:pk>/accept/", labels.AcceptInvitationView.as_view()),
    path("api/v1/labels/", labels.LabelsView.as_view()),
    path("api/v1/labels/<uuid:pk>/", labels.LabelView.as_view()),
    path("api/v1/labels/<uuid:pk>/qr/", labels.QRView.as_view()),
    path("api/v1/scan/<uuid:token>/", labels.ScanView.as_view()),
    path("api/v1/inbox/", labels.InboxView.as_view()),
]
