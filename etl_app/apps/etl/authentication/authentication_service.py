
import logging
import os
import threading
import time
from typing import Any

import requests
from requests.auth import HTTPBasicAuth

from etl_app.apps.etl.config.connections import CONNECTIONS


logger = logging.getLogger(__name__)


class AuthenticationService:

    _token_cache: dict[str, dict[str, Any]] = {}
    _cache_lock = threading.Lock()

    @classmethod
    def get_authentication(
        cls,
        connection_name: str,
    ) -> dict[str, Any]:

        configuration = CONNECTIONS.get(connection_name)

        if configuration is None:
            raise ValueError(
                f"No existe la conexión configurada: {connection_name}"
            )

        auth_type = configuration.get("auth_type", "none")

        logger.info(
            "Resolviendo autenticación para conexión '%s'. Tipo: %s.",
            connection_name,
            auth_type,
        )

        if auth_type == "none":
            return cls._no_authentication()

        if auth_type == "basic":
            return cls._basic_authentication(configuration)

        if auth_type == "bearer":
            return cls._bearer_authentication(configuration)

        if auth_type == "api_key":
            return cls._api_key_authentication(configuration)

        if auth_type == "oauth2_client_credentials":
            return cls._oauth2_authentication(
                connection_name,
                configuration,
            )

        raise ValueError(
            f"Tipo de autenticación no soportado: {auth_type}"
        )

    @staticmethod
    def _no_authentication() -> dict[str, Any]:

        return {
            "auth": None,
            "headers": {},
        }

    @staticmethod
    def _basic_authentication(
        configuration: dict[str, Any],
    ) -> dict[str, Any]:

        username_env = configuration.get("username_env")
        password_env = configuration.get("password_env")

        if not username_env or not password_env:
            raise ValueError(
                "Basic Auth requiere username_env y password_env."
            )

        username = os.getenv(username_env)
        password = os.getenv(password_env)

        if not username or not password:
            raise ValueError(
                "Faltan las credenciales configuradas para Basic Auth."
            )

        return {
            "auth": HTTPBasicAuth(username, password),
            "headers": {},
        }

    @staticmethod
    def _bearer_authentication(
        configuration: dict[str, Any],
    ) -> dict[str, Any]:

        token_env = configuration.get("token_env")

        if not token_env:
            raise ValueError(
                "Bearer Auth requiere token_env."
            )

        token = os.getenv(token_env)

        if not token:
            raise ValueError(
                f"No se encontró el token configurado en {token_env}."
            )

        return {
            "auth": None,
            "headers": {
                "Authorization": f"Bearer {token}",
            },
        }

    @staticmethod
    def _api_key_authentication(
        configuration: dict[str, Any],
    ) -> dict[str, Any]:

        key_env = configuration.get("key_env")
        header_name = configuration.get(
            "header_name",
            "X-API-Key",
        )

        if not key_env:
            raise ValueError(
                "API Key requiere key_env."
            )

        api_key = os.getenv(key_env)

        if not api_key:
            raise ValueError(
                f"No se encontró la API Key configurada en {key_env}."
            )

        return {
            "auth": None,
            "headers": {
                header_name: api_key,
            },
        }

    @classmethod
    def _oauth2_authentication(
        cls,
        connection_name: str,
        configuration: dict[str, Any],
    ) -> dict[str, Any]:

        token = cls._get_oauth2_token(
            connection_name,
            configuration,
        )

        return {
            "auth": None,
            "headers": {
                "Authorization": f"Bearer {token}",
            },
        }

    @classmethod
    def _get_oauth2_token(
        cls,
        connection_name: str,
        configuration: dict[str, Any],
    ) -> str:

        with cls._cache_lock:

            cached_token = cls._token_cache.get(connection_name)

            if cached_token and time.time() < cached_token["expires_at"]:
                return cached_token["access_token"]

            token_url_env = configuration.get("token_url_env")
            client_id_env = configuration.get("client_id_env")
            client_secret_env = configuration.get("client_secret_env")

            if not all((
                token_url_env,
                client_id_env,
                client_secret_env,
            )):
                raise ValueError(
                    "OAuth 2.0 requiere token_url_env, "
                    "client_id_env y client_secret_env."
                )

            token_url = os.getenv(token_url_env)
            client_id = os.getenv(client_id_env)
            client_secret = os.getenv(client_secret_env)

            if not all((token_url, client_id, client_secret)):
                raise ValueError(
                    "Faltan variables de entorno para OAuth 2.0."
                )

            scope_env = configuration.get("scope_env")
            scope = os.getenv(scope_env) if scope_env else None

            payload = {
                "grant_type": "client_credentials",
            }

            if scope:
                payload["scope"] = scope

            response = requests.post(
                token_url,
                data=payload,
                auth=(client_id, client_secret),
                timeout=configuration.get("timeout", 60),
            )

            response.raise_for_status()

            token_data = response.json()

            access_token = token_data.get("access_token")

            if not access_token:
                raise ValueError(
                    "El servidor OAuth 2.0 no devolvió access_token."
                )

            expires_in = int(token_data.get("expires_in", 3600))

            # Renovar un minuto antes de la expiración.
            cache_duration = max(expires_in - 60, 0)

            cls._token_cache[connection_name] = {
                "access_token": access_token,
                "expires_at": time.time() + cache_duration,
            }

            logger.info(
                "Token OAuth 2.0 obtenido para '%s'.",
                connection_name,
            )

            return access_token
