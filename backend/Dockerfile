# backend/Dockerfile
FROM python:3.12-slim

# ---- ENV básicos ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=core.settings

# ---- Paquetes del sistema ----
# - libpq-dev: psycopg2
# - libjpeg/zlib: Pillow
# - curl: HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    libpq-dev \
    libjpeg62-turbo-dev zlib1g-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# ---- Usuario no root y directorio ----
WORKDIR /app
RUN useradd -ms /bin/bash appuser

# ---- Dependencias Python ----
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# ---- Código de la app ----
COPY . /app
RUN chown -R appuser:appuser /app

# ---- Collectstatic (en build) ----
# Asegúrate de tener STATIC_ROOT configurado en settings.py
RUN python manage.py collectstatic --noinput

# ---- Entrypoint ----
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser
EXPOSE 8000

# Healthcheck (ajusta /health/ si usas otro path)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 \
  CMD curl -f http://localhost:8000/health/ || exit 1

ENTRYPOINT ["/entrypoint.sh"]

# Gunicorn: logs a stdout/err para EB
CMD ["gunicorn", "core.wsgi:application", "-b", "0.0.0.0:8000", \
     "--workers", "3", "--threads", "2", "--timeout", "60", \
     "--access-logfile", "-", "--error-logfile", "-"]
