from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.db import connection
from django.test import Client
from ninja_jwt.tokens import AccessToken

from apps.organizations.enums import Role
from apps.organizations.models import Membership
from apps.organizations.models import Organization
from tests.users.factories import UserFactory

if TYPE_CHECKING:
    from apps.users.models import User


@pytest.fixture(autouse=True)
def _media_storage(settings, tmpdir) -> None:
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture(scope="session")
def organization(django_db_setup, django_db_blocker) -> Organization:
    """Creates a single organization with schema, reused across all tests."""
    with django_db_blocker.unblock():
        org, _ = Organization.objects.get_or_create(
            schema_name="test_org",
            defaults={"name": "Test Organization"},
        )
        connection.set_schema_to_public()
    return org


@pytest.fixture(scope="session")
def other_organization(django_db_setup, django_db_blocker) -> Organization:
    """A second organization for tenant isolation tests."""
    with django_db_blocker.unblock():
        org, _ = Organization.objects.get_or_create(
            schema_name="test_other_org",
            defaults={"name": "Other Organization"},
        )
        connection.set_schema_to_public()
    return org


@pytest.fixture
def user(db) -> User:
    return UserFactory.create()


@pytest.fixture
def http_client(db) -> tuple[Client, User, None]:
    """Returns a Client with JWT auth, no organization."""
    user = UserFactory.create()
    return make_http_client(user)


def make_http_client(
    user: User,
    organization: Organization | None = None,
    role: Role = Role.OWNER,
) -> tuple[Client, User, Membership | None]:
    """Helper to create an authenticated client with optional org context."""
    token = str(AccessToken.for_user(user))
    headers = {"authorization": f"Bearer {token}"}
    membership = None

    if organization:
        membership, _ = Membership.objects.get_or_create(
            user=user,
            organization=organization,
            defaults={"role": role},
        )
        headers["x-organization-id"] = str(organization.pk)

    return Client(headers=headers), user, membership
