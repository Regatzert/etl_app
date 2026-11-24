from django.urls import path

from .views import (ODataExtractionView, 
                    ODataTransformationView, 
                    ODataLoadView,
                    ETLExecutionView,)


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

    path(
        "load/",
        ODataLoadView.as_view(),
        name="odata-load"
    ),

    path(
        "execute/",
        ETLExecutionView.as_view(),
        name="etl-execution"
    ),
]
