# backend/Dockerfile
FROM python:3.12-slim

# ---- ENV básicos ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=core.settings

# ---- Paquetes del sistema ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev \
    libjpeg62-turbo-dev zlib1g-dev \
    curl dos2unix \
 && rm -rf /var/lib/apt/lists/*

# ---- Usuario y directorio ----
WORKDIR /app
RUN useradd -ms /bin/bash appuser

# ---- Dependencias Python ----
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# ---- Código de la app ----
COPY . /app
RUN chown -R appuser:appuser /app

# ---- Entrypoint ----
COPY docker/entrypoint.sh /app/docker/entrypoint.sh
RUN dos2unix /app/docker/entrypoint.sh || true \
 && chmod +x /app/docker/entrypoint.sh

# ---- NO collectstatic en build (se hace en entrypoint) ----
# RUN python manage.py collectstatic --noinput   # (intencionalmente desactivado)

USER appuser
EXPOSE 8000

# ---- Healthcheck al endpoint de salud real ----
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 \
  CMD curl -fsS http://localhost:8000/api/health/ || exit 1

# ---- Entrypoint + Gunicorn (CMD) ----
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
