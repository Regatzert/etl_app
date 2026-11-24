
import logging
from datetime import datetime, timezone

from etl_app.apps.etl.extract.odata_extractor import ODataExtractor


logger = logging.getLogger(__name__)


class ExtractionService:

    @staticmethod
    def extract_from_odata(
        connection_name: str,
        url: str,
        auth=None,
        headers: dict | None = None,
        timeout: int = 60,
        max_retries: int = 3,
    ) -> dict:

        started_at = datetime.now(timezone.utc)

        result = {
            "status": "running",
            "source": url,
            "connection": connection_name,
            "started_at": started_at.isoformat(),
            "finished_at": None,
            "duration_seconds": None,
            "records_count": 0,
            "records": [],
            "message": "Extracción iniciada.",
        }

        try:

            logger.info(
                "Iniciando extracción OData. Conexión: %s",
                connection_name
            )

            extractor = ODataExtractor(
                url=url,
                auth=auth,
                headers=headers,
                timeout=timeout,
                max_retries=max_retries
            )

            records = extractor.extract()

            result["status"] = "success"
            result["records"] = records
            result["records_count"] = len(records)
            result["message"] = (
                "Extracción OData completada correctamente."
            )

            logger.info(
                "Extracción completada. Registros obtenidos: %s",
                len(records)
            )

        except Exception as error:

            logger.exception(
                "Error durante la extracción OData."
            )

            result["status"] = "error"
            result["message"] = str(error)

        finally:

            finished_at = datetime.now(timezone.utc)

            result["finished_at"] = finished_at.isoformat()

            result["duration_seconds"] = (
                finished_at - started_at
            ).total_seconds()

        return result
