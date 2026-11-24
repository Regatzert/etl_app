
import logging
from typing import Any

from django.conf import settings
from django.db import models, transaction
from django.db.models import Model

from etl_app.apps.etl.config.databases import DATABASE_CONNECTIONS

from .base_loader import BaseLoader


logger = logging.getLogger(__name__)


class PostgreSQLLoader(BaseLoader):

    SUPPORTED_STRATEGIES = {
        "replace_all",
        "replace_by_filter",
    }

    SUPPORTED_LOOKUPS = {
        "exact",
        "in",
        "range",
        "gt",
        "gte",
        "lt",
        "lte",
        "isnull",
    }

    def __init__(
        self,
        batch_size: int = 1000,
        database: str = "etl_platform",
    ):

        if batch_size <= 0:
            raise ValueError(
                "El batch_size debe ser mayor que cero."
            )

        self.batch_size = batch_size
        self.database = database
        self.database_alias = self._resolve_database_alias(database)

    # =========================================
    # RESOLVER BASE DE DATOS
    # =========================================

    @staticmethod
    def _resolve_database_alias(database: str) -> str:

        configuration = DATABASE_CONNECTIONS.get(database)

        if not configuration:
            raise ValueError(
                f"La base de datos '{database}' "
                "no está registrada en el catálogo."
            )

        alias = configuration.get("django_alias")

        if not alias:
            raise ValueError(
                f"La conexión '{database}' no tiene django_alias."
            )

        if alias not in settings.DATABASES:
            raise ValueError(
                f"El alias Django '{alias}' no está configurado "
                "en settings.DATABASES."
            )

        return alias

    # =========================================
    # LOAD
    # =========================================

    def load(
        self,
        records: list[dict[str, Any]],
        model: type[Model],
        strategy: str,
        delete_filter: dict[str, Any] | None = None,
        allow_empty: bool = False,
    ) -> dict[str, Any]:

        try:

            self._validate_model(model)
            self._validate_records(records, model)

            if strategy not in self.SUPPORTED_STRATEGIES:
                raise ValueError(
                    f"Estrategia de carga no soportada: {strategy}"
                )

            if strategy == "replace_all":

                return self.replace_all(
                    records=records,
                    model=model,
                    allow_empty=allow_empty,
                )

            if strategy == "replace_by_filter":

                return self.replace_by_filter(
                    records=records,
                    model=model,
                    delete_filter=delete_filter,
                    allow_empty=allow_empty,
                )

        except Exception as error:

            logger.exception(
                "Error durante la carga en el modelo %s.",
                getattr(model, "__name__", str(model)),
            )

            return self._error_result(
                model=model,
                strategy=strategy,
                error=error,
            )

    # =========================================
    # REEMPLAZO COMPLETO
    # =========================================

    def replace_all(
        self,
        records: list[dict[str, Any]],
        model: type[Model],
        allow_empty: bool = False,
    ) -> dict[str, Any]:

        if not records and not allow_empty:

            return self._empty_result(
                model=model,
                strategy="replace_all",
            )

        try:

            objects = [
                model(**record)
                for record in records
            ]

            with transaction.atomic(using=self.database_alias):

                deleted_count, _ = (
                    model.objects.using(
                        self.database_alias
                    ).all().delete()
                )

                self._bulk_insert(objects, model)

            logger.info(
                "Reemplazo completo finalizado. "
                "Modelo: %s. Base: %s. "
                "Eliminados: %s. Insertados: %s.",
                model.__name__,
                self.database,
                deleted_count,
                len(objects),
            )

            return {
                "status": "success",
                "model": model.__name__,
                "database": self.database,
                "database_alias": self.database_alias,
                "strategy": "replace_all",
                "deleted_count": deleted_count,
                "records_count": len(objects),
                "message": (
                    "Reemplazo completo realizado correctamente."
                ),
            }

        except Exception as error:

            logger.exception(
                "Error durante el reemplazo completo de %s.",
                model.__name__,
            )

            return self._error_result(
                model=model,
                strategy="replace_all",
                error=error,
            )

    # =========================================
    # REEMPLAZO POR FILTRO
    # =========================================

    def replace_by_filter(
        self,
        records: list[dict[str, Any]],
        model: type[Model],
        delete_filter: dict[str, Any] | None,
        allow_empty: bool = False,
    ) -> dict[str, Any]:

        if not delete_filter:
            raise ValueError(
                "La estrategia replace_by_filter requiere "
                "un delete_filter válido."
            )

        self._validate_delete_filter(
            model=model,
            delete_filter=delete_filter,
        )

        if not records and not allow_empty:

            return self._empty_result(
                model=model,
                strategy="replace_by_filter",
            )

        try:

            objects = [
                model(**record)
                for record in records
            ]

            # Verificar que todos los registros pertenezcan
            # al mismo conjunto que se va a reemplazar.
            self._validate_records_match_filter(
                records=records,
                model=model,
                delete_filter=delete_filter,
            )

            with transaction.atomic(using=self.database_alias):

                deleted_count, _ = (
                    model.objects.using(
                        self.database_alias
                    ).filter(**delete_filter).delete()
                )

                self._bulk_insert(objects, model)

            logger.info(
                "Reemplazo filtrado finalizado. "
                "Modelo: %s. Base: %s. "
                "Eliminados: %s. Insertados: %s.",
                model.__name__,
                self.database,
                deleted_count,
                len(objects),
            )

            return {
                "status": "success",
                "model": model.__name__,
                "database": self.database,
                "database_alias": self.database_alias,
                "strategy": "replace_by_filter",
                "delete_filter": delete_filter,
                "deleted_count": deleted_count,
                "records_count": len(objects),
                "message": (
                    "Reemplazo filtrado realizado correctamente."
                ),
            }

        except Exception as error:

            logger.exception(
                "Error durante el reemplazo filtrado de %s.",
                model.__name__,
            )

            return self._error_result(
                model=model,
                strategy="replace_by_filter",
                error=error,
            )

    # =========================================
    # INSERTAR POR LOTES
    # =========================================

    def _bulk_insert(
        self,
        objects: list[Model],
        model: type[Model],
    ) -> None:

        manager = model.objects.db_manager(
            self.database_alias
        )

        for start in range(0, len(objects), self.batch_size):

            batch = objects[
                start:start + self.batch_size
            ]

            manager.bulk_create(
                batch,
                batch_size=self.batch_size,
            )

    # =========================================
    # VALIDAR MODELO
    # =========================================

    @staticmethod
    def _validate_model(model: type[Model]) -> None:

        if not isinstance(model, type) or not issubclass(
            model,
            models.Model,
        ):
            raise ValueError(
                "El destino debe ser una clase de modelo Django."
            )

        if model._meta.abstract:
            raise ValueError(
                "No se puede utilizar un modelo Django abstracto."
            )

        if model._meta.proxy:
            raise ValueError(
                "No se puede utilizar directamente un modelo proxy."
            )

    # =========================================
    # VALIDAR REGISTROS
    # =========================================

    @staticmethod
    def _validate_records(
        records: list[dict[str, Any]],
        model: type[Model],
    ) -> None:

        if not isinstance(records, list):
            raise ValueError(
                "Los registros deben proporcionarse como una lista."
            )

        allowed_fields = {"pk"}

        for field in model._meta.concrete_fields:
            allowed_fields.add(field.name)
            allowed_fields.add(field.attname)

        for index, record in enumerate(records):

            if not isinstance(record, dict):
                raise ValueError(
                    f"El registro {index} no es un diccionario."
                )

            unknown_fields = set(record.keys()) - allowed_fields

            if unknown_fields:
                raise ValueError(
                    f"El registro {index} contiene campos que "
                    f"no existen en {model.__name__}: "
                    f"{sorted(unknown_fields)}"
                )

    # =========================================
    # VALIDAR FILTRO DE ELIMINACIÓN
    # =========================================

    @classmethod
    def _validate_delete_filter(
        cls,
        model: type[Model],
        delete_filter: dict[str, Any],
    ) -> None:

        if not isinstance(delete_filter, dict) or not delete_filter:
            raise ValueError(
                "El filtro de eliminación debe ser un diccionario "
                "no vacío."
            )

        fields = {
            field.name: field
            for field in model._meta.concrete_fields
        }

        fields.update({
            field.attname: field
            for field in model._meta.concrete_fields
        })

        for lookup in delete_filter:

            parts = lookup.split("__")

            field_name = parts[0]
            lookup_type = parts[1] if len(parts) > 1 else "exact"

            
            if field_name not in fields:
                raise ValueError(
                    f"El campo '{field_name}' no existe en "
                    f"el modelo {model.__name}."
                )

            if lookup_type not in cls.SUPPORTED_LOOKUPS:
                raise ValueError(
                    f"El operador '{lookup_type}' no está permitido."
                )

            if len(parts) > 2:
                raise ValueError(
                    f"No se permiten relaciones u operadores "
                    f"anidados en el filtro: {lookup}."
                )

    # =========================================
    # VALIDAR QUE LOS REGISTROS COINCIDAN
    # CON EL FILTRO DE ELIMINACIÓN
    # =========================================

    @classmethod
    def _validate_records_match_filter(
        cls,
        records: list[dict[str, Any]],
        model: type[Model],
        delete_filter: dict[str, Any],
    ) -> None:

        fields = {
            field.name: field
            for field in model._meta.concrete_fields
        }

        fields.update({
            field.attname: field
            for field in model._meta.concrete_fields
        })

        for index, record in enumerate(records):

            for lookup, expected in delete_filter.items():

                parts = lookup.split("__")

                field_name = parts[0]
                lookup_type = (
                    parts[1] if len(parts) > 1 else "exact"
                )

                field = fields[field_name]

                if field.attname in record:
                    raw_value = record[field.attname]

                elif field.name in record:
                    raw_value = record[field.name]

                else:
                    raise ValueError(
                        f"El registro {index} no contiene el campo "
                        f"'{field.name}' requerido por el filtro."
                    )

                value = cls._convert_filter_value(
                    field,
                    raw_value
                )

                if lookup_type == "isnull":

                    matches = (
                        (value is None) == expected
                    )

                elif lookup_type == "in":

                    if not isinstance(expected, (list, tuple, set)):
                        raise ValueError(
                            f"El filtro '{lookup}' requiere "
                            "una lista o tupla."
                        )

                    converted = [
                        cls._convert_filter_value(field, item)
                        for item in expected
                    ]

                    matches = value in converted

                elif lookup_type == "range":

                    if not isinstance(expected, (list, tuple)) or len(expected) != 2:
                        raise ValueError(
                            f"El filtro '{lookup}' requiere "
                            "exactamente dos valores."
                        )

                    lower = cls._convert_filter_value(
                        field, expected[0]
                    )

                    upper = cls._convert_filter_value(
                        field, expected[1]
                    )

                    matches = (
                        value is not None
                        and lower <= value <= upper
                    )

                else:

                    converted = cls._convert_filter_value(
                        field,
                        expected
                    )

                    if lookup_type == "exact":
                        matches = value == converted

                    elif lookup_type == "gt":
                        matches = value is not None and value > converted

                    elif lookup_type == "gte":
                        matches = value is not None and value >= converted

                    elif lookup_type == "lt":
                        matches = value is not None and value < converted

                    elif lookup_type == "lte":
                        matches = value is not None and value <= converted

                    else:
                        matches = False

                if not matches:
                    raise ValueError(
                        f"El registro {index} no cumple el filtro "
                        f"'{lookup}' configurado para la carga."
                    )


    @staticmethod
    def _convert_filter_value(field, value):

        if value is None:
            return None

        if field.is_relation:
            return field.target_field.to_python(value)

        return field.to_python(value)

    # =========================================
    # RESULTADO DE CARGA VACÍA
    # =========================================

    @staticmethod
    def _empty_result(
        self,
        model: type[Model],
        strategy: str,
    ) -> dict[str, Any]:

        logger.warning(
            "Carga omitida porque no existen registros. "
            "Modelo: %s. Estrategia: %s.",
            model.__name__,
            strategy,
        )

        return {
            "status": "success",
            "model": model.__name__,
            "database": self.database,
            "database_alias": self.database_alias,
            "strategy": strategy,
            "deleted_count": 0,
            "records_count": 0,
            "message": (
                "No existen registros para cargar. "
                "No se modificó la información existente."
            ),
        }

    # =========================================
    # RESULTADO DE ERROR
    # =========================================

    def _error_result(
        self,
        model,
        strategy,
        error,
    ) -> dict[str, Any]:

        return {
            "status": "error",
            "model": getattr(model, "__name__", None),
            "database": self.database,
            "strategy": strategy,
            "records_count": 0,
            "deleted_count": 0,
            "message": (
                "No se pudo completar la operación de carga. "
                "Revisa los registros de la aplicación para más detalles."
            ),
        }
