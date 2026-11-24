
from abc import ABC, abstractmethod
from typing import Any

from django.db.models import Model


class BaseLoader(ABC):

    @abstractmethod
    def load(
        self,
        records: list[dict[str, Any]],
        model: type[Model],
        strategy: str,
        delete_filter: dict[str, Any] | None = None,
        allow_empty: bool = False,
    ) -> dict[str, Any]:
        """
        Carga registros en un modelo Django.

        Args:
            records: Registros transformados.
            model: Modelo Django de destino.
            strategy: Estrategia de carga:
                - replace_all
                - replace_by_filter
            delete_filter: Condiciones para eliminar registros
                existentes cuando se utiliza replace_by_filter.
            allow_empty: Permite ejecutar el borrado aunque
                la extracción no haya devuelto registros.

        Returns:
            Resultado de la carga.
        """
        pass
