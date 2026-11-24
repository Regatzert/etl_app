
import logging
from datetime import datetime, timezone
from typing import Any

from etl_app.apps.etl.transform.odata_transformer import (
    ODataTransformer
)


logger = logging.getLogger(__name__)


class TransformationService:

    @staticmethod
    def transform_records(
        records: list[dict[str, Any]],
        mapping: dict[str, str] | None = None,
        types: dict[str, str] | None = None,
        include_unmapped: bool = False,
    ) -> dict[str, Any]:

        started_at = datetime.now(timezone.utc)

        logger.info(
            "Iniciando transformación tradicional"
        )

        try:

            transformer = ODataTransformer(
                mapping=mapping,
                types=types,
                include_unmapped=include_unmapped,
            )

            transformed_records = transformer.transform(
                records
            )

            return TransformationService._build_result(
                transformed_records,
                started_at
            )

        except Exception:

            logger.exception(
                "Error durante la transformación tradicional"
            )

            return TransformationService._build_error(
                started_at
            )

    @staticmethod
    def transform_records_dynamic(
        records: list[dict[str, Any]],
        columns: list[dict[str, Any]],
        mapping: dict[str, str] | None = None,
        include_unmapped: bool = True,
    ) -> dict[str, Any]:

        started_at = datetime.now(timezone.utc)

        logger.info(
            "Iniciando transformación dinámica mediante metadatos OData"
        )

        try:

            transformer = ODataTransformer()

            transformed_records = transformer.transform_dynamic(
                records=records,
                columns=columns,
                mapping=mapping,
                include_unmapped=include_unmapped,
            )

            return TransformationService._build_result(
                transformed_records,
                started_at
            )

        except Exception:

            logger.exception(
                "Error durante la transformación dinámica"
            )

            return TransformationService._build_error(
                started_at
            )

    @staticmethod
    def _build_result(
        records: list[dict[str, Any]],
        started_at: datetime
    ) -> dict[str, Any]:

        finished_at = datetime.now(timezone.utc)

        return {
            "status": "success",
            "records_count": len(records),
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "records": records,
        }

    @staticmethod
    def _build_error(
        started_at: datetime
    ) -> dict[str, Any]:

        finished_at = datetime.now(timezone.utc)

        return {
            "status": "error",
            "records_count": 0,
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "records": [],
            "message": "Error durante la transformación de datos.",
        }
