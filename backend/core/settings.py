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
load_dotenv(BASE_DIR / ".env")

FRONTEND_DIR = BASE_DIR.parent / "frontend"

# ================================
# Configuración básica
# ================================
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = os.getenv("DEBUG", "1") == "1"

_env_hosts = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if h.strip()
]

ALLOWED_HOSTS = list(
    set(
        _env_hosts
        + [
            "127.0.0.1",
            "localhost",
            "0.0.0.0",
            ".elasticbeanstalk.com",
            ".compute.amazonaws.com",
        ]
    )
)

# Para ALB/ELB
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# SIN HTTPS obligatoria en EB
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# ================================
# Apps instaladas
# ================================
INSTALLED_APPS = [
    "cuentas",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",

    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",

    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "corsheaders",

    "auditoria",
    "catalogo",
    "clientes",
    "ventas",
    "pagos",
    "reportes",
    "configuracion",
    "analitica",
    "ia",

    "storages",  # S3
]

# ================================
# Middleware
# ================================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "core.middleware.AuditoriaMiddleware",
]

ROOT_URLCONF = "core.urls"

# ================================
# Templates
# ================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
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
# Base de datos
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
# Autenticación / JWT / DRF
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
# Static y Media
# ================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

# ======== S3 para Media =========
USE_S3_MEDIA = os.getenv("USE_S3_MEDIA", "0" if DEBUG else "1") == "1"

if USE_S3_MEDIA:

    AWS_STORAGE_BUCKET_NAME = os.getenv(
        "AWS_STORAGE_BUCKET_NAME",
        "frontend-product-ef",        # 👈 TU BUCKET REAL
    )

    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")

    AWS_S3_CUSTOM_DOMAIN = os.getenv(
        "AWS_S3_CUSTOM_DOMAIN",
        "d1098mxiq3rtlj.cloudfront.net",  # 👈 TU CLOUDFRONT REAL
    )

    AWS_MEDIA_LOCATION = os.getenv("AWS_MEDIA_LOCATION", "media")

    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_MEDIA_LOCATION}/"
    MEDIA_ROOT = None

else:
    MEDIA_ROOT = BASE_DIR / "media"
    MEDIA_URL = "/media/"

# ================================
# Backend domain
# ================================
BACKEND_DOMAIN = os.getenv(
    "BACKEND_DOMAIN",
    "smart-sales-365-env.eba-n3j3inxe.us-east-1.elasticbeanstalk.com",
).strip()

# ================================
# CORS / CSRF
# ================================
DEFAULT_FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

EXTRA_FRONTEND = [
    o.strip()
    for o in os.getenv("FRONTEND_ORIGINS", "").split(",")
    if o.strip()
]

CORS_ALLOW_ALL_ORIGINS = True if DEBUG else False
CORS_ALLOWED_ORIGINS = [] if CORS_ALLOW_ALL_ORIGINS else (
    DEFAULT_FRONTEND_ORIGINS + EXTRA_FRONTEND
)
CORS_ALLOW_CREDENTIALS = True

# ================================
# CSRF trusted origins
# ================================
_csrf_from_cors = []
for o in (CORS_ALLOWED_ORIGINS or []):
    if o.startswith("http"):
        _csrf_from_cors.append(o)
    else:
        _csrf_from_cors.extend([f"http://{o}", f"https://{o}"])

_csrf_from_hosts = []
for h in _env_hosts:
    if not h:
        continue
    if h.startswith("http"):
        _csrf_from_hosts.append(h)
    else:
        _csrf_from_hosts.extend([f"http://{h}", f"https://{h}"])

CSRF_TRUSTED_ORIGINS = list(set(_csrf_from_cors + _csrf_from_hosts))

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
