
import logging
import os

from datetime import datetime, timezone
from typing import Any

from django.db.models import Model

from .extraction_service import ExtractionService
from .transformation_service import TransformationService
from .load_service import LoadService

from etl_app.apps.etl.authentication.authentication_service import (
    AuthenticationService
)

from etl_app.apps.etl.config.connections import CONNECTIONS

from etl_app.apps.etl.extract.metadata_inspector import (
    ODataMetadataInspector
)


logger = logging.getLogger(__name__)


class OrchestratorService:

    @staticmethod
    def execute_pipeline(
        source: dict[str, Any],
        destination: dict[str, Any],
        transformation: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        execution_started_at = datetime.now(timezone.utc)

        execution_result = {
            "status": "running",
            "started_at": execution_started_at.isoformat(),
            "finished_at": None,
            "duration_seconds": None,
            "discovery": None,
            "extraction": None,
            "transformation": None,
            "load": None,
            "records_extracted": 0,
            "records_transformed": 0,
            "records_loaded": 0,
            "message": "Proceso ETL iniciado.",
        }

        transformation = transformation or {}

        if not isinstance(transformation, dict):
            raise ValueError(
                "La configuración transformation debe ser un diccionario."
            )

        logger.info("Iniciando pipeline ETL.")

        try:

            # =========================================
            # 0. VALIDAR CONFIGURACIÓN
            # =========================================

            logger.info("Validando configuración del pipeline.")

            OrchestratorService._validate_configuration(
                source=source,
                destination=destination,
            )

            source_type = source.get("source_type", "odata")

            if source_type != "odata":
                raise ValueError(
                    f"Fuente no soportada: {source_type}"
                )

            model = destination["model"]

            if not isinstance(model, type) or not issubclass(
                model, Model
            ):
                raise ValueError(
                    "destination.model debe ser un modelo Django."
                )

            # =========================================
            # 1. RESOLVER CONEXIÓN Y AUTENTICACIÓN
            # =========================================

            logger.info(
                "Resolviendo conexión: %s",
                source["connection"]
            )

            connection_name = source["connection"]

            connection_config = CONNECTIONS[connection_name]

            if connection_config.get("source_type") != source_type:
                raise ValueError(
                    f"La conexión '{connection_name}' no es compatible "
                    f"con el tipo de fuente '{source_type}'."
                )

            authentication = (
                AuthenticationService.get_authentication(
                    connection_name
                )
            )

            timeout = int(
                source.get(
                    "timeout",
                    os.getenv(
                        connection_config.get(
                            "timeout_env",
                            "ODATA_TIMEOUT"
                        ),
                        "60"
                    )
                )
            )

            max_retries = int(
                source.get(
                    "max_retries",
                    os.getenv(
                        connection_config.get(
                            "max_retries_env",
                            "ETL_MAX_RETRIES"
                        ),
                        "3"
                    )
                )
            )

            auth = authentication["auth"]
            headers = authentication["headers"]

            # =========================================
            # 2. DISCOVERY
            # =========================================

            logger.info(
                "Etapa 1: Descubrimiento de metadatos."
            )

            metadata = ODataMetadataInspector.inspect(
                url=source["url"],
                timeout=timeout,
                auth=auth,
                headers=headers
            )

            execution_result["discovery"] = metadata

            columns = metadata["columns"]

            # =========================================
            # 3. EXTRACT
            # =========================================

            logger.info("Etapa 2: Extracción.")

            extraction_result = (
                ExtractionService.extract_from_odata(
                    connection_name=connection_name,
                    url=source["url"],
                    auth=auth,
                    headers=headers,
                    timeout=timeout,
                    max_retries=max_retries,
                    query_params=source.get("query_params"),
                )
            )

            execution_result["extraction"] = extraction_result

            if extraction_result.get("status") != "success":

                return OrchestratorService._finish_with_error(
                    execution_result,
                    execution_started_at,
                    "Error durante la extracción.",
                )

            extracted_records = extraction_result.get(
                "records", []
            )

            execution_result["records_extracted"] = len(
                extracted_records
            )

            # =========================================
            # 4. TRANSFORM
            # =========================================

            logger.info(
                "Etapa 3: Transformación dinámica."
            )

            transformation_result = (
                TransformationService.transform_records_dynamic(
                    records=extracted_records,
                    columns=columns,
                    mapping=transformation.get("mapping", {}),
                    include_unmapped=transformation.get(
                        "include_unmapped",
                        True,
                    ),
                )
            )

            execution_result["transformation"] = (
                transformation_result
            )

            if transformation_result.get("status") != "success":

                return OrchestratorService._finish_with_error(
                    execution_result,
                    execution_started_at,
                    "Error durante la transformación.",
                )

            transformed_records = transformation_result.get(
                "records", []
            )

            execution_result["records_transformed"] = len(
                transformed_records
            )

            # =========================================
            # 5. LOAD
            # =========================================

            logger.info(
                "Etapa 4: Carga en modelo %s.",
                model.__name__,
            )

            load_result = LoadService.load_records(
                records=transformed_records,
                model=model,
                strategy=destination["strategy"],
                batch_size=destination.get(
                    "batch_size",
                    1000
                ),
                delete_filter=destination.get(
                    "delete_filter"
                ),
                allow_empty=destination.get(
                    "allow_empty",
                    False
                ),
                database=destination.get(
                    "database",
                    "etl_platform"
                ),
            )

            execution_result["load"] = load_result

            if load_result.get("status") != "success":

                return OrchestratorService._finish_with_error(
                    execution_result,
                    execution_started_at,
                    "Error durante la carga.",
                )

            execution_result["records_loaded"] = (
                load_result.get("records_count", 0)
            )

            # =========================================
            # COMPLETED
            # =========================================

            execution_result["status"] = "success"

            execution_result["message"] = (
                "Pipeline ETL ejecutado correctamente."
            )

            logger.info(
                "Pipeline ETL completado correctamente."
            )

            return OrchestratorService._finish_execution(
                execution_result,
                execution_started_at,
            )

        except Exception as error:

            logger.exception(
                "Error inesperado durante la ejecución ETL."
            )

            execution_result["status"] = "error"
            execution_result["message"] = str(error)

            return OrchestratorService._finish_execution(
                execution_result,
                execution_started_at,
            )

    @staticmethod
    def _validate_configuration(
        source: dict[str, Any],
        destination: dict[str, Any],
    ) -> None:

        if not isinstance(source, dict):
            raise ValueError(
                "La configuración source debe ser un diccionario."
            )

        if not isinstance(destination, dict):
            raise ValueError(
                "La configuración destination debe ser un diccionario."
            )

        if not source.get("connection"):
            raise ValueError(
                "Debe especificar el nombre de la conexión."
            )

        if source["connection"] not in CONNECTIONS:
            raise ValueError(
                f"La conexión '{source['connection']}' "
                "no está registrada."
            )

        if not source.get("url"):
            raise ValueError(
                "La URL de origen es obligatoria."
            )

        query_params = source.get("query_params")

        if query_params is not None:

            if not isinstance(query_params, dict):
                raise ValueError(
                    "query_params debe ser un diccionario."
                )

            for key, value in query_params.items():

                if not isinstance(key, str) or not key.strip():
                    raise ValueError(
                        "Los nombres de los parámetros no pueden estar vacíos."
                    )

                if value is None:
                    raise ValueError(
                        f"El parámetro '{key}' no puede tener valor None."
                    )

        if not destination.get("model"):
            raise ValueError(
                "El modelo Django de destino es obligatorio."
            )

        if not destination.get("database"):
            raise ValueError(
                "Debe especificar la conexión PostgreSQL de destino."
            )

        strategy = destination.get("strategy")

        if strategy not in (
            "replace_all",
            "replace_by_filter"
        ):
            raise ValueError(
                "La estrategia debe ser replace_all "
                "o replace_by_filter."
            )

        if strategy == "replace_by_filter":

            delete_filter = destination.get("delete_filter")

            if not isinstance(delete_filter, dict) or not delete_filter:
                raise ValueError(
                    "La estrategia replace_by_filter requiere "
                    "un delete_filter no vacío."
                )

    @staticmethod
    def _finish_with_error(
        result: dict[str, Any],
        started_at: datetime,
        message: str,
    ) -> dict[str, Any]:

        result["status"] = "error"
        result["message"] = message

        return OrchestratorService._finish_execution(
            result,
            started_at,
        )

    @staticmethod
    def _finish_execution(
        result: dict[str, Any],
        started_at: datetime,
    ) -> dict[str, Any]:

        finished_at = datetime.now(timezone.utc)

        result["finished_at"] = finished_at.isoformat()

        result["duration_seconds"] = (
            finished_at - started_at
        ).total_seconds()

        return result
