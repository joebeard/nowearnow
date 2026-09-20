from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F

from labels.models import Delivery


class Command(BaseCommand):
    help = "Send pending found-item emails. Run one worker; failed deliveries retry on next run."

    def handle(self, *args, **options):
        sent = 0
        for pk in Delivery.objects.filter(
            status__in=["pending", "failed"], attempts__lt=5
        ).values_list("pk", flat=True):
            with transaction.atomic():
                delivery = (
                    Delivery.objects.select_for_update()
                    .select_related("access__user", "access__profile", "report")
                    .get(pk=pk)
                )
                if delivery.status not in {"pending", "failed"}:
                    continue
                access = delivery.access
                if (
                    access.profile.archived
                    or not access.active
                    or not access.email_alerts
                    or not access.user.is_active
                    or not access.user.email_verified
                    or delivery.report.created_at < access.joined_at
                ):
                    delivery.status = "skipped"
                else:
                    try:
                        count = send_mail(
                            "A found-item message is waiting",
                            f"Sign in to read your message:\n{settings.PUBLIC_BASE_URL}/",
                            settings.DEFAULT_FROM_EMAIL,
                            [access.user.email],
                        )
                        delivery.status = "sent" if count else "failed"
                        sent += count
                    except (OSError, SMTPException):
                        delivery.status = "failed"
                    delivery.attempts = F("attempts") + 1
                delivery.save(update_fields=["status", "attempts", "updated_at"])
        self.stdout.write(f"Sent {sent} notification(s). No message contents or recipients logged.")
