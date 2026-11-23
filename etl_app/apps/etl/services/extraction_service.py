import logging
from datetime import datetime, timezone
from typing import Any

from etl_app.apps.etl.extract.odata_extractor import ODataExtractor


logger = logging.getLogger(__name__)


class ExtractionService:

    @staticmethod
    def extract_from_odata(
        url: str,
        username: str | None = None,
        password: str | None = None,
        timeout: int = 60,
        max_retries: int = 3,
    ) -> dict[str, Any]:

        started_at = datetime.now(timezone.utc)

        logger.info("Iniciando extracción OData")

        try:

            extractor = ODataExtractor(
                url=url,
                username=username,
                password=password,
                timeout=timeout,
                max_retries=max_retries,
            )

            records = extractor.extract()

            finished_at = datetime.now(timezone.utc)

            result = {
                "status": "success",
                "source": "odata",
                "started_at": started_at.isoformat(),
                "finished_at": finished_at.isoformat(),
                "records_count": len(records),
                "records": records,
            }

            logger.info(
                "Extracción completada correctamente. "
                "Registros: %s",
                len(records),
            )

            return result

        except Exception:

            logger.exception(
                "Error durante el proceso de extracción OData"
            )

            finished_at = datetime.now(timezone.utc)

            return {
                "status": "error",
                "source": "odata",
                "started_at": started_at.isoformat(),
                "finished_at": finished_at.isoformat(),
                "records_count": 0,
                "records": [],
                "message": "Error durante la extracción de datos.",
            }