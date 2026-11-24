
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
        auth=None,
        headers: dict | None = None,
        timeout: int = 60,
        max_retries: int = 3,
        page_size: int = 1000
    ):

        self.url = url
        self.timeout = timeout
        self.max_retries = max_retries
        self.page_size = page_size

        self.session = requests.Session()

        # =========================================
        # AUTENTICACIÓN
        # =========================================

        if auth:
            self.session.auth = auth

        if headers:
            self.session.headers.update(headers)

        self.session.headers.update({
            "Accept": "application/json"
        })

        # =========================================
        # CONFIGURACIÓN DE REINTENTOS
        # =========================================

        retry_strategy = Retry(
            total=max_retries,
            connect=max_retries,
            read=max_retries,
            status=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            respect_retry_after_header=True
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy
        )

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    # =========================================
    # VALIDACIÓN DE URL
    # =========================================

    def _validate_url(self) -> None:

        parsed_url = urlparse(self.url)

        if parsed_url.scheme not in ["http", "https"]:
            raise ValueError(
                "La URL OData debe utilizar HTTP o HTTPS."
            )

        if not parsed_url.netloc or not parsed_url.hostname:
            raise ValueError(
                "La URL OData no contiene un host válido."
            )

        if parsed_url.username or parsed_url.password:
            raise ValueError(
                "No se permite incluir credenciales directamente en la URL."
            )

        if parsed_url.fragment:
            raise ValueError(
                "La URL OData no debe contener fragmentos."
            )

    # =========================================
    # OBTENER REGISTROS DE RESPUESTA
    # =========================================

    def _get_records_from_response(
        self,
        response_data: dict[str, Any]
    ) -> list[dict[str, Any]]:

        # OData v4
        if "value" in response_data:

            records = response_data["value"]

            if not isinstance(records, list):
                raise ValueError(
                    "La propiedad 'value' de OData debe ser una lista."
                )

            return records

        # OData v2
        if "d" in response_data:

            data = response_data["d"]

            if isinstance(data, dict) and "results" in data:
                return data["results"]

            if isinstance(data, list):
                return data

            if isinstance(data, dict):
                return [data]

        raise ValueError(
            "La respuesta no contiene una estructura OData reconocida."
        )

    # =========================================
    # OBTENER SIGUIENTE PÁGINA
    # =========================================

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

    # =========================================
    # EXTRACCIÓN
    # =========================================

    def extract(self) -> list[dict[str, Any]]:

        self._validate_url()

        records = []

        next_url = self.url

        page_number = 1

        try:

            while next_url:

                logger.info(
                    "Extrayendo página OData %s",
                    page_number
                )

                response = self.session.get(
                    next_url,
                    timeout=self.timeout,
                    params=(
                        {"$top": self.page_size}
                        if page_number == 1
                        else None
                    )
                )

                response.raise_for_status()

                try:
                    response_data = response.json()

                except ValueError as error:
                    raise ValueError(
                        "La respuesta OData no contiene JSON válido."
                    ) from error

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

        finally:
            self.session.close()

        logger.info(
            "Extracción OData finalizada. Total de registros: %s",
            len(records)
        )

        return records

    # =========================================
    # VALIDAR NEXT LINK
    # =========================================

    def _validate_next_link(self, next_url: str) -> str:

        absolute_url = urljoin(self.url, next_url)

        original_url = urlparse(self.url)
        next_link = urlparse(absolute_url)

        if next_link.scheme not in ["http", "https"]:
            raise ValueError(
                "El siguiente enlace OData tiene un esquema inválido."
            )

        if not next_link.hostname:
            raise ValueError(
                "El siguiente enlace OData no contiene un host válido."
            )

        if next_link.username or next_link.password:
            raise ValueError(
                "El siguiente enlace OData no debe contener credenciales."
            )

        if next_link.fragment:
            raise ValueError(
                "El siguiente enlace OData no debe contener fragmentos."
            )

        original_host = (
            original_url.hostname.lower(),
            original_url.port or (
                443 if original_url.scheme == "https" else 80
            )
        )

        next_host = (
            next_link.hostname.lower(),
            next_link.port or (
                443 if next_link.scheme == "https" else 80
            )
        )

        if next_host != original_host:
            raise ValueError(
                "El siguiente enlace OData apunta a un host diferente."
            )

        if next_link.scheme != original_url.scheme:
            raise ValueError(
                "El siguiente enlace OData utiliza un protocolo diferente."
            )

        return absolute_url
