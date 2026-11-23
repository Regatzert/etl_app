import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =========================================================
# ENVIRONMENT
# =========================================================

env = environ.Env(
    DEBUG=(bool, False)
)

environ.Env.read_env(BASE_DIR / ".env")


# =========================================================
# CONFIGURACIONES PRINCIPALES
# =========================================================

SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1"]
)


# =========================================================
# BASE DE DATOS
# =========================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
        "CONN_MAX_AGE": 60,
    }
}


# =========================================================
# ZONA HORARIA
# =========================================================

LANGUAGE_CODE = "es"

TIME_ZONE = "America/Lima"

USE_I18N = True

USE_TZ = True


# =========================================================
# ARCHIVOS ESTÁTICOS
# =========================================================

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# =========================================================
# APLICACIONES
# =========================================================

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "drf_spectacular",

    # Local applications
    "etl_app.apps.etl.apps.ETLConfig",
    "etl_app.apps.data.apps.DataConfig",
    "etl_app.apps.users.apps.UsersConfig",
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================================================
# TEMPLATES
# =========================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =========================================================
# URL CONFIGURATION
# =========================================================

ROOT_URLCONF = "etl_app.config.urls"


# =========================================================
# WSGI / ASGI
# =========================================================

WSGI_APPLICATION = "etl_app.config.wsgi.application"

ASGI_APPLICATION = "etl_app.config.asgi.application"


# =========================================================
# DJANGO REST FRAMEWORK
# =========================================================

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": (
        "drf_spectacular.openapi.AutoSchema"
    ),

    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),

    "PAGE_SIZE": 50,
}


# =========================================================
# SWAGGER / OPENAPI
# =========================================================

SPECTACULAR_SETTINGS = {
    "TITLE": "ETL Platform API",
    "DESCRIPTION": (
        "API para extracción, transformación y carga "
        "de datos desde diferentes fuentes."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


# =========================================================
# DEFAULT PRIMARY KEY
# =========================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"