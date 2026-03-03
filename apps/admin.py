from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.admin_site import custom_admin_site
from apps.models import User

# admin.AdminSite.login()

@admin.register(User, site=custom_admin_site)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("phone", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("first_name", "last_name", "phone")
    ordering = ("phone",)
    fieldsets = (
        (None, {"fields": ("phone",)}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "usable_password", "password1", "password2"),
            },
        ),
    )
