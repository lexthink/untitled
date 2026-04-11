from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from apps.organizations.enums import Role
from tests.organizations.factories import MembershipFactory
from tests.users.factories import UserFactory

if TYPE_CHECKING:
    from django.test import Client

pytestmark = pytest.mark.django_db


class TestListOrganizations:
    def test_list_own_organizations(
        self,
        http_client,
        organization,
        other_organization,
    ):
        client, user, _ = http_client
        MembershipFactory.create(user=user, organization=organization, role=Role.OWNER)
        MembershipFactory.create(
            user=user,
            organization=other_organization,
            role=Role.MEMBER,
        )

        response = client.get("/api/organizations/")

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 2  # noqa: PLR2004

    def test_does_not_list_other_users_organizations(self, http_client, organization):
        client, *_ = http_client
        other_user = UserFactory.create()
        MembershipFactory.create(
            user=other_user,
            organization=organization,
            role=Role.OWNER,
        )

        response = client.get("/api/organizations/")

        assert response.status_code == HTTPStatus.OK
        assert len(response.json()) == 0

    def test_unauthenticated(self, client: Client):
        response = client.get("/api/organizations/")
        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestRetrieveOrganization:
    def test_retrieve_own_membership(self, http_client, organization):
        client, user, _ = http_client
        MembershipFactory.create(user=user, organization=organization, role=Role.ADMIN)

        response = client.get(f"/api/organizations/{organization.pk}/")

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data["organization"]["name"] == organization.name
        assert data["role"] == Role.ADMIN

    def test_not_a_member(self, http_client, organization):
        client, *_ = http_client

        response = client.get(f"/api/organizations/{organization.pk}/")

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_nonexistent_org(self, http_client):
        client, *_ = http_client

        response = client.get(f"/api/organizations/{uuid4()}/")

        assert response.status_code == HTTPStatus.NOT_FOUND


class TestSetDefaultOrganization:
    def test_set_default(self, http_client, organization, other_organization):
        client, user, _ = http_client
        m1 = MembershipFactory.create(
            user=user,
            organization=organization,
            role=Role.OWNER,
        )
        MembershipFactory.create(
            user=user,
            organization=other_organization,
            role=Role.MEMBER,
        )

        assert m1.is_default is True

        response = client.patch(f"/api/organizations/{other_organization.pk}/default/")

        assert response.status_code == HTTPStatus.OK
        assert response.json()["is_default"] is True

        m1.refresh_from_db()
        assert m1.is_default is False

    def test_set_default_not_a_member(self, http_client, organization):
        client, *_ = http_client

        response = client.patch(f"/api/organizations/{organization.pk}/default/")

        assert response.status_code == HTTPStatus.NOT_FOUND
