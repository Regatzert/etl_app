from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


urlpatterns = [
    # =====================================================
    # DJANGO ADMIN
    # =====================================================
    path("admin/", admin.site.urls),

    # =====================================================
    # API
    # =====================================================
    path("api/v1/data/", include("etl_app.apps.data.urls")),
    path("api/v1/users/", include("etl_app.apps.users.urls")),
    path("api/v1/etl/", include("etl_app.apps.etl.urls")),

    # =====================================================
    # OPENAPI / SWAGGER
    # =====================================================
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),

    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
        name="swagger-ui",
    ),

    path(
        "api/redoc/",
        SpectacularRedocView.as_view(
            url_name="schema"
        ),
        name="redoc",
    ),
]