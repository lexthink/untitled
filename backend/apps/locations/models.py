from django.db.models import CharField
from django.utils.translation import gettext_lazy as _

from apps.utils.models import AbstractModel


class Location(AbstractModel):
    name = CharField(_("name"), max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name
