from django.contrib.admin.views.decorators import staff_member_required
from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

from apps.organizations.authentication import OrganizationJWTAuth

api = NinjaExtraAPI(
    urls_namespace="api",
    auth=OrganizationJWTAuth(),
    docs_decorator=staff_member_required,
)

api.register_controllers(NinjaJWTDefaultController)
api.add_router("/users/", "apps.users.api.views.router")
api.add_router("/organizations/", "apps.organizations.api.views.router")
api.add_router("/locations/", "apps.locations.api.views.router")
