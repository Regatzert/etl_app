from abc import ABC, abstractmethod
from typing import Any


class BaseLoader(ABC):

    @abstractmethod
    def load(
        self,
        records: list[dict[str, Any]],
        dataset: str
    ) -> dict[str, Any]:
        """
        Carga registros en el destino.

        Args:
            records: Registros transformados.
            dataset: Nombre lógico del conjunto de datos.

        Returns:
            Resultado de la carga.
        """
        pass