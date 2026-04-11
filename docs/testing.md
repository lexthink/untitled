# Testing

## Running tests

```bash
just test                                          # all tests
just test tests/locations/                         # one app
just test tests/locations/api/test_views.py        # one file
just test tests/locations/api/test_views.py -k create  # by keyword
```

## Test fixtures

### Session-scoped organizations

Defined in `tests/conftest.py`. Two organizations are created once per test session and reused across all tests:

- `organization` — schema `test_org`
- `other_organization` — schema `test_other_org`

These avoid creating PostgreSQL schemas in every test, keeping tests fast (~1.5s for 55 tests).

### `http_client`

Returns a Django test `Client` with JWT authentication, no organization context:

```python
def test_something(self, http_client):
    client, user, _ = http_client
    response = client.get("/api/users/me/")
```

### `make_http_client`

A helper function for creating clients with organization context and specific roles:

```python
from tests.conftest import make_http_client

# Owner (default)
client, user, membership = make_http_client(UserFactory.create(), organization)

# Admin role
client, user, membership = make_http_client(UserFactory.create(), organization, Role.ADMIN)

# Member role
client, user, membership = make_http_client(UserFactory.create(), organization, Role.MEMBER)

# No organization
client, user, _ = make_http_client(UserFactory.create())
```

## Working with organization data in tests

Organization models (Location, etc.) need `tenant_context` to create and query data:

```python
from django_tenants.utils import tenant_context

def test_create_location(self, organization):
    client, *_ = make_http_client(UserFactory.create(), organization)

    # Create test data in the organization schema
    with tenant_context(organization):
        LocationFactory.create_batch(3)

    # API requests activate the schema automatically via OrganizationJWTAuth
    response = client.get("/api/locations/")

    # Assertions about organization data need tenant_context
    with tenant_context(organization):
        assert Location.objects.count() == 3
```

### Schema reset

Tests that use organization context should reset to public schema after each test:

```python
@pytest.fixture(autouse=True)
def _reset_schema():
    yield
    connection.set_schema_to_public()
```

This is already included in `tests/locations/api/test_views.py`.

## Factories

### OrganizationFactory

Uses `auto_create_schema=False` and always returns the same organization (`test_org` schema). This avoids creating new schemas in tests:

```python
from tests.organizations.factories import OrganizationFactory, MembershipFactory

organization = OrganizationFactory.create()  # returns existing test_org
membership = MembershipFactory.create(user=user, organization=organization, role=Role.ADMIN)
```

### LocationFactory

Creates locations in the **current active schema**. Must be used inside `tenant_context`:

```python
with tenant_context(organization):
    location = LocationFactory.create(name="My Location")
```

## Testing permissions

Use `make_http_client` with different roles to verify permission enforcement:

```python
def test_member_cannot_create(self, organization):
    client, *_ = make_http_client(UserFactory.create(), organization, Role.MEMBER)

    response = client.post(
        "/api/locations/",
        data='{"name": "Nope"}',
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

def test_owner_can_delete(self, organization):
    client, *_ = make_http_client(UserFactory.create(), organization, Role.OWNER)
    with tenant_context(organization):
        location = LocationFactory.create()

    response = client.delete(f"/api/locations/{location.pk}/")

    assert response.status_code == HTTPStatus.NO_CONTENT
```
