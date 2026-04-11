# Testing Guide

## 1. Clone the repo

```bash
git clone git@github.com:lexthink/untitled.git
cd untitled
```

## 2. Build and start

```bash
just build
just up --detach
```

## 3. Seed the database

```bash
just seed
```

This will:
- Run migrations (public + organization schemas)
- Load users
- Create organizations with their PostgreSQL schemas
- Create memberships (user-organization relationships with roles)
- Load organization-specific data (locations)

## 4. Users

All users have the password: `123456`

| User | Email | Superuser |
|---|---|---|
| Admin | admin@example.com | Yes |
| Santiago Rivera | santiago.rivera@example.com | No |
| Carolina Mendez | carolina.mendez@example.com | No |
| Laura Garcia | laura.garcia@example.com | No |
| Diego Torres | diego.torres@example.com | No |

## 5. Organizations and memberships

### Acme Corp

| User | Role |
|---|---|
| Santiago Rivera | owner |
| Admin | admin |
| Laura Garcia | admin |
| Diego Torres | member |

Locations: **Almacen Principal**, **Oficina Centro**

### Globex Industries

| User | Role |
|---|---|
| Carolina Mendez | owner |
| Admin | admin |
| Laura Garcia | member |

Locations: **Bodega Central**, **Sucursal Norte**, **Punto de Venta Sur**

## 6. What to test

### Admin — Organization switcher

1. Go to http://localhost:8000/admin/
2. Login with any user
3. Use the dropdown (top left) to switch organizations
4. Without an organization selected, no organization data is visible

### Admin — Permissions by role (Acme Corp)

| Action | owner (Santiago) | admin (Laura) | member (Diego) |
|---|---|---|---|
| See Locations | Yes | Yes | Yes |
| Add location | Yes | Yes | No |
| Edit location | Yes | Yes | No |
| Delete location | Yes | No | No |

### Admin — Permissions by role (Globex Industries)

| Action | owner (Carolina) | member (Laura) |
|---|---|---|
| See Locations | Yes | Yes |
| Add location | Yes | No |
| Edit location | Yes | No |
| Delete location | Yes | No |

Note: Admin user is superuser and has full access everywhere regardless of role.

### API — Organization context

The API uses JWT authentication + `X-Organization-ID` header:

```bash
# 1. Get a token
curl -X POST http://localhost:8000/api/token/pair \
  -H "Content-Type: application/json" \
  -d '{"email": "santiago.rivera@example.com", "password": "123456"}'

# 2. List organizations (no header needed)
curl http://localhost:8000/api/organizations/ \
  -H "Authorization: Bearer <access_token>"

# 3. List locations (requires X-Organization-ID)
curl http://localhost:8000/api/locations/ \
  -H "Authorization: Bearer <access_token>" \
  -H "X-Organization-ID: <organization_uuid>"
```

### API — Permissions by role

Same as admin — owner/admin can create and edit, only owner can delete, members can only view. Without the `X-Organization-ID` header, organization endpoints return `403`.

### Organization isolation

1. Login as **Santiago Rivera**, select **Acme Corp** -> sees **Almacen Principal**, **Oficina Centro**
2. Login as **Carolina Mendez**, select **Globex Industries** -> sees **Bodega Central**, **Sucursal Norte**, **Punto de Venta Sur**
3. Login as **Laura Garcia**, switch between organizations -> sees different locations for each
4. Login as **Diego Torres**, select **Acme Corp** -> sees locations but cannot add, edit, or delete
5. Login as **Admin**, select **No organization** -> sees Users, Organizations, Memberships but no locations

### Superuser vs regular users

- **Admin** (superuser) -> sees all admin modules (Users, Organizations, Celery, etc.) regardless of organization
- **Regular users** -> only see organization modules (Locations) when an organization is selected

## 7. Run tests

```bash
just test
```

## 8. Reset everything

```bash
just prune
just up --detach
just seed
```

## Services

| Service  | URL                    | Profile  |
|----------|------------------------|----------|
| Frontend | http://localhost:4321  | frontend |
| Backend  | http://localhost:8000  | backend  |
| Flower   | http://localhost:5555  | backend  |
| Mailpit  | http://localhost:8025  | backend  |
