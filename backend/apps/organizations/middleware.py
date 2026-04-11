from typing import TYPE_CHECKING

from django.db import connection
from django_tenants.middleware.main import TenantMainMiddleware

from apps.users.models import User

if TYPE_CHECKING:
    from django.http.request import HttpRequest


class OrganizationSessionMiddleware(TenantMainMiddleware):
    """For admin/browser requests — reads organization from session."""

    SESSION_KEY = "ORGANIZATION_ID"

    def process_request(self, request: HttpRequest):
        if hasattr(request, "membership"):
            return

        connection.set_schema_to_public()

        user = request.user

        if not user.is_authenticated or not isinstance(user, User):
            self.setup_url_routing(request=request, force_public=True)
            return

        organization_id = request.session.get(self.SESSION_KEY)

        if not organization_id:
            self.setup_url_routing(request=request, force_public=True)
            return

        membership = (
            user.memberships.select_related("organization")
            .filter(organization_id=organization_id)
            .first()
        )

        if not membership:
            self.setup_url_routing(request=request, force_public=True)
            return

        request.tenant = membership.organization
        request.membership = membership
        connection.set_tenant(request.tenant)
        self.setup_url_routing(request)
