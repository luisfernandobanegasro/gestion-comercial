# ================================================
# core/settings.py — Configuración principal Django
# ================================================
from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

# ================================
# Paths base y .env
# ================================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")  # lee backend/.env si existe

# Si trabajas monorepo (backend/, frontend/)
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# ================================
# Configuración básica
# ================================
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = os.getenv("DEBUG", "1") == "1"

# Hosts permitidos
_env_hosts = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if h.strip()
]
ALLOWED_HOSTS = list(set(_env_hosts + ["127.0.0.1", "localhost"]))
# Permitir host interno de EB y health checks
ALLOWED_HOSTS += ["0.0.0.0", ".elasticbeanstalk.com", ".compute.amazonaws.com"]

# Detrás de ALB/ELB (X-Forwarded-Proto/Host)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Redirección a HTTPS (déjalo activado solo si tu ALB ya tiene TLS)
SECURE_SSL_REDIRECT = os.getenv("FORCE_HTTPS", "0") == "1"

# Cookies endurecidas en producción
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# ================================
# Apps instaladas
# ================================
INSTALLED_APPS = [
    # Apps del proyecto (cuentas primero por AUTH_USER_MODEL)
    "cuentas",

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Terceros
    "whitenoise.runserver_nostatic",  # sirve estáticos en dev/prod
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "corsheaders",

    # Dominios
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
# Middleware
# ================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise justo después de SecurityMiddleware
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    # CORS SIEMPRE antes de CommonMiddleware
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # Middleware propio
    "core.middleware.AuditoriaMiddleware",
]

ROOT_URLCONF = "core.urls"

# ================================
# Templates
# ================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Si algún día sirves el build de Vite desde Django:
        # "DIRS": [FRONTEND_DIR / "dist"],
        "DIRS": [],
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
# Base de datos (PostgreSQL)
# ================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("PGDATABASE", "gestion_comercial"),
        "USER": os.getenv("PGUSER", "postgres"),
        "PASSWORD": os.getenv("PGPASSWORD", ""),
        "HOST": os.getenv("PGHOST", "127.0.0.1"),
        "PORT": os.getenv("PGPORT", "5432"),
        # Para RDS con SSL:
        # "OPTIONS": {"sslmode": os.getenv("DB_SSLMODE", "prefer")},
    }
}

# ================================
# Autenticación / DRF / JWT / OpenAPI
# ================================
AUTH_USER_MODEL = "cuentas.Usuario"

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
# Validadores de contraseña
# ================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ================================
# I18N / TZ
# ================================
LANGUAGE_CODE = "es"
TIME_ZONE = os.getenv("TIME_ZONE", "America/La_Paz")
USE_I18N = True
USE_TZ = True

# ================================
# Static & Media (WhiteNoise)
# ================================
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

STATIC_ROOT = BASE_DIR / "static"   # destino de collectstatic
MEDIA_ROOT = BASE_DIR / "media"

# WhiteNoise: compresión + hash de archivos
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Si quisieras incluir assets del front en dev/CI:
# STATICFILES_DIRS = [FRONTEND_DIR / "dist"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ================================
# CORS / CSRF
# ================================
# Orígenes locales por defecto (Vite)
DEFAULT_FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Orígenes adicionales desde env (ej. CloudFront)
EXTRA_FRONTEND = [
    o.strip()
    for o in os.getenv("FRONTEND_ORIGINS", "").split(",")
    if o.strip()
]

CORS_ALLOW_ALL_ORIGINS = True if DEBUG else False
CORS_ALLOWED_ORIGINS = [] if CORS_ALLOW_ALL_ORIGINS else (DEFAULT_FRONTEND_ORIGINS + EXTRA_FRONTEND)
CORS_ALLOW_CREDENTIALS = True  # si usas cookies/sesión

# CSRF confía en tus orígenes + hosts (requiere esquema)
_csrf_from_cors = [
    o if o.startswith("http") else f"https://{o}" for o in (CORS_ALLOWED_ORIGINS or [])
]
_csrf_from_hosts = [
    f"https://{h}" for h in _env_hosts if h and not h.startswith("http")
]
CSRF_TRUSTED_ORIGINS = list(
    set(
        _csrf_from_cors
        + _csrf_from_hosts
        + ["https://*.elasticbeanstalk.com"]
    )
)

# ================================
# Email y Logging
# ================================
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

# ================================
# Stripe
# ================================
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
