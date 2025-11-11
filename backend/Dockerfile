# ---- Base ----
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=America/La_Paz

# Dependencias nativas para psycopg2, Pillow y cliente de Postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala requirements primero (cache de capas)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copia el proyecto completo
COPY . /app

# ENTRYPOINT: está en backend/docker/entrypoint.sh dentro del repo
# (el path es relativo al contexto de build)
COPY docker/entrypoint.sh /app/entrypoint.sh
# Normaliza CRLF->LF y marca como ejecutable
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
# Ajusta "core.wsgi" si tu módulo WSGI es otro (p.ej: config.wsgi)
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
