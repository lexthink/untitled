from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LocationsConfig(AppConfig):
    name = "apps.locations"
    verbose_name = _("Locations")

    def ready(self):
        """
        Override this method in subclasses to run code when Django starts.
        """
