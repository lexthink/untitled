from uuid import UUID  # noqa: TC003

from ninja import ModelSchema
from ninja import Schema

from apps.organizations.enums import Role  # noqa: TC001
from apps.organizations.models import Organization


class OrganizationSchema(ModelSchema):
    class Meta:
        model = Organization
        fields = ["id", "name"]


class MembershipSchema(Schema):
    id: UUID
    organization: OrganizationSchema
    role: Role
    is_default: bool
