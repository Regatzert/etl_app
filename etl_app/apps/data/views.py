from rest_framework.generics import ListAPIView

from .services.employee_service import EmployeeService
from .serializers import EmployeeSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services.data_service import DataService

class EmployeeListView(ListAPIView):

    serializer_class = EmployeeSerializer

    def get_queryset(self):

        return EmployeeService.get_employees()

class DataQueryView(APIView):

    def get(self, request, dataset):

        try:

            page = int(
                request.query_params.get("page", 1)
            )

            page_size = int(
                request.query_params.get("page_size", 50)
            )

            if page < 1:
                raise ValueError(
                    "page debe ser mayor o igual a 1."
                )

            if page_size < 1 or page_size > 100:
                raise ValueError(
                    "page_size debe estar entre 1 y 100."
                )

            result = DataService.get_data(
                dataset=dataset,
                page=page,
                page_size=page_size
            )

            return Response(
                result,
                status=status.HTTP_200_OK
            )

        except ValueError as error:

            return Response(
                {"message": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )