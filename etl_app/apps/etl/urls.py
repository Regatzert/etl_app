from django.urls import path

from .views import ODataExtractionView


urlpatterns = [
    path(
        "extract/",
        ODataExtractionView.as_view(),
        name="odata-extraction"
    ),
]