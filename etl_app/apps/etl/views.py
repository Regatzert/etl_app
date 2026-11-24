import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .serializers import ODataExtractionSerializer
from .services.extraction_service import ExtractionService

from .serializers import ODataTransformationSerializer
from .services.transformation_service import TransformationService

from .serializers import ODataLoadSerializer
from .services.load_service import LoadService

from .serializers import ETLExecutionSerializer
from .services.orchestrator_service import OrchestratorService

from .serializers import ODataDiscoverySerializer
from .extract.metadata_inspector import ODataMetadataInspector
from etl_app.apps.common.utils.response_encoder import make_json_safe

from etl_app.apps.etl.processes.odata_northwind.northwind_etl import (
    sync_products,
    sync_categories,
    sync_suppliers,
    sync_all,
)

logger = logging.getLogger(__name__)


class ODataExtractionView(APIView):

    def post(self, request):

        serializer = ODataExtractionSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        result = ExtractionService.extract_from_odata(
            url=validated_data["url"],
            username=validated_data.get("username"),
            password=validated_data.get("password"),
            timeout=validated_data["timeout"],
            max_retries=validated_data["max_retries"],
        )

        if result["status"] == "error":

            return Response(
                {
                    "status": "error",
                    "message": result["message"],
                    "source": result["source"],
                    "records_count": result["records_count"],
                    "started_at": result["started_at"],
                    "finished_at": result["finished_at"],
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response(
            {
                "status": result["status"],
                "source": result["source"],
                "records_count": result["records_count"],
                "started_at": result["started_at"],
                "finished_at": result["finished_at"],
                "records": result["records"],
            },
            status=status.HTTP_200_OK
        )

@extend_schema(
    request=ODataTransformationSerializer,
    responses={
        200: dict,
        400: dict,
        500: dict,
    },
    description="Transforma los registros obtenidos desde una fuente de datos."
)
class ODataTransformationView(APIView):

    def post(self, request):

        serializer = ODataTransformationSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        validated_data = serializer.validated_data

        # records = serializer.validated_data["records"]

        result = TransformationService.transform_records(
            records=validated_data["records"],
            mapping=validated_data["mapping"],
            types=validated_data["types"],
            include_unmapped=validated_data["include_unmapped"],
        )

        if result["status"] == "error":

            return Response(
                {
                    "status": "error",
                    "message": result["message"],
                    "records_count": 0,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            result,
            status=status.HTTP_200_OK
        )

@extend_schema(
    request=ODataLoadSerializer,
    responses={
        200: dict,
        400: dict,
        500: dict,
    },
    description="Carga registros transformados en PostgreSQL."
)
class ODataLoadView(APIView):

    def post(self, request):

        serializer = ODataLoadSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        validated_data = serializer.validated_data

        result = LoadService.load_records(
            records=validated_data["records"],
            dataset=validated_data["dataset"],
            batch_size=validated_data["batch_size"],
        )

        if result["status"] == "error":

            return Response(
                result,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            result,
            status=status.HTTP_200_OK
        )

@extend_schema(
    request=ETLExecutionSerializer,
    responses={
        200: dict,
        400: dict,
        500: dict,
    },
    description=(
        "Ejecuta un pipeline ETL completo: "
        "Extract, Transform y Load."
    )
)
class ETLExecutionView(APIView):

    def post(self, request):

        serializer = ETLExecutionSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        validated_data = serializer.validated_data

        result = OrchestratorService.execute_pipeline(
            source_config=validated_data["source"],
            transformation_config=(
                validated_data["transformation"]
            ),
            load_config=validated_data["load"],
        )

        if result["status"] == "error":

            return Response(
                result,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            result,
            status=status.HTTP_200_OK
        )


class ODataDiscoveryView(APIView):

    @extend_schema(
        request=ODataDiscoverySerializer,
        responses={
            200: dict,
            400: dict,
        },
        description=(
            "Analiza los metadatos de una fuente OData "
            "y devuelve sus columnas y tipos de datos."
        )
    )
    def post(self, request):
        serializer = ODataDiscoverySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = ODataMetadataInspector.inspect(
                url=serializer.validated_data["url"],
                timeout=serializer.validated_data["timeout"]
            )

            return Response(result, status=status.HTTP_200_OK)

        except ValueError as error:
            return Response(
                {"message": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

# =====================================================
# NORTHWIND ETL
# =====================================================

class NorthwindProcessView(APIView):
    """
    Vista base para ejecutar procesos ETL predefinidos
    de Northwind.
    """

    process_function = None
    process_description = ""

    @extend_schema(
        request=None,
        responses={
            200: dict,
            500: dict,
            502: dict,
        },
        description="Ejecuta un proceso ETL predefinido de Northwind."
    )
    def post(self, request):

        try:

            result = self.process_function()

            if result.get("status") != "success":

                return Response(
                    make_json_safe(result),
                    status=status.HTTP_502_BAD_GATEWAY
                )

            return Response(
                make_json_safe(result),
                status=status.HTTP_200_OK
            )

        except Exception:

            logger.exception(
                "Error ejecutando proceso Northwind: %s",
                self.process_description
            )

            return Response(
                {
                    "status": "error",
                    "message": (
                        f"Error ejecutando {self.process_description}."
                    ),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class NorthwindProductsView(NorthwindProcessView):

    process_function = staticmethod(sync_products)
    process_description = "sincronización de productos"


class NorthwindCategoriesView(NorthwindProcessView):

    process_function = staticmethod(sync_categories)
    process_description = "sincronización de categorías"


class NorthwindSuppliersView(NorthwindProcessView):

    process_function = staticmethod(sync_suppliers)
    process_description = "sincronización de proveedores"


class NorthwindSyncAllView(NorthwindProcessView):

    process_function = staticmethod(sync_all)
    process_description = "sincronización completa de Northwind"