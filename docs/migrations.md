# Migrations

## How migrations work with multi-tenancy

Django-tenants uses a router (`TenantSyncRouter`) that determines which migrations run on which schemas:

- **Shared apps** (users, organizations, memberships) — migrate only on `public` schema
- **Organization apps** (locations) — migrate on every organization schema

This is controlled by `SHARED_APPS` and `TENANT_APPS` in `config/settings/base.py`.

## Creating migrations

Same as standard Django:

```bash
just manage makemigrations
```

This generates migration files. The router decides where they run at migrate time — you don't need to do anything special when creating them.

### Adding a new shared model

1. Create the model in an app listed in `SHARED_APPS`
2. Run `just manage makemigrations`
3. Run `just manage migrate` — runs on `public` schema only

### Adding a new organization model

1. Create the model in an app listed in `TENANT_APPS`
2. Run `just manage makemigrations`
3. Run `just manage migrate` — runs on **every** organization schema

### Adding a new app

If the app has models that should be isolated per organization:

1. Add it to `TENANT_APPS` in `config/settings/base.py`
2. Add `OrganizationAdminMixin` to its `ModelAdmin` classes
3. Use `require_roles` decorator on its API views

If the app has shared models:

1. Add it to `SHARED_APPS` in `config/settings/base.py`

## Running migrations

### Local

```bash
just manage migrate
```

Django-tenants replaces the default `migrate` command. It:

1. Migrates the `public` schema (shared apps)
2. Migrates each organization schema (organization apps)

### Production

```bash
docker compose -f docker-compose.production.yaml run --rm backend python manage.py migrate
```

Same behavior — migrates public first, then each organization schema.

### Migration order matters

When deploying, **always run migrations before starting the new code**. If the new code expects a column that doesn't exist yet, requests will fail.

```bash
# 1. Build new image
docker compose -f docker-compose.production.yaml build

# 2. Run migrations (with old containers still running)
docker compose -f docker-compose.production.yaml run --rm backend python manage.py migrate

# 3. Restart with new code
docker compose -f docker-compose.production.yaml up -d
```

## Checking migration status

```bash
# All migrations
just manage showmigrations

# Specific app
just manage showmigrations locations
```

## Common scenarios

### New organization has no tables

When a new organization is created (via admin, API, or seed), `auto_create_schema=True` on the `Organization` model triggers:

1. `CREATE SCHEMA <schema_name>` in PostgreSQL
2. Runs all `TENANT_APPS` migrations on the new schema

No manual migration needed.

### Adding a field to an organization model

```bash
# 1. Add field to model
# 2. Create migration
just manage makemigrations

# 3. Run migration — applies to ALL organization schemas
just manage migrate
```

If you have 100 organizations, the migration runs 100 times. Keep migrations fast — avoid data migrations on large tables.

### Renaming a model or field

Same as standard Django. The migration runs on each organization schema automatically.

### Data migrations

Data migrations in organization apps run per schema. Use `schema_context` if you need to reference specific schemas:

```python
from django.db import migrations

def forward(apps, schema_editor):
    Location = apps.get_model("locations", "Location")
    # This runs in the current schema context (each org schema)
    Location.objects.filter(name="").update(name="Default")

class Migration(migrations.Migration):
    dependencies = [("locations", "0001_initial")]
    operations = [migrations.RunPython(forward, migrations.RunPython.noop)]
```

### Parallel migrations

By default, migrations run on each schema sequentially. With many organizations this can be slow. Run them in parallel with:

```bash
just manage migrate_schemas --executor=multiprocessing
```

Configure in `config/settings/base.py`:

```python
TENANT_MULTIPROCESSING_MAX_PROCESSES = 2  # max parallel workers (avoid exhausting DB connections)
TENANT_MULTIPROCESSING_CHUNKS = 2         # migrations sent to each worker at once
```

Keep the defaults low to avoid overwhelming the database connection pool. Increase only if your DB can handle it.

### Squashing migrations

Works the same as standard Django:

```bash
just manage squashmigrations locations 0001 0005
```

The squashed migration will run on each organization schema.
