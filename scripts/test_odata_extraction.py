import os
import sys
from pathlib import Path

# Obtener la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Agregar la raíz del proyecto al PYTHONPATH
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "etl_app.config.settings"
)

import django

django.setup()

from etl_app.apps.etl.services.extraction_service import (
    ExtractionService
)


result = ExtractionService.extract_from_odata(
    url="https://services.odata.org/V4/Northwind/Northwind.svc/Products",
)

print("\n========== RESULTADO ==========")

print("Estado:", result["status"])
print("Fuente:", result["source"])
print("Cantidad:", result["records_count"])

print("\nPrimeros 5 registros:")

for record in result["records"][:5]:
    print(record)