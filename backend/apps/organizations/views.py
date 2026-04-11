from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from .middleware import OrganizationSessionMiddleware
from .models import Organization


@staff_member_required
def switch_organization(request: HttpRequest, pk: str):
    organization = get_object_or_404(
        Organization.objects.filter(memberships__user=request.user),
        pk=pk,
    )
    request.session[OrganizationSessionMiddleware.SESSION_KEY] = str(organization.pk)
    messages.success(request, f"Switched to {organization.name}")
    return HttpResponseRedirect(reverse("admin:index"))


@staff_member_required
def clear_organization(request: HttpRequest):
    request.session.pop(OrganizationSessionMiddleware.SESSION_KEY, None)
    messages.info(request, "Switched to public schema")
    return HttpResponseRedirect(reverse("admin:index"))
