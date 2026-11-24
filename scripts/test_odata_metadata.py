
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import os
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "etl_app.config.settings"
)

import django
django.setup()

from etl_app.apps.etl.extract.metadata_inspector import (
    ODataMetadataInspector
)

url = (
    "https://services.odata.org/V4/"
    "Northwind/Northwind.svc/Products"
)

try:
    result = ODataMetadataInspector.inspect(url)

    print("\nENTIDAD:", result["entity"])
    print("TIPO:", result["entity_type"])
    print("TOTAL COLUMNAS:", result["columns_count"])

    print("\nCOLUMNAS ENCONTRADAS:")

    for column in result["columns"]:
        print(
            f'{column["name"]} | '
            f'{column["odata_type"]} | '
            f'{column["python_type"]} | '
            f'Nullable: {column["nullable"]}'
        )

except Exception as error:
    print("ERROR:", error)
