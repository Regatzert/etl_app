# apps/data/views.py

from rest_framework.generics import ListAPIView

from apps.data.services import EmployeeService
from apps.data.serializers import EmployeeSerializer


class EmployeeListView(ListAPIView):

    serializer_class = EmployeeSerializer

    def get_queryset(self):

        return EmployeeService.get_employees()