from celery import shared_task

from apps.organizations.tasks import OrganizationTask

from .models import Location


@shared_task(base=OrganizationTask)
def get_locations_count():
    """A Celery task to demonstrate organization aware task usage."""
    return Location.objects.count()
