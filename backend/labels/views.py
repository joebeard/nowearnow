from datetime import timedelta
from io import BytesIO
from smtplib import SMTPException

import qrcode
import qrcode.image.svg
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from .models import Access, Delivery, Invitation, Item, Label, Profile, Report


def access_for(user, profile_id, controller=False):
    access = get_object_or_404(Access, user=user, profile_id=profile_id, active=True)
    if controller and not access.controller:
        raise PermissionDenied("Only the profile creator can manage access and public text.")
    return access


def label_data(label):
    return {
        "id": str(label.pk),
        "profile": str(label.profile_id),
        "item_name": label.item.name if label.item else "",
        "print_text": label.print_text,
        "public_text": label.public_text,
        "share_text": label.share_text,
        "active": label.active,
        "scan_url": f"{settings.PUBLIC_BASE_URL}/s/{label.token}",
        "qr_url": f"/api/v1/labels/{label.pk}/qr/",
    }


class ProfileInput(serializers.Serializer):
    name = serializers.CharField(max_length=80)
    kind = serializers.ChoiceField(choices=Profile.Kind.choices)


class ProfilesView(APIView):
    def get(self, request):
        return Response(
            [
                {
                    "id": str(a.profile_id),
                    "name": a.profile.name,
                    "kind": a.profile.kind,
                    "controller": a.controller,
                    "email_alerts": a.email_alerts,
                }
                for a in Access.objects.filter(user=request.user, active=True)
                .select_related("profile")
                .order_by("profile__created_at")
            ]
        )

    def post(self, request):
        data = ProfileInput(data=request.data)
        data.is_valid(raise_exception=True)
        with transaction.atomic():
            profile = Profile.objects.create(**data.validated_data)
            Access.objects.create(profile=profile, user=request.user, controller=True)
        return Response({"id": str(profile.pk)}, status=201)


class LabelInput(serializers.Serializer):
    profile = serializers.UUIDField()
    item_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    print_text = serializers.CharField(max_length=80, required=False, allow_blank=True)
    public_text = serializers.CharField(max_length=200, required=False, allow_blank=True)
    share_text = serializers.BooleanField(default=False)


class LabelChanges(serializers.Serializer):
    print_text = serializers.CharField(max_length=80, required=False, allow_blank=True)
    public_text = serializers.CharField(max_length=200, required=False, allow_blank=True)
    share_text = serializers.BooleanField(required=False)
    active = serializers.BooleanField(required=False)


class LabelsView(APIView):
    def get(self, request):
        labels = Label.objects.filter(
            profile__accesses__user=request.user, profile__accesses__active=True
        ).select_related("item")
        return Response([label_data(label) for label in labels.order_by("-created_at")])

    def post(self, request):
        data = LabelInput(data=request.data)
        data.is_valid(raise_exception=True)
        fields = data.validated_data
        access = access_for(request.user, fields["profile"])
        if fields.get("share_text") and not access.controller:
            raise PermissionDenied("Only the profile creator can opt into public text.")
        with transaction.atomic():
            item_name = fields.get("item_name", "")
            item = (
                Item.objects.create(profile=access.profile, name=item_name) if item_name else None
            )
            label = Label.objects.create(
                profile=access.profile,
                item=item,
                print_text=fields.get("print_text", ""),
                public_text=fields.get("public_text", ""),
                share_text=fields["share_text"],
            )
        return Response(label_data(label), status=201)


class LabelView(APIView):
    def patch(self, request, pk):
        label = get_object_or_404(Label, pk=pk)
        access = access_for(request.user, label.profile_id)
        data = LabelChanges(data=request.data)
        data.is_valid(raise_exception=True)
        changes = data.validated_data
        # Any guardian may hide text or disable a label; only controller can broaden access.
        if not access.controller and (
            "public_text" in changes or changes.get("share_text") or changes.get("active")
        ):
            raise PermissionDenied(
                "Only the profile creator can enable or change public information."
            )
        for key, value in changes.items():
            setattr(label, key, value)
        label.save()
        return Response(label_data(label))


class QRView(APIView):
    def get(self, request, pk):
        label = get_object_or_404(Label, pk=pk)
        access_for(request.user, label.profile_id)
        if not label.active:
            raise ValidationError("This label is disabled.")
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
        qr.add_data(f"{settings.PUBLIC_BASE_URL}/s/{label.token}")
        qr.make(fit=True)
        out = BytesIO()
        qr.make_image(image_factory=qrcode.image.svg.SvgPathFillImage).save(out)
        return HttpResponse(out.getvalue(), content_type="image/svg+xml")


class FinderThrottle(AnonRateThrottle):
    rate = "20/hour"


class ReportInput(serializers.Serializer):
    message = serializers.CharField(max_length=1500)
    submission_id = serializers.UUIDField()
    website = serializers.CharField(required=False, allow_blank=True, max_length=200)


@method_decorator(csrf_protect, name="dispatch")
class ScanView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [FinderThrottle]

    def get(self, request, token):
        label = get_object_or_404(Label, token=token, active=True)
        return Response({"public_text": label.public_text if label.share_text else ""})

    def post(self, request, token):
        label = get_object_or_404(Label, token=token, active=True)
        data = ReportInput(data=request.data)
        data.is_valid(raise_exception=True)
        fields = data.validated_data
        if not fields.get("website"):
            with transaction.atomic():
                report, created = Report.objects.get_or_create(
                    label=label,
                    submission_id=fields["submission_id"],
                    defaults={"message": fields["message"]},
                )
                if created:
                    Delivery.objects.bulk_create(
                        [
                            Delivery(
                                report=report,
                                access=a,
                                status="pending" if a.email_alerts else "skipped",
                            )
                            for a in label.profile.accesses.filter(active=True)
                        ]
                    )
        return Response({"detail": "Thank you. Your message has been received."}, status=202)


class InboxView(APIView):
    def get(self, request):
        deliveries = Delivery.objects.filter(
            access__user=request.user,
            access__active=True,
            report__created_at__gte=F("access__joined_at"),
        )
        return Response(
            [
                {
                    "id": str(d.report_id),
                    "message": d.report.message,
                    "profile": d.access.profile.name,
                    "item_name": d.report.label.item.name if d.report.label.item else "",
                    "created_at": d.report.created_at.isoformat(),
                }
                for d in deliveries.select_related(
                    "report__label__item", "access__profile"
                ).order_by("-report__created_at")[:100]
            ]
        )


class Preferences(serializers.Serializer):
    email_alerts = serializers.BooleanField()


class PreferencesView(APIView):
    def patch(self, request, pk):
        access = access_for(request.user, pk)
        data = Preferences(data=request.data)
        data.is_valid(raise_exception=True)
        if data.validated_data["email_alerts"] and not request.user.email_verified:
            raise ValidationError("Verify your email before enabling notifications.")
        access.email_alerts = data.validated_data["email_alerts"]
        access.save(update_fields=["email_alerts"])
        return Response({"email_alerts": access.email_alerts})


class InviteInput(serializers.Serializer):
    email = serializers.EmailField()


class InviteThrottle(UserRateThrottle):
    rate = "10/hour"


class InvitationsView(APIView):
    throttle_classes = [InviteThrottle]

    def post(self, request, pk):
        access_for(request.user, pk, controller=True)
        if not request.user.email_verified:
            raise PermissionDenied("Verify your email before inviting another guardian.")
        data = InviteInput(data=request.data)
        data.is_valid(raise_exception=True)
        invite = Invitation.objects.create(
            profile_id=pk, created_by=request.user, email=data.validated_data["email"].lower()
        )
        link = f"{settings.PUBLIC_BASE_URL}/invite#{invite.pk}"
        try:
            send_mail(
                "Invitation to nowearnow",
                "Sign in with this verified email to accept "
                f"shared access within 48 hours.\n{link}",
                settings.DEFAULT_FROM_EMAIL,
                [invite.email],
            )
        except (OSError, SMTPException):
            invite.delete()
            return Response({"detail": "Email unavailable. Please try again later."}, status=503)
        return Response({"detail": "Invitation sent."}, status=201)


class AcceptInvitationView(APIView):
    def post(self, request, pk):
        if not request.user.email_verified:
            raise PermissionDenied("Verify your email before accepting an invitation.")
        with transaction.atomic():
            invite = get_object_or_404(
                Invitation.objects.select_for_update(),
                pk=pk,
                accepted=False,
                email=request.user.email.lower(),
                created_at__gte=timezone.now() - timedelta(hours=48),
            )
            if not Access.objects.filter(
                profile=invite.profile, user=invite.created_by, active=True, controller=True
            ).exists():
                raise PermissionDenied("This invitation is no longer available.")
            access, created = Access.objects.get_or_create(
                profile=invite.profile, user=request.user
            )
            if not created and not access.active:
                access.active = True
                access.joined_at = timezone.now()
                access.email_alerts = False
                access.save()
            invite.accepted = True
            invite.save(update_fields=["accepted"])
        return Response({"detail": "Shared access accepted."})


class AccessView(APIView):
    def get(self, request, pk):
        access_for(request.user, pk, controller=True)
        return Response(
            [
                {"id": a.pk, "username": a.user.username, "controller": a.controller}
                for a in Access.objects.filter(profile_id=pk, active=True).select_related("user")
            ]
        )

    def delete(self, request, pk, access_id):
        access_for(request.user, pk, controller=True)
        access = get_object_or_404(Access, pk=access_id, profile_id=pk, controller=False)
        access.active = False
        access.email_alerts = False
        access.save(update_fields=["active", "email_alerts"])
        Invitation.objects.filter(profile_id=pk, email=access.user.email, accepted=False).delete()
        return Response(status=204)


class ObjectInput(LabelInput):
    name = serializers.CharField(max_length=100)
    kind = serializers.ChoiceField(choices=Item.Kind.choices, default=Item.Kind.ITEM)


def object_data(item):
    return {
        "id": str(item.pk),
        "name": item.name,
        "kind": item.kind,
        "profile": str(item.profile_id),
        "profile_name": item.profile.name,
        "label": label_data(item.label),
    }


class ObjectsView(APIView):
    def get(self, request):
        objects = Item.objects.filter(
            profile__accesses__user=request.user,
            profile__accesses__active=True,
            label__isnull=False,
        )
        return Response(
            [
                object_data(item)
                for item in objects.select_related("label__item", "profile").order_by(
                    "profile__created_at", "name", "pk"
                )
            ]
        )

    def post(self, request):
        data = ObjectInput(data=request.data)
        data.is_valid(raise_exception=True)
        fields = data.validated_data
        access = access_for(request.user, fields["profile"])
        if fields["share_text"] and not access.controller:
            raise PermissionDenied("Only the profile creator can opt into public text.")
        with transaction.atomic():
            item = Item.objects.create(
                profile=access.profile, name=fields["name"], kind=fields["kind"]
            )
            Label.objects.create(
                profile=access.profile,
                item=item,
                print_text=fields.get("print_text", ""),
                public_text=fields.get("public_text", ""),
                share_text=fields["share_text"],
            )
        return Response(object_data(item), status=201)


class ObjectChanges(serializers.Serializer):
    name = serializers.CharField(max_length=100)


class ObjectView(APIView):
    def patch(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        access_for(request.user, item.profile_id)
        data = ObjectChanges(data=request.data)
        data.is_valid(raise_exception=True)
        item.name = data.validated_data["name"]
        item.save(update_fields=["name"])
        return Response(object_data(item))


class SheetEntry(serializers.Serializer):
    object_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, max_value=180)


class SheetInput(serializers.Serializer):
    entries = SheetEntry(many=True, allow_empty=False, max_length=180)
    paper = serializers.ChoiceField(choices=["A4", "Letter"], default="A4")

    def validate_entries(self, entries):
        ids = [e["object_id"] for e in entries]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Choose each object once and set its quantity.")
        if sum(e["quantity"] for e in entries) > 180:
            raise serializers.ValidationError("Choose at most 180 labels per print run.")
        return entries


class SheetPreviewView(APIView):
    def post(self, request):
        data = SheetInput(data=request.data)
        data.is_valid(raise_exception=True)
        entries = data.validated_data["entries"]
        allowed = Item.objects.filter(
            pk__in=[e["object_id"] for e in entries],
            profile__accesses__user=request.user,
            profile__accesses__active=True,
            label__active=True,
        )
        objects = {item.pk: item for item in allowed.select_related("label__item", "profile")}
        if len(objects) != len(entries):
            raise ValidationError(
                "One or more objects are unavailable. Refresh your objects and try again."
            )
        cells = []
        for entry in entries:
            item = objects[entry["object_id"]]
            cell = {
                **label_data(item.label),
                "object_id": str(item.pk),
                "object_name": item.name,
                "profile_name": item.profile.name,
            }
            cells.extend([cell] * entry["quantity"])
        return Response(
            {
                "paper": data.validated_data["paper"],
                "total": len(cells),
                "sheets": [cells[i : i + 18] for i in range(0, len(cells), 18)],
            }
        )
