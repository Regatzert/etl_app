from ..models import Employee


class EmployeeRepository:

    @staticmethod
    def get_all():

        return Employee.objects.all()

    @staticmethod
    def get_by_id(employee_id: int):

        return Employee.objects.filter(
            id=employee_id
        ).first()

    @staticmethod
    def create(data: dict):

        return Employee.objects.create(
            **data
        )