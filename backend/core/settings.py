# ================================================
# core/settings.py — Configuración principal Django
# ================================================
from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

# ================================
# BASE DIR + .env
# ================================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")  # Carga variables desde backend/.env

# Monorepo (backend/, frontend/)
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# ================================
# CONFIGURACIÓN BÁSICA
# ================================
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = os.getenv("DEBUG", "1") == "1"

# Hosts permitidos (importante para despliegue)
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()
]

# Si hay proxy o load balancer (Elastic Beanstalk/ALB)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Cookies seguras cuando no estamos en DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# ================================
# APLICACIONES INSTALADAS
# ================================
INSTALLED_APPS = [
    # Apps del proyecto (cuentas primero para AUTH_USER_MODEL)
    "cuentas",

    # Django apps por defecto
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Terceros
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "corsheaders",  # pip install django-cors-headers

    # Módulos del dominio
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

    # CORS siempre antes de CommonMiddleware
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # Middleware personalizado (auditoría)
    "core.middleware.AuditoriaMiddleware",
]

ROOT_URLCONF = "core.urls"

# ================================
# TEMPLATES
# ================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Si decides servir el build de Vite desde Django
        "DIRS": [],  # Ejemplo: [FRONTEND_DIR / "dist"]
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
# BASE DE DATOS (PostgreSQL)
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
# AUTENTICACIÓN
# ================================
AUTH_USER_MODEL = "cuentas.Usuario"

# ================================
# DJANGO REST FRAMEWORK + JWT + OpenAPI
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
# VALIDADORES DE CONTRASEÑA
# ================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ================================
# INTERNACIONALIZACIÓN
# ================================
LANGUAGE_CODE = "es"
TIME_ZONE = os.getenv("TIME_ZONE", "America/La_Paz")
USE_I18N = True
USE_TZ = True

# ================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ================================
STATIC_URL = "static/"
MEDIA_URL = "media/"
STATIC_ROOT = BASE_DIR / "static"
MEDIA_ROOT = BASE_DIR / "media"
# STATICFILES_DIRS = [FRONTEND_DIR / "dist"]  # si sirves build de Vite

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ================================
# CORS / CSRF (para frontend remoto)
# ================================
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False

# Permite inyectar orígenes del frontend (desde .env o CloudFront)
FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "")
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
if FRONTEND_ORIGINS:
    CORS_ALLOWED_ORIGINS += [o.strip() for o in FRONTEND_ORIGINS.split(",") if o.strip()]

CORS_ALLOW_CREDENTIALS = True  # si usas cookies o sesión en frontend

# Construimos dinámicamente CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = list(set([
    *[o if o.startswith("http") else f"https://{o}" for o in (CORS_ALLOWED_ORIGINS or [])],
    *[f"https://{h.strip()}" for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()],
]))

# ================================
# EMAIL Y LOGGING
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
