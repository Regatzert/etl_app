from rest_framework.generics import ListAPIView

from .services.employee_service import EmployeeService
from .serializers import EmployeeSerializer


class EmployeeListView(ListAPIView):

    serializer_class = EmployeeSerializer

    def get_queryset(self):

        return EmployeeService.get_employees()