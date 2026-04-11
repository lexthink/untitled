from uuid import UUID  # noqa: TC003

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja import Status

from apps.locations.models import Location
from apps.organizations.enums import Role
from apps.organizations.permissions import require_roles

from .schema import LocationInputSchema
from .schema import LocationSchema

router = Router(tags=["locations"])


@router.get("/", response=list[LocationSchema])
@require_roles(Role.OWNER, Role.ADMIN, Role.MEMBER)
def list_locations(request):
    return Location.objects.all()


@router.get("/{pk}/", response=LocationSchema)
@require_roles(Role.OWNER, Role.ADMIN, Role.MEMBER)
def retrieve_location(request, pk: UUID):
    return get_object_or_404(Location, pk=pk)


@router.post("/", response={201: LocationSchema})
@require_roles(Role.OWNER, Role.ADMIN)
def create_location(request, data: LocationInputSchema):
    return Status(201, Location.objects.create(**data.dict()))


@router.patch("/{pk}/", response=LocationSchema)
@require_roles(Role.OWNER, Role.ADMIN)
def update_location(request, pk: UUID, data: LocationInputSchema):
    location = get_object_or_404(Location, pk=pk)
    location.name = data.name
    location.save()
    return location


@router.delete("/{pk}/", response={204: None})
@require_roles(Role.OWNER)
def delete_location(request, pk: UUID):
    location = get_object_or_404(Location, pk=pk)
    location.delete()
    return Status(204, None)
