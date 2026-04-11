from .middleware import OrganizationSessionMiddleware
from .models import Organization


def active_organization(request):
    if not hasattr(request, "user") or not request.user.is_authenticated:
        return {}

    organizations = Organization.objects.filter(
        memberships__user=request.user,
    ).order_by("name")

    org_id = request.session.get(OrganizationSessionMiddleware.SESSION_KEY)
    active_org = None
    if org_id:
        active_org = organizations.filter(pk=org_id).first()

    return {
        "user_organizations": organizations,
        "active_organization": active_org,
    }
