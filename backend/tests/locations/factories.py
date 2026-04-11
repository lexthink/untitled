from factory import Faker
from factory.django import DjangoModelFactory

from apps.locations.models import Location


class LocationFactory(DjangoModelFactory[Location]):
    name = Faker("city")

    class Meta:
        model = Location
