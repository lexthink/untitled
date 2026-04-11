from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from django.db import connection
from django_tenants.utils import tenant_context

from apps.locations.models import Location
from apps.organizations.enums import Role
from tests.conftest import make_http_client
from tests.locations.factories import LocationFactory
from tests.users.factories import UserFactory

if TYPE_CHECKING:
    from django.test import Client

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _reset_schema():
    """Reset to public schema after each test."""
    yield
    connection.set_schema_to_public()


class TestListLocations:
    def test_list_locations(self, organization):
        client, *_ = make_http_client(UserFactory.create(), organization)
        with tenant_context(organization):
            LocationFactory.create_batch(3)

        response = client.get("/api/locations/")

        assert response.status_code == HTTPStatus.OK
        assert len(response.json()) == 3  # noqa: PLR2004

    def test_member_can_list(self, organization):
        client, *_ = make_http_client(UserFactory.create(), organization, Role.MEMBER)
        with tenant_context(organization):
            LocationFactory.create()

        response = client.get("/api/locations/")

        assert response.status_code == HTTPStatus.OK

    def test_tenant_isolation(self, organization, other_organization):
        client, *_ = make_http_client(UserFactory.create(), organization)

        with tenant_context(organization):
            LocationFactory.create(name="My Location")
        with tenant_context(other_organization):
            LocationFactory.create(name="Other Location")

        response = client.get("/api/locations/")

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "My Location"

    def test_without_org_header(self, http_client):
        client, *_ = http_client

        response = client.get("/api/locations/")

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_unauthenticated(self, client: Client):
        response = client.get("/api/locations/")
        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestRetrieveLocation:
    def test_retrieve(self, organization):
        client, *_ = make_http_client(UserFactory.create(), organization)
        with tenant_context(organization):
            location = LocationFactory.create()

        response = client.get(f"/api/locations/{location.pk}/")

        assert response.status_code == HTTPStatus.OK
        assert response.json()["name"] == location.name

    def test_not_found(self, organization):
        client, *_ = make_http_client(UserFactory.create(), organization)

        response = client.get(f"/api/locations/{uuid4()}/")

        assert response.status_code == HTTPStatus.NOT_FOUND


class TestCreateLocation:
    def test_owner_can_create(self, organization):
        client, *_ = make_http_client(UserFactory.create(), organization, Role.OWNER)

        response = client.post(
            "/api/locations/",
            data='{"name": "Owner Location"}',
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.CREATED

    def test_admin_can_create(self, organization):
        client, *_ = make_http_client(UserFactory.create(), organization, Role.ADMIN)

        response = client.post(
            "/api/locations/",
            data='{"name": "Admin Location"}',
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.CREATED

    def test_member_cannot_create(self, organization):
        client, *_ = make_http_client(UserFactory.create(), organization, Role.MEMBER)

        response = client.post(
            "/api/locations/",
            data='{"name": "Member Location"}',
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_create_in_correct_tenant(self, organization, other_organization):
        client, *_ = make_http_client(UserFactory.create(), organization)

        client.post(
            "/api/locations/",
            data='{"name": "Tenant Location"}',
            content_type="application/json",
        )

        with tenant_context(organization):
            assert Location.objects.filter(name="Tenant Location").exists()
        with tenant_context(other_organization):
            assert not Location.objects.filter(name="Tenant Location").exists()


class TestUpdateLocation:
    def test_owner_can_update(self, organization):
        client, *_ = make_http_client(UserFactory.create(), organization, Role.OWNER)
        with tenant_context(organization):
            location = LocationFactory.create(name="Old")

        response = client.patch(
            f"/api/locations/{location.pk}/",
            data='{"name": "Updated"}',
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json()["name"] == "Updated"

    def test_admin_can_update(self, organization):
        client, *_ = make_http_client(UserFactory.create(), organization, Role.ADMIN)
        with tenant_context(organization):
            location = LocationFactory.create(name="Old")

        response = client.patch(
            f"/api/locations/{location.pk}/",
            data='{"name": "Updated"}',
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.OK

    def test_member_cannot_update(self, organization):
        client, *_ = make_http_client(UserFactory.create(), organization, Role.MEMBER)
        with tenant_context(organization):
            location = LocationFactory.create()

        response = client.patch(
            f"/api/locations/{location.pk}/",
            data='{"name": "Nope"}',
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_not_found(self, organization):
        client, *_ = make_http_client(UserFactory.create(), organization)

        response = client.patch(
            f"/api/locations/{uuid4()}/",
            data='{"name": "Nope"}',
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.NOT_FOUND


class TestDeleteLocation:
    def test_owner_can_delete(self, organization):
        client, *_ = make_http_client(UserFactory.create(), organization, Role.OWNER)
        with tenant_context(organization):
            location = LocationFactory.create()

        response = client.delete(f"/api/locations/{location.pk}/")

        assert response.status_code == HTTPStatus.NO_CONTENT

        with tenant_context(organization):
            assert not Location.objects.filter(pk=location.pk).exists()

    def test_admin_cannot_delete(self, organization):
        client, *_ = make_http_client(UserFactory.create(), organization, Role.ADMIN)
        with tenant_context(organization):
            location = LocationFactory.create()

        response = client.delete(f"/api/locations/{location.pk}/")

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_member_cannot_delete(self, organization):
        client, *_ = make_http_client(UserFactory.create(), organization, Role.MEMBER)
        with tenant_context(organization):
            location = LocationFactory.create()

        response = client.delete(f"/api/locations/{location.pk}/")

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_not_found(self, organization):
        client, *_ = make_http_client(UserFactory.create(), organization)

        response = client.delete(f"/api/locations/{uuid4()}/")

        assert response.status_code == HTTPStatus.NOT_FOUND
