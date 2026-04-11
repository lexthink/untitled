from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path

from apps.organizations.views import clear_organization
from apps.organizations.views import switch_organization

from .api import api

urlpatterns = [
    path("admin/switch-org/<str:pk>/", switch_organization, name="switch-organization"),
    path("admin/clear-org/", clear_organization, name="clear-organization"),
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/", api.urls),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
            *urlpatterns,
        ]
