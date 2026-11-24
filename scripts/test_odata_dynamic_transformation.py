
from pathlib import Path
import sys
import os

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "etl_app.config.settings"
)

import django
django.setup()

from etl_app.apps.etl.transform.odata_transformer import (
    ODataTransformer
)

records = [
    {
        "ProductID": 1,
        "ProductName": "Chai",
        "UnitPrice": "18.0000",
        "UnitsInStock": 39,
        "Discontinued": False
    },
    {
        "ProductID": 2,
        "ProductName": "Chang",
        "UnitPrice": "19.0000",
        "UnitsInStock": 17,
        "Discontinued": True
    }
]

columns = [
    {
        "name": "ProductID",
        "odata_type": "Edm.Int32"
    },
    {
        "name": "ProductName",
        "odata_type": "Edm.String"
    },
    {
        "name": "UnitPrice",
        "odata_type": "Edm.Decimal"
    },
    {
        "name": "UnitsInStock",
        "odata_type": "Edm.Int16"
    },
    {
        "name": "Discontinued",
        "odata_type": "Edm.Boolean"
    }
]

transformer = ODataTransformer()

result = transformer.transform_dynamic(
    records=records,
    columns=columns
)

print("\nREGISTROS TRANSFORMADOS:")

for record in result:
    print(record)

print("\nTIPOS RESULTANTES:")

for field, value in result[0].items():
    print(field, ":", type(value).__name__)
