from django.urls import path

from .views import (ODataExtractionView, ODataTransformationView)


urlpatterns = [
    path(
        "extract/",
        ODataExtractionView.as_view(),
        name="odata-extraction"
    ),

    path(
        "transform/",
        ODataTransformationView.as_view(),
        name="odata-transformation"
    ),
]