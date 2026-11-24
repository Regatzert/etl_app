import logging
from typing import Any

from django.db import transaction

from .base_loader import BaseLoader
from etl_app.apps.etl.models import ETLDataRecord


logger = logging.getLogger(__name__)


class PostgreSQLLoader(BaseLoader):

    def __init__(
        self,
        batch_size: int = 1000
    ):

        if batch_size <= 0:
            raise ValueError(
                "El batch_size debe ser mayor que cero."
            )

        self.batch_size = batch_size

    def load(
        self,
        records: list[dict[str, Any]],
        dataset: str
    ) -> dict[str, Any]:

        logger.info(
            "Iniciando carga del dataset '%s'. Registros: %s",
            dataset,
            len(records)
        )

        if not dataset or not dataset.strip():

            return {
                "status": "error",
                "dataset": dataset,
                "records_count": 0,
                "message": "El dataset es obligatorio.",
            }

        if not records:

            return {
                "status": "success",
                "dataset": dataset,
                "records_count": 0,
                "message": "No existen registros para cargar.",
            }

        try:

            for record in records:

                if not isinstance(record, dict):

                    raise ValueError(
                        "Todos los registros deben ser diccionarios."
                    )

            objects = [
                ETLDataRecord(
                    dataset=dataset.strip(),
                    data=record
                )
                for record in records
            ]

            with transaction.atomic():

                for start in range(
                    0,
                    len(objects),
                    self.batch_size
                ):

                    batch = objects[
                        start:start + self.batch_size
                    ]

                    ETLDataRecord.objects.bulk_create(
                        batch,
                        batch_size=self.batch_size
                    )

            logger.info(
                "Carga completada. Dataset: %s. Registros: %s",
                dataset,
                len(records)
            )

            return {
                "status": "success",
                "dataset": dataset,
                "records_count": len(records),
                "message": "Carga completada correctamente.",
            }

        except Exception:

            logger.exception(
                "Error durante la carga del dataset '%s'",
                dataset
            )

            return {
                "status": "error",
                "dataset": dataset,
                "records_count": 0,
                "message": "Error durante la carga de datos.",
            }