from typing import Any

from celery import Task
from django_tenants.utils import tenant_context

from .models import Organization


class OrganizationTask(Task):
    """
    Base task that activates the organization schema before running.
    The first argument is always the organization_id, which is intercepted
    and used to set the organization context. The task itself does not receive it.

    Usage:
        @shared_task(base=OrganizationTask)
        def my_task(some_arg):
            # organization schema is already active
            ...

        # Execute immediately in background
        my_task.bind(org).delay(some_arg)

        # Execute with options (countdown, eta, queue, etc.)
        my_task.bind(org).apply_async(args=[some_arg], countdown=60)
        my_task.bind(org).apply_async(args=[some_arg], eta=datetime(2026, 4, 12, 10, 0))
        my_task.bind(org).apply_async(args=[some_arg], queue="high_priority")
    """

    def bind(self, organization: Organization) -> Task:
        """Returns a signature that prepends the organization_id."""
        return self.s(str(organization.pk))

    def __call__(self, organization_id: str, *args: Any, **kwargs: Any) -> Any:
        organization = Organization.objects.get(pk=organization_id)
        with tenant_context(organization):
            return self.run(*args, **kwargs)
