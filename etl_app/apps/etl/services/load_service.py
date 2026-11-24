import logging
from datetime import datetime, timezone
from typing import Any

from etl_app.apps.etl.load.postgresql_loader import (
    PostgreSQLLoader
)


logger = logging.getLogger(__name__)


class LoadService:

    @staticmethod
    def load_records(
        records: list[dict[str, Any]],
        dataset: str,
        batch_size: int = 1000,
    ) -> dict[str, Any]:

        started_at = datetime.now(timezone.utc)

        logger.info(
            "Iniciando servicio de carga. Dataset: %s",
            dataset
        )

        loader = PostgreSQLLoader(
            batch_size=batch_size
        )

        result = loader.load(
            records=records,
            dataset=dataset
        )

        finished_at = datetime.now(timezone.utc)

        result["started_at"] = started_at.isoformat()
        result["finished_at"] = finished_at.isoformat()

        return result