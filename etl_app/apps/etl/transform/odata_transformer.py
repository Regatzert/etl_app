import logging
from typing import Any
from decimal import Decimal
from datetime import date, datetime

from .base_transformer import BaseTransformer


logger = logging.getLogger(__name__)


class ODataTransformer(BaseTransformer):

    SUPPORTED_TYPES = {
        "string",
        "integer",
        "decimal",
        "float",
        "boolean",
        "date",
        "datetime",
    }

    def __init__(
        self,
        mapping: dict[str, str] | None = None,
        types: dict[str, str] | None = None,
        include_unmapped: bool = False,
    ):

        self.mapping = mapping or {}
        self.types = types or {}
        self.include_unmapped = include_unmapped

        self._validate_types()

    def _validate_types(self):

        for source_field, data_type in self.types.items():

            if data_type not in self.SUPPORTED_TYPES:

                raise ValueError(
                    f"Tipo de dato no soportado para "
                    f"{source_field}: {data_type}"
                )

    def transform(
        self,
        records: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:

        logger.info(
            "Iniciando transformación de %s registros",
            len(records)
        )

        transformed_records = []

        for record in records:

            transformed_record = self._transform_record(
                record
            )

            transformed_records.append(
                transformed_record
            )

        logger.info(
            "Transformación completada. Registros: %s",
            len(transformed_records)
        )

        return transformed_records

    def _transform_record(
        self,
        record: dict[str, Any]
    ) -> dict[str, Any]:

        transformed_record = {}

        for source_field, value in record.items():

            target_field = self.mapping.get(
                source_field
            )

            if target_field:

                data_type = self.types.get(
                    source_field,
                    "string"
                )

                normalized_value = self._normalize_value(
                    value,
                    data_type
                )

                transformed_record[target_field] = (
                    normalized_value
                )

            elif self.include_unmapped:

                normalized_field = (
                    self._normalize_field_name(
                        source_field
                    )
                )

                transformed_record[normalized_field] = (
                    self._normalize_value(
                        value,
                        "string"
                    )
                )

        return transformed_record

    @staticmethod
    def _normalize_field_name(
        field_name: str
    ) -> str:

        return field_name.lower()

    def _normalize_value(
        self,
        value: Any,
        data_type: str
    ) -> Any:

        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()

            if value == "":
                return None

        if data_type == "string":
            return str(value)

        if data_type == "integer":
            return int(value)

        if data_type == "decimal":
            return Decimal(str(value))

        if data_type == "float":
            return float(value)

        if data_type == "boolean":
            return self._convert_boolean(value)

        if data_type == "date":
            return self._convert_date(value)

        if data_type == "datetime":
            return self._convert_datetime(value)

        raise ValueError(
            f"Tipo de dato no soportado: {data_type}"
        )

    @staticmethod
    def _convert_boolean(value: Any) -> bool:

        if isinstance(value, bool):
            return value

        if isinstance(value, int):
            if value in (0, 1):
                return bool(value)

        if isinstance(value, str):

            normalized_value = value.lower()

            if normalized_value in (
                "true",
                "1",
                "yes",
                "y",
                "si",
                "sí",
            ):
                return True

            if normalized_value in (
                "false",
                "0",
                "no",
                "n",
            ):
                return False

        raise ValueError(
            f"No se puede convertir '{value}' a boolean."
        )

    @staticmethod
    def _convert_date(value: Any) -> date:

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        return date.fromisoformat(str(value))

    @staticmethod
    def _convert_datetime(value: Any) -> datetime:

        if isinstance(value, datetime):
            return value

        return datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )