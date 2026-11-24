
DATABASE_CONNECTIONS = {

    "etl_platform": {
        "django_alias": "default",
        "description": "Base de datos principal de la plataforma ETL",
    },

    # Ejemplo para una futura instancia:
    #
    # "reporting": {
    #     "django_alias": "postgres_reporting",
    #     "description": "Base de datos de reportes",
    # },

}


def build_databases(env):
    """
    Construye las conexiones Django registradas
    en el catálogo centralizado.
    """

    databases = {}

    for connection_name, configuration in DATABASE_CONNECTIONS.items():

        alias = configuration["django_alias"]

        if alias in databases:
            continue

        if alias == "default":

            databases[alias] = {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": env("DB_NAME"),
                "USER": env("DB_USER"),
                "PASSWORD": env("DB_PASSWORD"),
                "HOST": env("DB_HOST"),
                "PORT": env("DB_PORT"),
                "CONN_MAX_AGE": 60,
            }

        else:
            prefix = alias.upper()

            databases[alias] = {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": env(f"{prefix}_NAME"),
                "USER": env(f"{prefix}_USER"),
                "PASSWORD": env(f"{prefix}_PASSWORD"),
                "HOST": env(f"{prefix}_HOST"),
                "PORT": env(f"{prefix}_PORT"),
                "CONN_MAX_AGE": 60,
            }

    if "default" not in databases:
        raise ValueError(
            "Debe existir una conexión PostgreSQL con alias default."
        )

    return databases
