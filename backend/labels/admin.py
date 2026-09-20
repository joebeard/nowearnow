from django.contrib import admin

from .models import Access, Delivery, Invitation, Item, Label, Profile, Report


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "created_at")
    list_filter = ("kind",)
    search_fields = ("name",)
    readonly_fields = ("id", "created_at")


@admin.register(Access)
class AccessAdmin(admin.ModelAdmin):
    list_display = ("profile", "user", "controller", "active", "email_alerts")
    list_filter = ("active", "controller", "email_alerts")
    autocomplete_fields = ("profile", "user")
    readonly_fields = ("joined_at",)

    def get_readonly_fields(self, request, obj=None):
        return (*self.readonly_fields, "profile", "user") if obj else self.readonly_fields

    def save_model(self, request, obj, form, change):
        from django.utils import timezone

        if change and "active" in form.changed_data and obj.active:
            obj.joined_at = timezone.now()
            obj.email_alerts = False
        super().save_model(request, obj, form, change)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "profile")
    search_fields = ("name",)
    autocomplete_fields = ("profile",)
    readonly_fields = ("id",)

    def get_readonly_fields(self, request, obj=None):
        return (*self.readonly_fields, "profile") if obj else self.readonly_fields


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "item", "active", "share_text")
    list_filter = ("active", "share_text")
    search_fields = ("id", "profile__name", "item__name")
    autocomplete_fields = ("profile", "item")
    readonly_fields = ("id", "token", "created_at")
    fieldsets = (
        ("Assignment", {"fields": ("id", "profile", "item", "active")}),
        (
            "Physical label",
            {"fields": ("print_text",), "description": "Printed text is visible on the sticker."},
        ),
        (
            "Public scan page",
            {
                "fields": ("public_text", "share_text"),
                "description": (
                    "Public text requires explicit guardian authorization. Hidden by default."
                ),
            },
        ),
        ("Internal", {"fields": ("token", "created_at"), "classes": ("collapse",)}),
    )

    def get_readonly_fields(self, request, obj=None):
        # Reassignment could expose existing reports to a different family.
        return (*self.readonly_fields, "profile", "item") if obj else self.readonly_fields


class ReadOnlyRecords(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Invitation)
class InvitationAdmin(ReadOnlyRecords):
    list_display = ("profile", "created_at", "accepted")
    list_filter = ("accepted",)
    exclude = ("id",)


@admin.register(Report)
class ReportAdmin(ReadOnlyRecords):
    list_display = ("id", "label", "created_at")
    readonly_fields = ("id", "label", "message", "created_at")
    exclude = ("submission_id",)
    date_hierarchy = "created_at"


@admin.register(Delivery)
class DeliveryAdmin(ReadOnlyRecords):
    list_display = ("id", "report", "access", "status", "attempts", "updated_at")
    list_filter = ("status",)
