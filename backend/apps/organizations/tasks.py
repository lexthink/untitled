from typing import Any

from celery import Task
from django_tenants.utils import tenant_context

from .models import Organization


class OrganizationTask(Task):
    """
    Base task that activates the organization schema before running.
    The first argument is always the organization_id, which is intercepted
    and used to set the organization context. The task itself does not receive it.

    Inside the task, you can access the organization via self.organization:
        self.organization             — the Organization instance
        self.organization.pk          — the UUID
        self.organization.schema_name — the PostgreSQL schema name

    The result is automatically wrapped with the organization context:
        {"organization_id": "...", "schema_name": "...", "result": <task return value>}

    Usage:
        @shared_task(base=OrganizationTask, bind=True)
        def my_task(self, some_arg):
            print(self.organization.name)
            ...

        my_task.on(organization).delay(some_arg)
    """

    organization: Organization | None = None

    def on(self, organization: Organization) -> Task:
        """Returns a signature that prepends the organization_id."""
        return self.s(str(organization.pk))

    def __call__(self, organization_id: str, *args: Any, **kwargs: Any) -> Any:
        self.organization = Organization.objects.get(pk=organization_id)

        with tenant_context(self.organization):
            result = self.run(*args, **kwargs)

        return {
            "organization": {
                "id": self.organization.pk,
                "name": self.organization.name,
                "schema_name": self.organization.schema_name,
            },
            "result": result,
        }
