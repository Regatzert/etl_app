
from etl_app.apps.etl.config.sources import NORTHWIND_SOURCES

from etl_app.apps.etl.services.orchestrator_service import (
    OrchestratorService
)
from datetime import datetime, timezone
from time import perf_counter

from etl_app.apps.data.models import (
    NorthwindProduct,
    NorthwindCategory,
    NorthwindSupplier,
)


def sync_products():

    return OrchestratorService.execute_pipeline(

        source={
            "connection": "northwind",
            "source_type": "odata",
            "url": NORTHWIND_SOURCES["products"],
        },

        destination={
            "model": NorthwindProduct,
            "database": "etl_platform",
            "strategy": "replace_all",
            "batch_size": 1000,
            "allow_empty": False,
        },

        transformation={
            "mapping": {
                "ProductID": "product_id",
                "ProductName": "product_name",
                "SupplierID": "supplier_id",
                "CategoryID": "category_id",
                "QuantityPerUnit": "quantity_per_unit",
                "UnitPrice": "unit_price",
                "UnitsInStock": "units_in_stock",
                "UnitsOnOrder": "units_on_order",
                "ReorderLevel": "reorder_level",
                "Discontinued": "discontinued",
            },
            "include_unmapped": False,
        },
    )

def sync_categories():

    return OrchestratorService.execute_pipeline(

        source={
            "connection": "northwind",
            "source_type": "odata",
            "url": NORTHWIND_SOURCES["categories"],
        },

        destination={
            "model": NorthwindCategory,
            "database": "etl_platform",
            "strategy": "replace_all",
            "batch_size": 1000,
            "allow_empty": False,
        },

        transformation={
            "mapping": {
                "CategoryID": "category_id",
                "CategoryName": "category_name",
                "Description": "description",
                "Picture": "picture",
            },
            "include_unmapped": False,
        },
    )

def sync_suppliers():

    return OrchestratorService.execute_pipeline(

        source={
            "connection": "northwind",
            "source_type": "odata",
            "url": NORTHWIND_SOURCES["suppliers"],
        },

        destination={
            "model": NorthwindSupplier,
            "database": "etl_platform",
            "strategy": "replace_all",
            "batch_size": 1000,
            "allow_empty": False,
        },

        transformation={
            "mapping": {
                "SupplierID": "supplier_id",
                "CompanyName": "company_name",
                "ContactName": "contact_name",
                "ContactTitle": "contact_title",
                "Address": "address",
                "City": "city",
                "Region": "region",
                "PostalCode": "postal_code",
                "Country": "country",
                "Phone": "phone",
                "Fax": "fax",
                "HomePage": "home_page",
            },
            "include_unmapped": False,
        },
    )

def sync_all():

    started_at = datetime.now(timezone.utc)
    start_counter = perf_counter()

    results = {}

    processes = {
        "products": sync_products,
        "categories": sync_categories,
        "suppliers": sync_suppliers,
    }

    for name, process in processes.items():

        result = process()

        results[name] = result

        if result.get("status") != "success":

            finished_at = datetime.now(timezone.utc)

            return {
                "status": "error",
                "message": f"Error ejecutando el proceso {name}.",
                "started_at": started_at.isoformat(),
                "finished_at": finished_at.isoformat(),
                "duration_seconds": round(
                    perf_counter() - start_counter, 3
                ),
                "processes": results,
            }

    finished_at = datetime.now(timezone.utc)

    return {
        "status": "success",
        "message": (
            "Todos los procesos Northwind finalizaron correctamente."
        ),
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "duration_seconds": round(
            perf_counter() - start_counter, 3
        ),
        "processes": results,
    }

