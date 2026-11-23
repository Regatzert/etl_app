# apps/data/services.py

from apps.data.repositories import EmployeeRepository


class EmployeeService:

    @staticmethod
    def get_employees():

        return EmployeeRepository.get_all()