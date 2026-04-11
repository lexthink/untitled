# Celery Tasks with Organization Context

Celery workers run outside of HTTP requests — they don't have middleware or authentication. Tasks that access organization data need to activate the organization schema manually.

## OrganizationTask

Located in `apps/organizations/tasks.py`. A base task class that handles schema activation:

```python
from celery import shared_task
from apps.organizations.tasks import OrganizationTask

@shared_task(base=OrganizationTask)
def send_report(location_id):
    # organization schema is already active
    location = Location.objects.get(id=location_id)
    ...
```

The first argument is always the `organization_id` (as a string). It's intercepted by `OrganizationTask.__call__` and never reaches the task function.

The result is automatically wrapped with the organization context:

```json
{
    "organization": {
        "id": "3ceabf4e-...",
        "name": "Acme Corp",
        "schema_name": "schema_vkojrfv6lz_0006"
    },
    "result": <task return value>
}
```

With `bind=True`, you can access the organization inside the task via `self.organization`:

```python
@shared_task(base=OrganizationTask, bind=True)
def send_report(self, location_id):
    print(self.organization.id)
    print(self.organization.name)
    print(self.organization.schema_name)
    ...
```

## Calling tasks

Use `.on(organization)` to prepend the organization ID (recommended):

```python
# From a view
send_report.on(request.membership.organization).delay(location_id)

# From another task
send_report.on(organization).delay(location_id)

# From a management command
for organization in Organization.objects.all():
    send_report.on(organization).delay(location_id)
```

You can also pass the organization ID manually as the first argument:

```python
send_report.delay(str(organization.pk), location_id)
```

Both are equivalent. `.on()` is a helper to avoid calling `str(organization.pk)` every time. Calling `.delay()` without an organization ID will fail.

### With options

```python
# Execute after 60 seconds
send_report.on(organization).apply_async(args=[location_id], countdown=60)

# Execute at a specific time
send_report.on(organization).apply_async(args=[location_id], eta=datetime(...))

# Execute in a specific queue
send_report.on(organization).apply_async(args=[location_id], queue="high_priority")

# With kwargs
send_report.on(organization).delay(location_id, key="value")
```

## Shared vs organization tasks

Not all tasks need organization context. Tasks that work with public schema data (users, memberships) don't need `OrganizationTask`:

```python
# Shared task — no OrganizationTask needed
@shared_task
def send_welcome_email(user_id):
    user = User.objects.get(pk=user_id)
    ...

# Organization task — needs OrganizationTask
@shared_task(base=OrganizationTask)
def generate_report():
    locations = Location.objects.all()
    ...
```

## Tasks that iterate organizations

If you need to run something for all organizations (e.g. nightly reports), dispatch one task per organization:

```python
# Dispatcher — runs once, dispatches per org
@shared_task
def nightly_reports():
    for organization in Organization.objects.all():
        generate_report.on(organization).delay()

# Actual work — runs per org
@shared_task(base=OrganizationTask)
def generate_report():
    ...
```

Don't process all organizations in a single task with a loop — if it fails midway, remaining organizations are skipped.

## Scheduled tasks (Celery Beat)

Celery Beat doesn't know about organizations. Schedule a dispatcher task that launches one task per organization:

```python
# config/settings/base.py or celery beat schedule
CELERY_BEAT_SCHEDULE = {
    "nightly-reports": {
        "task": "apps.reports.tasks.nightly_reports",
        "schedule": crontab(hour=2, minute=0),
    },
}
```

## Retry

If a task with `OrganizationTask` fails and retries, the `organization_id` is preserved because it's the first argument. Retries work correctly.

## Module imports

Don't import organization models at module level in shared tasks:

```python
# Wrong — Location doesn't exist in public schema
from apps.locations.models import Location

@shared_task
def some_shared_task():
    ...

# Correct — import inside the function
@shared_task(base=OrganizationTask)
def some_organization_task():
    from apps.locations.models import Location
    ...
```

## Example

```python
# apps/locations/tasks.py
from celery import shared_task
from apps.organizations.tasks import OrganizationTask
from .models import Location

@shared_task(base=OrganizationTask)
def get_locations_count():
    """Returns the location count for the active organization."""
    return Location.objects.count()
```

Each organization gets its own count because the schema is isolated.
