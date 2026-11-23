# apps/data/repositories.py

from apps.data.models import Employee

class EmployeeRepository:
    @staticmethod
    def get_all():
        return Employee.objects.all()

    @staticmethod
    def get_by_id(employee_id):
        return Employee.objects.filter(id=employee_id).first()