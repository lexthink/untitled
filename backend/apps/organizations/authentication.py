from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import connection
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth

if TYPE_CHECKING:
    from django.http import HttpRequest


class OrganizationJWTAuth(JWTAuth):
    """
    Authenticates the user via JWT, then resolves the organization
    from the X-Organization-ID header and activates the organization schema.
    """

    HEADER = "HTTP_X_ORGANIZATION_ID"

    def authenticate(self, request: HttpRequest, token: str):
        connection.set_schema_to_public()

        user = super().authenticate(request, token)
        if user is None:
            return None

        organization_id = request.META.get(self.HEADER)
        if not organization_id:
            return user

        membership = user.memberships.select_related("organization").filter(organization_id=organization_id).first()

        if not membership:
            msg = "You are not a member of this organization."
            raise HttpError(403, msg)

        request.tenant = membership.organization  # required by django-tenants
        request.membership = membership
        connection.set_tenant(membership.organization)

        return user
