# Seed Command

The `seed` management command populates the database with fixture data for local development.

## Usage

```bash
just seed
```

This runs `migrate` + `seed` and creates:
1. Users from `fixtures/users.json`
2. Organizations with their PostgreSQL schemas from `fixtures/organizations.json`
3. Memberships (user-organization relationships with roles)
4. Organization-specific data from `fixtures/<schema_name>.json`

## Fixture files

Located in `backend/fixtures/`:

```
fixtures/
├── users.json                        # shared users (public schema)
├── organizations.json                # organizations + memberships
├── schema_vkojrfv6lz_0006.json      # Acme Corp data (locations)
└── schema_z0207t1shm_3579.json      # Globex Industries data (locations)
```

## How it works

The seed command uses `get_or_create` everywhere, so it's **idempotent** — safe to run multiple times without duplicating data.

### 1. Users (`users.json`)

Standard Django fixture loaded with `loaddata`. Each user has a pre-hashed password.

```json
{
  "model": "users.user",
  "pk": "e531d437-...",
  "fields": {
    "password": "argon2$...",
    "email": "admin@example.com",
    "name": "Admin",
    "is_superuser": true,
    "is_staff": true
  }
}
```

### 2. Organizations (`organizations.json`)

Not loaded with `loaddata` — created via ORM to trigger `auto_create_schema=True`, which runs `CREATE SCHEMA` + migrations in PostgreSQL. Memberships are embedded in the same file:

```json
{
  "model": "organizations.organization",
  "pk": "3ceabf4e-...",
  "fields": {
    "schema_name": "schema_vkojrfv6lz_0006",
    "name": "Acme Corp",
    "memberships": [
      {"user": "bfdc4156-...", "role": "owner", "is_default": true},
      {"user": "e531d437-...", "role": "admin", "is_default": true}
    ]
  }
}
```

### 3. Organization data (`<schema_name>.json`)

Standard Django fixtures loaded with `loaddata` inside a `tenant_context`. The seed command matches the filename to the organization's `schema_name`:

```json
[
  {
    "model": "locations.location",
    "pk": "3ba168a8-...",
    "fields": {
      "name": "Almacen Principal"
    }
  }
]
```

## Adding new seed data

### Add a new user

Add an entry to `fixtures/users.json`. Use an existing password hash (all test users share the same password `123456`):

```json
{
  "model": "users.user",
  "pk": "NEW-UUID-HERE",
  "fields": {
    "password": "argon2$argon2id$v=19$m=102400,t=2,p=8$Z0FpRW02TmxIOEhoMk1ja0xTTE81SA$8JEJ6f9Ae5xV6x1IuLENmepKD6cR5pyLrKvqfB8aZog",
    "email": "newuser@example.com",
    "name": "New User",
    "is_superuser": false,
    "is_staff": true,
    "is_active": true,
    "date_joined": "2026-04-11T00:00:00.000Z",
    "created_at": "2026-04-11T00:00:00.000Z",
    "updated_at": "2026-04-11T00:00:00.000Z",
    "groups": [],
    "user_permissions": []
  }
}
```

### Add a user to an organization

Add a membership entry inside the organization's `memberships` array in `fixtures/organizations.json`:

```json
{"user": "NEW-UUID-HERE", "role": "member", "is_default": true}
```

### Add a new organization

Add an entry to `fixtures/organizations.json` with a unique `schema_name`:

```json
{
  "model": "organizations.organization",
  "pk": "NEW-ORG-UUID",
  "fields": {
    "schema_name": "schema_new_org_0001",
    "name": "New Organization",
    "memberships": [
      {"user": "SOME-USER-UUID", "role": "owner", "is_default": true}
    ]
  }
}
```

Then create a fixture file for its data: `fixtures/schema_new_org_0001.json`.

### Add data to an existing organization

Edit the corresponding `fixtures/<schema_name>.json` file. Add entries for any model in `TENANT_APPS`:

```json
{
  "model": "locations.location",
  "pk": "NEW-LOCATION-UUID",
  "fields": {
    "name": "New Location",
    "created_at": "2026-04-11T00:00:00.000Z",
    "updated_at": "2026-04-11T00:00:00.000Z"
  }
}
```

### Dump existing data to fixtures

```bash
# Shared data (users)
just manage dumpdata users.User --indent 2 --output fixtures/users.json

# Organization data (need tenant_command)
just manage tenant_command dumpdata --schema=<schema_name> locations --indent 2 --output fixtures/<schema_name>.json
```

## Reset and re-seed

```bash
just prune           # remove all containers and volumes
just up --detach     # start fresh containers
just seed            # migrate + seed
```
