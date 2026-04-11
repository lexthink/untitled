# Multi-tenant Considerations

> **Note:** These are recommendations for future implementation. Not all are implemented yet.

## Backups

A full database backup (`pg_dump`) includes all schemas automatically. For organization-specific backups:

```bash
# Backup a single organization
pg_dump --schema=schema_vkojrfv6lz_0006 -Fc dbname > acme_backup.dump

# Restore a single organization
pg_restore --schema=schema_vkojrfv6lz_0006 -d dbname acme_backup.dump
```

Always backup the `public` schema alongside organization schemas — it contains users, organizations, and memberships that the organization data depends on.

## Rate limiting

Without rate limiting, a single organization can consume all resources (API requests, Celery workers, database connections).

Implement per-organization throttling in the API:

```python
from ninja.throttling import BaseThrottle

class OrganizationThrottle(BaseThrottle):
    rate = "100/minute"

    def get_cache_key(self, request):
        membership = getattr(request, "membership", None)
        if membership:
            return f"throttle:org:{membership.organization.pk}"
        return None
```

Apply it to the API:

```python
api = NinjaExtraAPI(
    throttle=[OrganizationThrottle()],
)
```

Consider different limits per organization (free vs paid tiers) by storing the limit on the Organization model.

## Soft delete

Never hard-delete data in production. Use soft delete instead:

### Users

```python
# Don't do this
user.delete()

# Do this
user.is_active = False
user.save()
```

An inactive user can't login but their data references (`created_by`, etc.) remain intact.

### Organizations

Add a `deleted_at` field to Organization:

```python
class Organization(AbstractModel, TenantMixin):
    name = CharField(...)
    deleted_at = DateTimeField(null=True, default=None)
```

A soft-deleted organization:
- Is excluded from queries (`Organization.objects.filter(deleted_at__isnull=True)`)
- Its schema still exists in PostgreSQL
- Can be restored by setting `deleted_at = None`
- After a grace period (e.g. 30 days), a background task can hard-delete it with `DROP SCHEMA CASCADE`

### Hard delete (irreversible)

`DROP SCHEMA CASCADE` permanently deletes all organization data. Use only after the grace period:

```python
from django.db import connection

def hard_delete_organization(organization):
    schema_name = organization.schema_name
    organization.delete()  # removes from public schema
    with connection.cursor() as cursor:
        cursor.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE")
```

## Cache

Django-tenants provides a `KEY_FUNCTION` that automatically prefixes all cache keys with the current schema name. This is already configured in both local and production settings:

```python
CACHES = {
    "default": {
        ...
        "KEY_FUNCTION": "django_tenants.cache.make_key",
        "REVERSE_KEY_FUNCTION": "django_tenants.cache.reverse_key",
    },
}
```

With this, you don't need to manually scope cache keys. Django handles it:

```python
from django.core.cache import cache

# Inside an organization context, this key is automatically prefixed
# with the schema name (e.g. "schema_vkojrfv6lz_0006:locations_count")
cache.set("locations_count", count)
cache.get("locations_count")  # returns count for the current organization only
```

No risk of collision between organizations — each schema gets its own cache namespace.

## File uploads

Files uploaded by users must be isolated per organization in storage (S3, local, etc.):

```python
def organization_upload_path(instance, filename):
    from django.db import connection
    return f"{connection.schema_name}/uploads/{filename}"

class Document(AbstractModel):
    file = FileField(upload_to=organization_upload_path)
```

This creates paths like:
- `schema_vkojrfv6lz_0006/uploads/report.pdf` (Acme Corp)
- `schema_z0207t1shm_3579/uploads/report.pdf` (Globex Industries)

Benefits:
- No filename collisions between organizations
- Easy to backup/delete files for a single organization
- Can set different S3 bucket policies per organization prefix

## Signals

Django signals don't carry organization context. If a signal triggers a Celery task or accesses organization data, pass the context explicitly:

```python
# Wrong — no organization context in the task
@receiver(post_save, sender=Location)
def on_location_created(sender, instance, created, **kwargs):
    if created:
        notify_admins.delay(instance.pk)  # which organization?

# Correct — pass organization context
@receiver(post_save, sender=Location)
def on_location_created(sender, instance, created, **kwargs):
    if created:
        from django.db import connection
        from apps.organizations.models import Organization

        organization = Organization.objects.get(schema_name=connection.schema_name)
        notify_admins.on(organization).delay(instance.pk)
```

Alternatively, get the organization from the current connection:

```python
from django.db import connection

def get_current_organization():
    """Returns the active organization based on the current schema."""
    if connection.schema_name == "public":
        return None
    from apps.organizations.models import Organization
    return Organization.objects.get(schema_name=connection.schema_name)
```

This helper can be useful in signals, model methods, or anywhere outside of request context.
