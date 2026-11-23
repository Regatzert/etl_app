import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "etl_app.config.settings"
)

import django

django.setup()

from etl_app.apps.etl.services.transformation_service import (
    TransformationService
)


records = [
    {
        "ProductID": "1",
        "ProductName": "  Chai  ",
        "UnitPrice": "18.50",
        "UnitsInStock": "39",
        "Discontinued": "false",
        "CreatedDate": "2026-11-23",
    },
    {
        "ProductID": "2",
        "ProductName": "Chang",
        "UnitPrice": "19.00",
        "UnitsInStock": "17",
        "Discontinued": "true",
        "CreatedDate": "2026-11-23",
    },
]


mapping = {
    "ProductID": "product_id",
    "ProductName": "product_name",
    "UnitPrice": "price",
    "UnitsInStock": "stock",
    "Discontinued": "is_discontinued",
    "CreatedDate": "created_date",
}


types = {
    "ProductID": "integer",
    "ProductName": "string",
    "UnitPrice": "decimal",
    "UnitsInStock": "integer",
    "Discontinued": "boolean",
    "CreatedDate": "date",
}


result = TransformationService.transform_records(
    records=records,
    mapping=mapping,
    types=types,
    include_unmapped=False,
)


print("\n========== RESULTADO ==========")

print("Estado:", result["status"])

print("Cantidad:", result["records_count"])

print("\nRegistros transformados:")

for record in result["records"]:
    print(record)

    print("\nTipos de datos:")

    for field, value in record.items():
        print(
            f"{field}: {value} "
            f"({type(value).__name__})"
        )