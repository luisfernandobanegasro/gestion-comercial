# backend/Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# -------- deps del sistema --------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    libpq-dev \
    libjpeg62-turbo-dev zlib1g-dev \
  && rm -rf /var/lib/apt/lists/*

# -------- dir de la app --------
WORKDIR /app

# -------- dependencias de Python --------
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# -------- código --------
COPY . /app

# Proyecto Django
ENV DJANGO_SETTINGS_MODULE=core.settings

# -------- WhiteNoise: assets estáticos --------
# (usa STATIC_ROOT de settings.py -> /app/static)
RUN python manage.py collectstatic --noinput

# -------- entrypoint (como root para poder chmod) --------
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# -------- usuario no root --------
RUN useradd -ms /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

# Logs a stdout/stderr para EB
CMD ["gunicorn", "core.wsgi:application", "-b", "0.0.0.0:8000", \
     "--workers", "3", "--threads", "2", "--timeout", "60", \
     "--access-logfile", "-", "--error-logfile", "-"]
