from django.urls import include, path

from .views import api

app_name = "common"
API_URL_PREFIX = "api"

urlpatterns = [
    path(f"{API_URL_PREFIX}/server/status/", api.ServerStatusAPIView.as_view()),
    path("", include("apps.properties.urls")),
    path("", include("apps.access.urls")),
]
