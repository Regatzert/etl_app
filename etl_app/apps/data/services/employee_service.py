from ..repositories.employee_repository import EmployeeRepository


class EmployeeService:

    @staticmethod
    def get_employees():
        return EmployeeRepository.get_all()

    @staticmethod
    def get_employee_by_id(employee_id: int):
        return EmployeeRepository.get_by_id(employee_id)

    @staticmethod
    def create_employee(data: dict):
        return EmployeeRepository.create(data)