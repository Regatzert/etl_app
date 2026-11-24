
import logging

from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from etl_app.apps.data.models import (
    NorthwindProduct,
    NorthwindCategory,
    NorthwindSupplier,
)

from etl_app.apps.common.utils.response_encoder import make_json_safe

from .serializers import (
    ODataExtractionSerializer,
    ODataTransformationSerializer,
    ODataLoadSerializer,
    ETLExecutionSerializer,
    ODataDiscoverySerializer,
)

from .services.extraction_service import ExtractionService
from .services.transformation_service import TransformationService
from .services.load_service import LoadService
from .services.orchestrator_service import OrchestratorService
from .services.etl_response_service import ETLResponseService

from etl_app.apps.etl.authentication.authentication_service import AuthenticationService

from .config.connections import CONNECTIONS

from .extract.metadata_inspector import ODataMetadataInspector

from etl_app.apps.etl.processes.odata_northwind.northwind_etl import (
    sync_products,
    sync_categories,
    sync_suppliers,
    sync_all,
)


logger = logging.getLogger(__name__)


# =====================================================
# DATASETS PERMITIDOS
# =====================================================

ETL_DATASETS = {
    "northwind_products": NorthwindProduct,
    "northwind_categories": NorthwindCategory,
    "northwind_suppliers": NorthwindSupplier,
}


# =====================================================
# HELPERS
# =====================================================

def get_connection_authentication(connection_name):

    if connection_name not in CONNECTIONS:
        raise ValueError(
            f"La conexión '{connection_name}' no está configurada."
        )

    authentication = AuthenticationService.get_authentication(
        connection_name
    )

    return (
        authentication["auth"],
        authentication["headers"],
    )


def get_dataset_model(dataset):

    model = ETL_DATASETS.get(dataset)

    if model is None:
        raise ValueError(
            f"El dataset '{dataset}' no está registrado "
            "como destino permitido."
        )

    return model


# =====================================================
# ODATA EXTRACTION
# =====================================================

@extend_schema(
    request=ODataExtractionSerializer,
    responses={
        200: dict,
        400: dict,
        502: dict,
    },
    description="Extrae registros desde una fuente OData."
)
class ODataExtractionView(APIView):

    def post(self, request):

        serializer = ODataExtractionSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        try:

            connection_name = validated_data["connection"]

            auth, headers = get_connection_authentication(
                connection_name
            )

            result = ExtractionService.extract_from_odata(
                connection_name=connection_name,
                url=validated_data["url"],
                auth=auth,
                headers=headers,
                timeout=validated_data["timeout"],
                max_retries=validated_data["max_retries"],
                query_params=validated_data["query_params"],
            )

            if result["status"] == "error":

                return Response(
                    make_json_safe(result),
                    status=status.HTTP_502_BAD_GATEWAY
                )

            return Response(
                make_json_safe(result),
                status=status.HTTP_200_OK
            )

        except ValueError as error:

            return Response(
                {
                    "status": "error",
                    "message": str(error),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:

            logger.exception(
                "Error ejecutando extracción OData."
            )

            return Response(
                {
                    "status": "error",
                    "message": "Error interno durante la extracción."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =====================================================
# ODATA TRANSFORMATION
# =====================================================

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

        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        result = TransformationService.transform_records(
            records=validated_data["records"],
            mapping=validated_data["mapping"],
            types=validated_data["types"],
            include_unmapped=validated_data["include_unmapped"],
        )

        if result["status"] == "error":

            return Response(
                make_json_safe(result),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            make_json_safe(result),
            status=status.HTTP_200_OK
        )


# =====================================================
# ODATA LOAD
# =====================================================

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

        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        try:

            model = get_dataset_model(
                validated_data["dataset"]
            )

            result = LoadService.load_records(
                records=validated_data["records"],
                model=model,
                strategy=validated_data["strategy"],
                batch_size=validated_data["batch_size"],
                delete_filter=validated_data.get("delete_filter"),
                allow_empty=validated_data["allow_empty"],
            )

            if result["status"] == "error":

                return Response(
                    make_json_safe(result),
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response(
                make_json_safe(result),
                status=status.HTTP_200_OK
            )

        except ValueError as error:

            return Response(
                {
                    "status": "error",
                    "message": str(error),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:

            logger.exception(
                "Error ejecutando carga de datos."
            )

            return Response(
                {
                    "status": "error",
                    "message": "Error interno durante la carga."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =====================================================
# GENERIC ETL EXECUTION
# =====================================================

@extend_schema(
    request=ETLExecutionSerializer,
    responses={
        200: dict,
        400: dict,
        500: dict,
        502: dict,
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

        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        source_config = validated_data["source"]
        load_config = validated_data["load"]
        transformation_config = validated_data["transformation"]

        try:

            model = get_dataset_model(
                load_config["dataset"]
            )

            source = {
                "connection": source_config["connection"],
                "source_type": source_config["source_type"],
                "url": source_config["url"],
                "query_params": source_config["query_params"],
                "timeout": source_config["timeout"],
                "max_retries": source_config["max_retries"],
            }

            destination = {
                "model": model,
                "database": load_config["database"],
                "strategy": load_config["strategy"],
                "batch_size": load_config["batch_size"],
                "allow_empty": load_config["allow_empty"],
                "delete_filter": load_config.get("delete_filter"),
            }

            result = OrchestratorService.execute_pipeline(
                source=source,
                destination=destination,
                transformation=transformation_config,
            )

            if result["status"] == "error":

                return Response(
                    make_json_safe(result),
                    status=status.HTTP_502_BAD_GATEWAY
                )

            return Response(
                make_json_safe(result),
                status=status.HTTP_200_OK
            )

        except ValueError as error:

            return Response(
                {
                    "status": "error",
                    "message": str(error),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:

            logger.exception(
                "Error ejecutando pipeline ETL genérico."
            )

            return Response(
                {
                    "status": "error",
                    "message": "Error interno durante la ejecución ETL."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =====================================================
# ODATA DISCOVERY
# =====================================================

@extend_schema(
    request=ODataDiscoverySerializer,
    responses={
        200: dict,
        400: dict,
        502: dict,
    },
    description=(
        "Analiza los metadatos de una fuente OData "
        "y devuelve sus columnas y tipos de datos."
    )
)
class ODataDiscoveryView(APIView):

    def post(self, request):

        serializer = ODataDiscoverySerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        try:

            auth, headers = get_connection_authentication(
                validated_data["connection"]
            )

            result = ODataMetadataInspector.inspect(
                url=validated_data["url"],
                timeout=validated_data["timeout"],
                auth=auth,
                headers=headers,
            )

            return Response(
                make_json_safe(result),
                status=status.HTTP_200_OK
            )

        except ValueError as error:

            return Response(
                {
                    "status": "error",
                    "message": str(error),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:

            logger.exception(
                "Error consultando metadatos OData."
            )

            return Response(
                {
                    "status": "error",
                    "message": "No se pudieron consultar los metadatos."
                },
                status=status.HTTP_502_BAD_GATEWAY
            )


# =====================================================
# NORTHWIND ETL
# =====================================================

class NorthwindProcessView(APIView):

    process_function = None
    process_description = ""

    def summarize_result(self, result):

        return ETLResponseService.summarize_pipeline(
            result
        )

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

            response_data = self.summarize_result(result)

            if result.get("status") != "success":

                return Response(
                    make_json_safe(response_data),
                    status=status.HTTP_502_BAD_GATEWAY
                )

            return Response(
                make_json_safe(response_data),
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

    def summarize_result(self, result):

        return ETLResponseService.summarize_sync_all(
            result
        )
