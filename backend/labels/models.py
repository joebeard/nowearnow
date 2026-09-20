import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction


class Profile(models.Model):
    class Kind(models.TextChoices):
        CHILD = "child", "Child"
        ADULT = "adult", "Adult"
        FAMILY = "family", "Family"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=10, choices=Kind.choices)
    name = models.CharField(max_length=80)  # Private dashboard name, never public automatically.
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            archiving = (
                self.archived and type(self).objects.filter(pk=self.pk, archived=False).exists()
            )
            super().save(*args, **kwargs)
            if archiving:
                Label.objects.filter(profile=self).update(active=False)
                Access.objects.filter(profile=self).update(email_alerts=False)
                Delivery.objects.filter(
                    report__label__profile=self, status__in=["pending", "failed"]
                ).update(status="skipped")
                Invitation.objects.filter(profile=self, accepted=False).delete()

    def __str__(self):
        return self.name


class FamilyMembership(models.Model):
    """Organization only: linking a child/adult never grants access to them."""

    family = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="family_memberships",
        limit_choices_to={"kind": "family"},
    )
    member = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="family_links",
        limit_choices_to={"kind__in": ["child", "adult"]},
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["family", "member"], name="one_family_membership")
        ]

    def clean(self):
        if self.family_id and (self.family.kind != Profile.Kind.FAMILY or self.family.archived):
            raise ValidationError({"family": "Choose an active family profile."})
        if self.member_id and (self.member.kind == Profile.Kind.FAMILY or self.member.archived):
            raise ValidationError({"member": "Choose an active child or adult profile."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.family.name}: {self.member.name}"


class Access(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="accesses")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    controller = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    email_alerts = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "guardian access"
        verbose_name_plural = "guardian access grants"
        constraints = [
            models.UniqueConstraint(fields=["profile", "user"], name="one_profile_access"),
            models.UniqueConstraint(
                fields=["profile"],
                condition=models.Q(controller=True, active=True),
                name="one_active_controller",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} — {self.profile.name}"


class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    email = models.EmailField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)


class Item(models.Model):
    class Kind(models.TextChoices):
        ITEM = "item", "Specific item"
        GROUP = "group", "Reusable group of belongings"

    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.ITEM)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=100)  # Private; public text is a separate opt-in.

    def __str__(self):
        return self.name


class Label(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="labels")
    item = models.OneToOneField(Item, on_delete=models.PROTECT, related_name="label")
    print_text = models.CharField(max_length=80, blank=True)
    public_text = models.CharField(max_length=200, blank=True)
    share_text = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.profile_id and self.profile.archived and self.active:
            raise ValidationError({"active": "Restore this profile before enabling its QR codes."})
        if self.item_id and self.item.profile_id != self.profile_id:
            raise ValidationError({"item": "The item must belong to the selected profile."})

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Preserve legacy generic-label callers while giving every label an object.
            if not self.item_id:
                self.item = Item.objects.create(
                    profile=self.profile, name="General belongings", kind=Item.Kind.GROUP
                )
            self.clean()
            super().save(*args, **kwargs)

    def __str__(self):
        return str(self.pk)


class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    submission_id = models.UUIDField()
    message = models.CharField(max_length=1500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["label", "submission_id"], name="one_report")
        ]


class Delivery(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    access = models.ForeignKey(Access, on_delete=models.CASCADE)
    status = models.CharField(max_length=12, default="pending")
    attempts = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "notification delivery"
        verbose_name_plural = "notification deliveries"
        constraints = [models.UniqueConstraint(fields=["report", "access"], name="one_delivery")]
