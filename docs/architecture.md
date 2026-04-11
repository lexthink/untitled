# Architecture

## Multi-tenancy

This project uses [django-tenants](https://github.com/django-tenants/django-tenants) for PostgreSQL schema-based multi-tenancy. Each organization gets its own PostgreSQL schema with isolated data.

### Schemas

- **public** — shared data: users, organizations, memberships
- **Per-organization schemas** — isolated data: locations (and future organization-specific models)

### Models

| Model | Schema | Description |
|---|---|---|
| User | public | Authentication, shared across all organizations |
| Organization | public | Represents an organization, maps to a PostgreSQL schema |
| Membership | public | Links users to organizations with a role |
| Domain | public | Required by django-tenants (not actively used) |
| Location | organization | Example organization model, isolated per organization |

### How it works

1. A request comes in with an `X-Organization-ID` header (API) or a session value (admin)
2. The system looks up the user's membership in that organization
3. If valid, the PostgreSQL `search_path` is set to the organization's schema
4. All subsequent queries in that request hit the organization's schema
5. If no organization is specified, queries hit the public schema only

## Organization context

### API — `OrganizationJWTAuth`

Located in `apps/organizations/authentication.py`. Extends `JWTAuth` to:

1. Validate the JWT token (authenticate the user)
2. Read the `X-Organization-ID` header
3. Verify the user is a member of that organization
4. Activate the organization's schema

```
Authorization: Bearer <token>
X-Organization-ID: <uuid>
```

**Behavior without header:** The user is authenticated but no schema is activated. Endpoints that require organization context will return `403`.

**Behavior with invalid organization:** Returns `403 - You are not a member of this organization.`

### Admin — `OrganizationSessionMiddleware`

Located in `apps/organizations/middleware.py`. For browser/admin requests:

1. Reads `ORGANIZATION_ID` from the Django session
2. Verifies membership
3. Activates the schema

The user selects the organization from a dropdown in the admin header (top left). The selection is stored in the session.

**Behavior without selection:** Public schema only. Organization models (locations) are not visible.

## Authentication

### API

Uses JWT via `django-ninja-jwt`:

- `POST /api/token/pair` — obtain access + refresh tokens (email + password)
- `POST /api/token/refresh` — refresh the access token
- `POST /api/token/verify` — verify token validity

Access token lifetime: 30 minutes. Refresh token: 7 days.

### Admin

Standard Django session authentication (login form).
