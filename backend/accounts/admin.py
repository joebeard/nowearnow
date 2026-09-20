from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

admin.site.site_url = settings.PUBLIC_BASE_URL
admin.site.site_header = "nowearnow administration"
admin.site.site_title = "nowearnow admin"
admin.site.index_title = "Site management"


@admin.register(User)
class AccountAdmin(UserAdmin):
    fieldsets = (*UserAdmin.fieldsets, ("Notifications", {"fields": ("email_verified",)}))
    readonly_fields = ("email_verified",)
    list_display = ("username", "email", "email_verified", "is_staff", "is_active")
    list_filter = (*UserAdmin.list_filter, "email_verified")
