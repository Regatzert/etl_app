
from django.db import models


class Employee(models.Model):

    employee_code = models.CharField(
        max_length=50,
        unique=True,
    )

    first_name = models.CharField(
        max_length=100,
    )

    last_name = models.CharField(
        max_length=100,
    )

    email = models.EmailField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "employees"
        ordering = ["last_name", "first_name"]
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"

    def __str__(self):
        return f"{self.employee_code} - {self.first_name} {self.last_name}"


class NorthwindProduct(models.Model):

    product_id = models.IntegerField(primary_key=True)
    product_name = models.TextField(null=True, blank=True)
    supplier_id = models.IntegerField(null=True, blank=True)
    category_id = models.IntegerField(null=True, blank=True)
    quantity_per_unit = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
    )
    units_in_stock = models.SmallIntegerField(null=True, blank=True)
    units_on_order = models.SmallIntegerField(null=True, blank=True)
    reorder_level = models.SmallIntegerField(null=True, blank=True)
    discontinued = models.BooleanField()

    class Meta:
        db_table = "northwind_products"
        verbose_name = "Producto Northwind"
        verbose_name_plural = "Productos Northwind"

    def __str__(self):
        return self.product_name or str(self.product_id)


class NorthwindCategory(models.Model):

    category_id = models.IntegerField(primary_key=True)
    category_name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    picture = models.BinaryField(null=True, blank=True)

    class Meta:
        db_table = "northwind_categories"
        verbose_name = "Categoría Northwind"
        verbose_name_plural = "Categorías Northwind"

    def __str__(self):
        return self.category_name or str(self.category_id)


class NorthwindSupplier(models.Model):

    supplier_id = models.IntegerField(primary_key=True)
    company_name = models.TextField(null=True, blank=True)
    contact_name = models.TextField(null=True, blank=True)
    contact_title = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    region = models.TextField(null=True, blank=True)
    postal_code = models.TextField(null=True, blank=True)
    country = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    fax = models.TextField(null=True, blank=True)
    home_page = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "northwind_suppliers"
        verbose_name = "Proveedor Northwind"
        verbose_name_plural = "Proveedores Northwind"

    def __str__(self):
        return self.company_name or str(self.supplier_id)
