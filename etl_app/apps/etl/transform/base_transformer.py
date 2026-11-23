from abc import ABC, abstractmethod
from typing import Any


class BaseTransformer(ABC):

    @abstractmethod
    def transform(
        self,
        records: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Transforma una lista de registros.

        Args:
            records: Datos extraídos de la fuente.

        Returns:
            Datos transformados.
        """
        pass