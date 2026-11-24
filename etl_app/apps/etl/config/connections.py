
CONNECTIONS = {

    # =================================================
    # NORTHWIND - SIN AUTENTICACIÓN
    # =================================================

    "northwind": {
        "source_type": "odata",
        "auth_type": "none",
        "timeout_env": "ODATA_TIMEOUT",
        "max_retries_env": "ETL_MAX_RETRIES",
    },

    # =========================================================
    # 2. SAP - ODATA CON BEARER TOKEN
    # =========================================================
    #
    # Para servicios SAP que entreguen un Access Token
    # previamente obtenido.
    #
    # El token se configura en el archivo .env.
    #
    # Activar cuando se integre SAP:
    # 1. Completar SAP_ACCESS_TOKEN en .env.
    # 2. Descomentar esta conexión.
    #
    # =========================================================

    # "sap": {
    #     "source_type": "odata",
    #     "auth_type": "bearer",
    #     "token_env": "SAP_ACCESS_TOKEN",
    #     "timeout_env": "ODATA_TIMEOUT",
    #     "max_retries_env": "ETL_MAX_RETRIES",
    # },

    # =========================================================
    # SAP - ODATA CON BASIC AUTH
    # =========================================================
    #
    # Autenticación mediante usuario y contraseña.
    #
    # Las credenciales se obtienen desde el archivo .env.
    #
    # =========================================================

    # "sap": {
    #     "source_type": "odata",
    #     "auth_type": "basic",
    #     "username_env": "SAP_USERNAME",
    #     "password_env": "SAP_PASSWORD",
    #     "timeout_env": "ODATA_TIMEOUT",
    #     "max_retries_env": "ETL_MAX_RETRIES",
    # },

    # =========================================================
    # 3. SAP - ODATA CON OAUTH 2.0 CLIENT CREDENTIALS
    # =========================================================
    #
    # Alternativa para SAP y servicios empresariales
    # que utilizan OAuth 2.0.
    #
    # El sistema obtiene el Access Token automáticamente
    # mediante client_id y client_secret.
    #
    # Requiere:
    # - URL del servidor de autenticación.
    # - Client ID.
    # - Client Secret.
    # - Scope, cuando corresponda.
    #
    # Activar solamente si el proveedor utiliza este flujo.
    #
    # =========================================================

    # "sap_oauth": {
    #     "source_type": "odata",
    #     "auth_type": "oauth2_client_credentials",
    #     "token_url_env": "SAP_TOKEN_URL",
    #     "client_id_env": "SAP_CLIENT_ID",
    #     "client_secret_env": "SAP_CLIENT_SECRET",
    #     "scope_env": "SAP_SCOPE",
    #     "timeout": 60,
    # },


    # =========================================================
    # 4. SISTEMA EXTERNO - BASIC AUTH
    # =========================================================
    #
    # Para servicios OData que utilizan usuario y contraseña.
    #
    # Ejemplos:
    # - ERP empresarial.
    # - Sistemas internos.
    # - Servicios de proveedores.
    #
    # Las credenciales se obtienen desde .env.
    #
    # =========================================================

    # "sistema_basic": {
    #     "source_type": "odata",
    #     "auth_type": "basic",
    #     "username_env": "EXTERNAL_USERNAME",
    #     "password_env": "EXTERNAL_PASSWORD",
    #     "timeout_env": "ODATA_TIMEOUT",
    #     "max_retries_env": "ETL_MAX_RETRIES",
    # },


    # =========================================================
    # 5. SISTEMA EXTERNO - API KEY
    # =========================================================
    #
    # Para servicios que solicitan una API Key en una cabecera.
    #
    # Ejemplo:
    # X-API-Key: valor_de_la_api_key
    #
    # El nombre de la cabecera depende del proveedor.
    #
    # =========================================================

    # "sistema_api_key": {
    #     "source_type": "odata",
    #     "auth_type": "api_key",
    #     "key_env": "EXTERNAL_API_KEY",
    #     "header_name": "X-API-Key",
    # },


    # =========================================================
    # 6. SISTEMA EXTERNO - OAUTH 2.0
    # =========================================================
    #
    # Plantilla para cualquier proveedor externo que utilice
    # OAuth 2.0 Client Credentials.
    #
    # Puede utilizarse para:
    # - ERP.
    # - Plataformas empresariales.
    # - APIs corporativas.
    # - Servicios de terceros.
    #
    # =========================================================

    # "sistema_oauth": {
    #     "source_type": "odata",
    #     "auth_type": "oauth2_client_credentials",
    #     "token_url_env": "EXTERNAL_TOKEN_URL",
    #     "client_id_env": "EXTERNAL_CLIENT_ID",
    #     "client_secret_env": "EXTERNAL_CLIENT_SECRET",
    #     "scope_env": "EXTERNAL_SCOPE",
    #     "timeout": 60,
    # },

}
