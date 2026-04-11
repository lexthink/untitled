from ninja import ModelSchema

from apps.locations.models import Location


class LocationSchema(ModelSchema):
    class Meta:
        model = Location
        fields = ["id", "name"]


class LocationInputSchema(ModelSchema):
    class Meta:
        model = Location
        fields = ["name"]
