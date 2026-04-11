from uuid import UUID  # noqa: TC003

from ninja import Router
from ninja.errors import HttpError

from .schema import MembershipSchema

router = Router(tags=["organizations"])


@router.get("/", response=list[MembershipSchema])
def list_organizations(request):
    """List all organizations the current user belongs to."""
    return request.user.memberships.select_related("organization").order_by(
        "organization__name",
    )


@router.get("/{organization_id}/", response=MembershipSchema)
def retrieve_organization(request, organization_id: UUID):
    """Retrieve the current user's membership in a specific organization."""
    membership = (
        request.user.memberships.select_related("organization").filter(organization_id=organization_id).first()
    )
    if not membership:
        raise HttpError(404, "Organization not found.")
    return membership


@router.patch("/{organization_id}/default/", response=MembershipSchema)
def set_default_organization(request, organization_id: UUID):
    """Set an organization as the default for the current user."""
    membership = (
        request.user.memberships.select_related("organization").filter(organization_id=organization_id).first()
    )
    if not membership:
        raise HttpError(404, "Organization not found.")

    # Clear previous default
    request.user.memberships.filter(is_default=True).update(is_default=False)

    membership.is_default = True
    membership.save(update_fields=["is_default", "updated_at"])
    return membership
