# backend/Dockerfile
FROM python:3.12-slim

# -------- runtime envs básicos --------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# -------- deps del sistema --------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    libpq-dev \
    libjpeg62-turbo-dev zlib1g-dev \
  && rm -rf /var/lib/apt/lists/*

# -------- app dir --------
WORKDIR /app

# -------- dependencias de Python --------
# (aprovecha cache de capas si solo cambian fuentes)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# -------- código de la app --------
# (tu workflow construye con contexto ./backend)
COPY . /app

# Tu proyecto real es "core"
ENV DJANGO_SETTINGS_MODULE=core.settings

# -------- assets estáticos del admin --------
# Los genera en /app/static (usa STATIC_ROOT en settings.py)
RUN python manage.py collectstatic --noinput

# -------- usuario no-root --------
RUN useradd -ms /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

# -------- puerto y arranque --------
EXPOSE 8000

# Script de entrada: migra y arranca gunicorn
COPY docker/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# WSGI: core.wsgi
CMD ["gunicorn", "core.wsgi:application", "-b", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "--timeout", "60"]
