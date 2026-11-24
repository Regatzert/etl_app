
import logging

from typing import Any
from decimal import Decimal
from datetime import date, datetime, time
from uuid import UUID
import base64

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
        "time",
        "uuid",
        "binary",
    }

    # Conversión automática desde tipos OData a tipos internos.
    EDM_TYPE_MAPPING = {
        "Edm.String": "string",
        "Edm.Int16": "integer",
        "Edm.Int32": "integer",
        "Edm.Int64": "integer",
        "Edm.Decimal": "decimal",
        "Edm.Double": "float",
        "Edm.Single": "float",
        "Edm.Boolean": "boolean",
        "Edm.Date": "date",
        "Edm.DateTimeOffset": "datetime",
        "Edm.TimeOfDay": "time",
        "Edm.Guid": "uuid",
        "Edm.Binary": "binary",
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

    # =====================================================
    # VALIDACIÓN
    # =====================================================

    def _validate_types(self):

        for source_field, data_type in self.types.items():

            if data_type not in self.SUPPORTED_TYPES:

                raise ValueError(
                    f"Tipo de dato no soportado para "
                    f"{source_field}: {data_type}"
                )

    # =====================================================
    # TRANSFORMACIÓN TRADICIONAL
    # =====================================================

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

            transformed_record = self._transform_record(record)

            transformed_records.append(transformed_record)

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

            target_field = self.mapping.get(source_field)

            if target_field:

                data_type = self.types.get(
                    source_field,
                    "string"
                )

                transformed_record[target_field] = (
                    self._normalize_value(value, data_type)
                )

            elif self.include_unmapped:

                normalized_field = self._normalize_field_name(
                    source_field
                )

                transformed_record[normalized_field] = (
                    self._normalize_value(value, "string")
                )

        return transformed_record

    # =====================================================
    # TRANSFORMACIÓN DINÁMICA MEDIANTE METADATOS ODATA
    # =====================================================

    def transform_dynamic(
        self,
        records: list[dict[str, Any]],
        columns: list[dict[str, Any]],
        mapping: dict[str, str] | None = None,
        include_unmapped: bool = True,
    ) -> list[dict[str, Any]]:

        logger.info(
            "Iniciando transformación dinámica de %s registros",
            len(records)
        )

        mapping = mapping or {}

        # Obtener automáticamente los tipos desde los metadatos.
        metadata_types = {
            column["name"]: self.EDM_TYPE_MAPPING.get(
                column["odata_type"]
            )
            for column in columns
        }

        transformed_records = []

        for record_index, record in enumerate(records):

            transformed_record = {}

            for source_field, value in record.items():

                data_type = metadata_types.get(source_field)

                if data_type is None:
                    if include_unmapped:
                        target_field = mapping.get(
                            source_field,
                            source_field
                        )
                        transformed_record[target_field] = value

                    continue

                # Si existe un mapeo explícito, utilizarlo.
                # Si no existe, conservar el campo solamente
                # cuando include_unmapped=True.
                target_field = mapping.get(source_field)

                if target_field is None:

                    if not include_unmapped:
                        continue

                    target_field = source_field

                try:

                    transformed_record[target_field] = (
                        self._normalize_value(value, data_type)
                    )

                except (ValueError, TypeError, ArithmeticError) as error:

                    raise ValueError(
                        f"Error transformando el campo "
                        f"'{source_field}' del registro "
                        f"{record_index}: {error}"
                    ) from error

            transformed_records.append(transformed_record)

        logger.info(
            "Transformación dinámica completada. Registros: %s",
            len(transformed_records)
        )

        return transformed_records

    # =====================================================
    # NORMALIZACIÓN DE CAMPOS
    # =====================================================

    @staticmethod
    def _normalize_field_name(
        field_name: str
    ) -> str:

        return field_name.lower()

    # =====================================================
    # CONVERSIÓN DE VALORES
    # =====================================================

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

        if data_type == "time":
            return self._convert_time(value)

        if data_type == "uuid":
            return UUID(str(value))

        if data_type == "binary":
            return self._convert_binary(value)

        raise ValueError(
            f"Tipo de dato no soportado: {data_type}"
        )

    # =====================================================
    # CONVERSIÓN BOOLEAN
    # =====================================================

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

    # =====================================================
    # CONVERSIÓN DATE
    # =====================================================

    @staticmethod
    def _convert_date(value: Any) -> date:

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        return date.fromisoformat(str(value))

    # =====================================================
    # CONVERSIÓN DATETIME
    # =====================================================

    @staticmethod
    def _convert_datetime(value: Any) -> datetime:

        if isinstance(value, datetime):
            return value

        return datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )

    # =====================================================
    # CONVERSIÓN TIME
    # =====================================================

    @staticmethod
    def _convert_time(value: Any) -> time:

        if isinstance(value, time):
            return value

        return time.fromisoformat(str(value))

    # =====================================================
    # CONVERSIÓN BINARY
    # =====================================================

    @staticmethod
    def _convert_binary(value: Any) -> bytes:

        if isinstance(value, bytes):
            return value

        return base64.b64decode(value, validate=True)
