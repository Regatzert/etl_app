import logging
from datetime import datetime, timezone
from typing import Any

from .extraction_service import ExtractionService
from .transformation_service import TransformationService
from .load_service import LoadService


logger = logging.getLogger(__name__)


class OrchestratorService:

    @staticmethod
    def execute_pipeline(
        source_config: dict[str, Any],
        transformation_config: dict[str, Any],
        load_config: dict[str, Any],
    ) -> dict[str, Any]:

        execution_started_at = datetime.now(timezone.utc)

        execution_result = {
            "status": "running",
            "started_at": execution_started_at.isoformat(),
            "finished_at": None,
            "duration_seconds": None,
            "extraction": None,
            "transformation": None,
            "load": None,
            "records_extracted": 0,
            "records_transformed": 0,
            "records_loaded": 0,
            "message": "Proceso ETL iniciado.",
        }

        logger.info(
            "Iniciando ejecución del pipeline ETL."
        )

        try:

            # =========================================
            # 1. EXTRACT
            # =========================================

            logger.info(
                "Etapa 1: Extracción iniciada."
            )

            extraction_result = (
                OrchestratorService._execute_extraction(
                    source_config
                )
            )

            execution_result["extraction"] = (
                extraction_result
            )

            if extraction_result["status"] != "success":

                execution_result["status"] = "error"

                execution_result["message"] = (
                    "Error durante la extracción."
                )

                return OrchestratorService._finish_execution(
                    execution_result,
                    execution_started_at
                )

            extracted_records = (
                extraction_result.get("records", [])
            )

            execution_result["records_extracted"] = (
                len(extracted_records)
            )

            # =========================================
            # 2. TRANSFORM
            # =========================================

            logger.info(
                "Etapa 2: Transformación iniciada."
            )

            transformation_result = (
                TransformationService.transform_records(
                    records=extracted_records,
                    mapping=transformation_config.get(
                        "mapping",
                        {}
                    ),
                    types=transformation_config.get(
                        "types",
                        {}
                    ),
                    include_unmapped=(
                        transformation_config.get(
                            "include_unmapped",
                            False
                        )
                    ),
                )
            )

            execution_result["transformation"] = (
                transformation_result
            )

            if transformation_result.get(
                "status"
            ) != "success":

                execution_result["status"] = "error"

                execution_result["message"] = (
                    "Error durante la transformación."
                )

                return OrchestratorService._finish_execution(
                    execution_result,
                    execution_started_at
                )

            transformed_records = (
                transformation_result.get(
                    "records",
                    []
                )
            )

            execution_result["records_transformed"] = (
                len(transformed_records)
            )

            # =========================================
            # 3. LOAD
            # =========================================

            logger.info(
                "Etapa 3: Carga iniciada."
            )

            load_result = LoadService.load_records(
                records=transformed_records,
                dataset=load_config["dataset"],
                batch_size=load_config.get(
                    "batch_size",
                    1000
                ),
            )

            execution_result["load"] = load_result

            if load_result.get("status") != "success":

                execution_result["status"] = "error"

                execution_result["message"] = (
                    "Error durante la carga."
                )

                return OrchestratorService._finish_execution(
                    execution_result,
                    execution_started_at
                )

            execution_result["records_loaded"] = (
                load_result.get(
                    "records_count",
                    0
                )
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
                execution_started_at
            )

        except Exception:

            logger.exception(
                "Error inesperado durante la ejecución ETL."
            )

            execution_result["status"] = "error"

            execution_result["message"] = (
                "Error inesperado durante la ejecución ETL."
            )

            return OrchestratorService._finish_execution(
                execution_result,
                execution_started_at
            )

    @staticmethod
    def _execute_extraction(
        source_config: dict[str, Any]
    ) -> dict[str, Any]:

        source_type = source_config.get(
            "source_type",
            "odata"
        )

        if source_type != "odata":

            return {
                "status": "error",
                "message": (
                    f"Fuente no soportada: {source_type}"
                ),
                "records": [],
                "records_count": 0,
            }

        return ExtractionService.extract_from_odata(
            url=source_config["url"],
            username=source_config.get("username"),
            password=source_config.get("password"),
            timeout=source_config.get(
                "timeout",
                60
            ),
            max_retries=source_config.get(
                "max_retries",
                3
            ),
        )

    @staticmethod
    def _finish_execution(
        result: dict[str, Any],
        started_at: datetime
    ) -> dict[str, Any]:

        finished_at = datetime.now(timezone.utc)

        result["finished_at"] = (
            finished_at.isoformat()
        )

        result["duration_seconds"] = (
            finished_at - started_at
        ).total_seconds()

        return result