from django.urls import path

from .views import (ODataExtractionView,
    ODataTransformationView,
    ODataLoadView,
    ETLExecutionView,
    ODataDiscoveryView,
    NorthwindProductsView,
    NorthwindCategoriesView,
    NorthwindSuppliersView,
    NorthwindSyncAllView,)


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

    path("inspeccionar_odata/", ODataDiscoveryView.as_view(), name="odata-discover"),

    # =========================================
    # NORTHWIND
    # =========================================

    path(
        "northwind/products/",
        NorthwindProductsView.as_view(),
        name="northwind-products"
    ),

    path(
        "northwind/categories/",
        NorthwindCategoriesView.as_view(),
        name="northwind-categories"
    ),

    path(
        "northwind/suppliers/",
        NorthwindSuppliersView.as_view(),
        name="northwind-suppliers"
    ),

    path(
        "northwind/sync-all/",
        NorthwindSyncAllView.as_view(),
        name="northwind-sync-all"
    ),

]
