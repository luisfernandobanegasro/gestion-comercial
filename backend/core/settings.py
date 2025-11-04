# core/settings.py
from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

# ================================
# BASE DIR + .env
# ================================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Monorepo (backend/, frontend/)
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# ================================
# CONFIG BÁSICA
# ================================
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = os.getenv("DEBUG", "1") == "1"

# Hosts válidos (prod desde env)
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]

# Detrás de ELB/Proxy para que Django detecte HTTPS correctamente
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Cookies más seguras cuando no estamos en debug
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# ================================
# APPS
# ================================
INSTALLED_APPS = [
    # Proyecto (la app de cuentas primero)
    "cuentas",

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # 3rd party
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "corsheaders",  # pip install django-cors-headers

    # Apps del dominio
    "auditoria",
    "catalogo",
    "clientes",
    "ventas",
    "pagos",
    "reportes",
    "configuracion",
    "analitica",
    "ia",
]

# ================================
# MIDDLEWARE
# ================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",

    # CORS SIEMPRE antes de CommonMiddleware
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # Auditoría propia
    "core.middleware.AuditoriaMiddleware",
]

ROOT_URLCONF = "core.urls"

# ================================
# TEMPLATES
# ================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # Ej: [FRONTEND_DIR / "dist"] si sirves build de Vite desde Django
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

WSGI_APPLICATION = "core.wsgi.application"

# ================================
# DATABASE (PostgreSQL)
# ================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("PGDATABASE", "gestion_comercial"),
        "USER": os.getenv("PGUSER", "postgres"),
        "PASSWORD": os.getenv("PGPASSWORD", ""),
        "HOST": os.getenv("PGHOST", "127.0.0.1"),
        "PORT": os.getenv("PGPORT", "5432"),
    }
}

# ================================
# AUTH
# ================================
AUTH_USER_MODEL = "cuentas.Usuario"

# ================================
# DRF + JWT + OpenAPI
# ================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "SmartSales365 API",
    "DESCRIPTION": "API del Sistema de Gestión Comercial con Django + PostgreSQL",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SECURITY": [{"bearerAuth": []}],
    "COMPONENT_SPLIT_REQUEST": True,
}

# ================================
# PASSWORD VALIDATORS
# ================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ================================
# I18N
# ================================
LANGUAGE_CODE = "es"
TIME_ZONE = os.getenv("TIME_ZONE", "America/La_Paz")
USE_I18N = True
USE_TZ = True

# ================================
# STATIC & MEDIA
# ================================
STATIC_URL = "static/"
MEDIA_URL = "media/"
STATIC_ROOT = BASE_DIR / "static"
MEDIA_ROOT = BASE_DIR / "media"
# STATICFILES_DIRS = [FRONTEND_DIR / "dist"]  # sólo si sirves assets del build

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ================================
# CORS / CSRF
# ================================
# Por defecto en dev todo abierto; en prod, controlado por FRONTEND_ORIGINS
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False

# Permite inyectar orígenes desde ENV (CloudFront/dominio del frontend)
FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "")
if FRONTEND_ORIGINS:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in FRONTEND_ORIGINS.split(",") if o.strip()]

CORS_ALLOW_CREDENTIALS = True  # si vas a usar cookies/sesión

# Confianza CSRF a los mismos orígenes (si usas cookies/CSRf desde frontend)
CSRF_TRUSTED_ORIGINS = list(set(
    [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        # añade dominios de CORS_ALLOWED_ORIGINS con esquema
        *[o if o.startswith("http") else f"https://{o}" for o in (CORS_ALLOWED_ORIGINS or [])],
    ]
))

# ================================
# EMAIL & LOGGING
# ================================
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

# ================================
# STRIPE
# ================================
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
