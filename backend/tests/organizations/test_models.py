import pytest
from django.db import IntegrityError

from apps.organizations.enums import Role
from apps.organizations.models import Membership
from tests.organizations.factories import MembershipFactory
from tests.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestMembership:
    def test_first_membership_is_default(self, organization):
        membership = MembershipFactory.create(
            user=UserFactory.create(),
            organization=organization,
            role=Role.MEMBER,
        )
        assert membership.is_default is True

    def test_second_membership_is_not_default(self, organization, other_organization):
        user = UserFactory.create()
        MembershipFactory.create(user=user, organization=organization, role=Role.MEMBER)
        membership2 = MembershipFactory.create(
            user=user,
            organization=other_organization,
            role=Role.MEMBER,
        )
        assert membership2.is_default is False

    def test_unique_constraint(self):
        membership = MembershipFactory.create()
        with pytest.raises(IntegrityError):
            Membership.objects.create(
                user=membership.user,
                organization=membership.organization,
                role=Role.ADMIN,
            )

    def test_str(self):
        membership = MembershipFactory.create(role=Role.OWNER)
        assert str(membership.organization) in str(membership)
        assert str(membership.user) in str(membership)
        assert "owner" in str(membership)
