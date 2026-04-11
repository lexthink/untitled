from __future__ import annotations

from factory import Faker
from factory import SubFactory
from factory.django import DjangoModelFactory

from apps.organizations.enums import Role
from apps.organizations.models import Membership
from apps.organizations.models import Organization
from tests.users.factories import UserFactory


class OrganizationFactory(DjangoModelFactory[Organization]):
    name = Faker("company")
    schema_name = "test_org"
    auto_create_schema = False

    class Meta:
        model = Organization
        django_get_or_create = ["schema_name"]


class MembershipFactory(DjangoModelFactory[Membership]):
    user = SubFactory(UserFactory)
    organization = SubFactory(OrganizationFactory)
    role = Role.MEMBER

    class Meta:
        model = Membership
        django_get_or_create = ["user", "organization"]
