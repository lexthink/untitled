from django.contrib import admin

from apps.organizations.enums import Role
from apps.organizations.mixins import OrganizationAdminMixin

from .models import Location


@admin.register(Location)
class LocationAdmin(OrganizationAdminMixin, admin.ModelAdmin):
    view_roles = (Role.OWNER, Role.ADMIN, Role.MEMBER)
    add_roles = (Role.OWNER, Role.ADMIN)
    change_roles = (Role.OWNER, Role.ADMIN)
    delete_roles = (Role.OWNER,)

    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)
