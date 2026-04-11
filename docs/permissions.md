# Permissions

## Roles

Defined in `apps/organizations/enums.py`:

| Role | Description |
|---|---|
| `owner` | Full access, can delete resources |
| `admin` | Can view, create, and edit, but not delete |
| `member` | View only |

A user can have different roles in different organizations.

## API permissions — `require_roles`

Located in `apps/organizations/permissions.py`. A decorator for API views:

```python
from apps.organizations.enums import Role
from apps.organizations.permissions import require_roles

@router.post("/")
@require_roles(Role.OWNER, Role.ADMIN)
def create_location(request, data: LocationInputSchema):
    ...
```

The decorator:
1. Checks that `request.membership` exists (set by `OrganizationJWTAuth`)
2. Checks that the user's role is in the allowed roles
3. Returns `403` if either check fails

### Locations API permissions

| Endpoint | Roles allowed |
|---|---|
| `GET /api/locations/` | owner, admin, member |
| `GET /api/locations/{id}/` | owner, admin, member |
| `POST /api/locations/` | owner, admin |
| `PATCH /api/locations/{id}/` | owner, admin |
| `DELETE /api/locations/{id}/` | owner |

### Organizations API permissions

No role restrictions — any authenticated user can list their own organizations and set a default. The endpoints only return data for organizations the user belongs to.

## Admin permissions — `OrganizationAdminMixin`

Located in `apps/organizations/mixins.py`. A mixin for `ModelAdmin` classes:

```python
from apps.organizations.enums import Role
from apps.organizations.mixins import OrganizationAdminMixin

@admin.register(Location)
class LocationAdmin(OrganizationAdminMixin, admin.ModelAdmin):
    view_roles = (Role.OWNER, Role.ADMIN, Role.MEMBER)
    add_roles = (Role.OWNER, Role.ADMIN)
    change_roles = (Role.OWNER, Role.ADMIN)
    delete_roles = (Role.OWNER,)
```

Each property defines which roles can perform that action. If empty, only superusers have access.

### How it works

- The middleware sets `request.membership` with the active organization's membership
- The mixin checks `request.membership.role` against the allowed roles
- Superusers bypass all checks

### Models without the mixin

Any `ModelAdmin` without `OrganizationAdminMixin` is only visible to superusers (Users, Organizations, Celery Beat, etc.).
