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
            "Iniciando proceso de transformación"
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

            finished_at = datetime.now(timezone.utc)

            return {
                "status": "success",
                "records_count": len(transformed_records),
                "started_at": started_at.isoformat(),
                "finished_at": finished_at.isoformat(),
                "records": transformed_records,
            }

        except Exception:

            logger.exception(
                "Error durante la transformación"
            )

            finished_at = datetime.now(timezone.utc)

            return {
                "status": "error",
                "records_count": 0,
                "started_at": started_at.isoformat(),
                "finished_at": finished_at.isoformat(),
                "records": [],
                "message": "Error durante la transformación de datos.",
            }