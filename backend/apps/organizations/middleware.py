from typing import TYPE_CHECKING

from django.db import connection
from django.utils.deprecation import MiddlewareMixin

from apps.users.models import User

if TYPE_CHECKING:
    from django.http.request import HttpRequest


class OrganizationSessionMiddleware(MiddlewareMixin):
    """For admin/browser requests — reads organization from session."""

    SESSION_KEY = "ORGANIZATION_ID"

    def process_request(self, request: HttpRequest):
        if hasattr(request, "membership"):
            return

        connection.set_schema_to_public()

        user = request.user

        if not user.is_authenticated or not isinstance(user, User):
            return

        organization_id = request.session.get(self.SESSION_KEY)
        if not organization_id:
            return

        membership = user.memberships.select_related("organization").filter(organization_id=organization_id).first()

        if not membership:
            return

        request.tenant = membership.organization  # required by django-tenants
        request.membership = membership
        connection.set_tenant(membership.organization)
