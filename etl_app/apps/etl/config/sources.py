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

# ODATA - SAP
SAP_BASE_URL = ""

SAP_SOURCES = {
    # "employees": f"{SAP_BASE_URL}/Employees",
    # "materials": f"{SAP_BASE_URL}/Materials",
}
