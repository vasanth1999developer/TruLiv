from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

admin.site.site_header = "Super Admin"
admin.site.site_title = "Super Admin Portal"
admin.site.index_title = "Welcome to Techademy Admin portal."

urlpatterns = [
    path("", include("apps.common.urls")),
    path(settings.ADMIN_URL, admin.site.urls),
]

if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += staticfiles_urlpatterns()
