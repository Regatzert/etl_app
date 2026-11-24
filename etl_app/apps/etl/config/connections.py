
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

    # =================================================
    # SAP - BEARER TOKEN
    # =================================================

    # "sap": {
    #     "source_type": "odata",
    #     "auth_type": "bearer",
    #     "token_env": "SAP_ACCESS_TOKEN",
    #     "timeout_env": "ODATA_TIMEOUT",
    #     "max_retries_env": "ETL_MAX_RETRIES",
    # },

    # =================================================
    # EJEMPLO - BASIC AUTH
    # =================================================

    # "sistema_basic": {
    #     "source_type": "odata",
    #     "auth_type": "basic",
    #     "username_env": "BASIC_USERNAME",
    #     "password_env": "BASIC_PASSWORD",
    #     "timeout_env": "ODATA_TIMEOUT",
    #     "max_retries_env": "ETL_MAX_RETRIES",
    # },

    # =================================================
    # EJEMPLO - API KEY
    # =================================================

    # "sistema_api_key": {
    #     "source_type": "odata",
    #     "auth_type": "api_key",
    #     "key_env": "SYSTEM_API_KEY",
    #     "header_name": "X-API-Key",
    # },

    # =================================================
    # EJEMPLO - OAUTH 2.0
    # =================================================

    # "sistema_oauth": {
    #     "source_type": "odata",
    #     "auth_type": "oauth2_client_credentials",
    #     "token_url_env": "SYSTEM_TOKEN_URL",
    #     "client_id_env": "SYSTEM_CLIENT_ID",
    #     "client_secret_env": "SYSTEM_CLIENT_SECRET",
    #     "scope_env": "SYSTEM_SCOPE",
    #     "timeout": 60,
    # },

}
