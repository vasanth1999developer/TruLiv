from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from .views import api

app_name = "common"
API_URL_PREFIX = "api"

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version="v1",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path(f"{API_URL_PREFIX}/server/status/", api.ServerStatusAPIView.as_view()),
    path("", include("apps.properties.urls")),
    path("", include("apps.access.urls")),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
