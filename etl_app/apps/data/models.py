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