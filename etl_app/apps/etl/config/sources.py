# ODATA - NORTHWIND
NORTHWIND_BASE_URL = (
    "https://services.odata.org/"
    "V4/Northwind/Northwind.svc"
)

NORTHWIND_SOURCES = {
    "products": f"{NORTHWIND_BASE_URL}/Products",
    "categories": f"{NORTHWIND_BASE_URL}/Categories",
    "suppliers": f"{NORTHWIND_BASE_URL}/Suppliers",
}

# =========================================================
# 2. SAP - ODATA
# =========================================================
#
# Completar con la URL base del servicio OData proporcionada
# por SAP.
#
# Importante:
# SAP puede publicar distintos servicios OData.
# Cada servicio puede tener su propio endpoint.
#
# =========================================================

# SAP_BASE_URL = "https://servidor-sap.example.com/sap/opu/odata/sap"

# SAP_SOURCES = {
#
#     "employees": (
#         f"{SAP_BASE_URL}/ZEMPLOYEE_SRV/EmployeeSet"
#     ),
#
#     "materials": (
#         f"{SAP_BASE_URL}/ZPRODUCT_SRV/MaterialSet"
#     ),
#
#     "orders": (
#         f"{SAP_BASE_URL}/ZORDER_SRV/OrderSet"
#     ),
#
# }


# =========================================================
# 3. SISTEMA EXTERNO - ERP
# =========================================================
#
# Plantilla para conectar un ERP externo que exponga OData.
#
# Completar con la URL entregada por el proveedor.
#
# =========================================================

# ERP_BASE_URL = "https://erp.example.com/odata"

# ERP_SOURCES = {
#
#     "customers": f"{ERP_BASE_URL}/Customers",
#
#     "products": f"{ERP_BASE_URL}/Products",
#
#     "invoices": f"{ERP_BASE_URL}/Invoices",
#
# }


# =========================================================
# 4. SISTEMA EXTERNO - API ODATA DE TERCEROS
# =========================================================
#
# Plantilla para servicios OData externos.
#
# Cada proveedor puede publicar una estructura diferente.
# No es obligatorio utilizar una URL base común.
#
# =========================================================

# EXTERNAL_API_SOURCES = {
#
#     "employees": (
#         "https://api.example.com/odata/Employees"
#     ),
#
#     "transactions": (
#         "https://api.example.com/odata/Transactions"
#     ),
#
# }