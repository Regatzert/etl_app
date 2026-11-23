from abc import ABC, abstractmethod
from typing import Any


class BaseExtractor(ABC):

    @abstractmethod
    def extract(self) -> list[dict[str, Any]]:
        """
        Extrae información desde una fuente externa.

        Returns:
            Lista de registros representados como diccionarios.
        """
        pass