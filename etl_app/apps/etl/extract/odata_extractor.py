import logging
from typing import Any
from urllib.parse import urlparse, urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base_extractor import BaseExtractor


logger = logging.getLogger(__name__)


class ODataExtractor(BaseExtractor):

    def __init__(
        self,
        url: str,
        username: str | None = None,
        password: str | None = None,
        timeout: int = 60,
        max_retries: int = 3,
        page_size: int = 1000,
    ):
        self.url = url
        self.username = username
        self.password = password
        self.timeout = timeout
        self.page_size = page_size

        self._validate_url()

        self.session = requests.Session()

        # Configuración de reintentos
        retry_strategy = Retry(
            total=max_retries,
            connect=max_retries,
            read=max_retries,
            status=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Autenticación Basic Auth, cuando corresponda
        if username and password:
            self.session.auth = (username, password)

        self.session.headers.update({
            "Accept": "application/json",
        })

    def _validate_url(self) -> None:

        parsed_url = urlparse(self.url)

        if parsed_url.scheme not in ["http", "https"]:
            raise ValueError(
                "La URL OData debe utilizar HTTP o HTTPS."
            )

        if not parsed_url.netloc:
            raise ValueError(
                "La URL OData no contiene un host válido."
            )

        if parsed_url.username or parsed_url.password:
            raise ValueError(
                "No se permite incluir credenciales directamente en la URL."
            )

    def _get_records_from_response(
        self,
        response_data: dict[str, Any]
    ) -> list[dict[str, Any]]:

        # OData v4
        if "value" in response_data:
            return response_data["value"]

        # OData v2
        if "d" in response_data:

            data = response_data["d"]

            if isinstance(data, dict) and "results" in data:
                return data["results"]

            if isinstance(data, list):
                return data

            return [data]

        raise ValueError(
            "La respuesta no contiene una estructura OData reconocida."
        )

    def _get_next_link(
        self,
        response_data: dict[str, Any]
    ) -> str | None:

        # OData v4
        next_link = response_data.get("@odata.nextLink")

        if next_link:
            return next_link

        # OData v2
        data = response_data.get("d", {})

        if isinstance(data, dict):
            return data.get("__next")

        return None

    def extract(self) -> list[dict[str, Any]]:

        records = []

        next_url = self.url

        page_number = 1

        while next_url:

            logger.info(
                "Extrayendo página OData %s",
                page_number
            )

            response = self.session.get(
                next_url,
                timeout=self.timeout,
            )

            response.raise_for_status()

            response_data = response.json()

            page_records = self._get_records_from_response(
                response_data
            )

            records.extend(page_records)

            logger.info(
                "Página %s: %s registros obtenidos",
                page_number,
                len(page_records)
            )

            next_url = self._get_next_link(
                response_data
            )

            if next_url:
                next_url = self._validate_next_link(next_url)

            page_number += 1

        logger.info(
            "Extracción OData finalizada. Total de registros: %s",
            len(records)
        )

        return records

    def _validate_next_link(self, next_url: str) -> str:

        # Convertir enlaces relativos en enlaces absolutos
        absolute_url = urljoin(self.url, next_url)

        original_url = urlparse(self.url)
        next_link = urlparse(absolute_url)

        if next_link.scheme not in ["http", "https"]:
            raise ValueError(
                "El siguiente enlace OData tiene un esquema inválido."
            )

        if next_link.netloc != original_url.netloc:
            raise ValueError(
                "El siguiente enlace OData apunta a un host diferente."
            )

        return absolute_url