# backend/Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Paquetes necesarios para psycopg2, Pillow, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    libpq-dev \
    libjpeg62-turbo-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependencias
# Asegúrate de tener backend/requirements.txt en el repo
COPY requirements.txt /tmp/requirements.txt
# Si tus reqs están en backend/requirements.txt usa: COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# Copia el código
COPY . /app
# Si prefieres solo la carpeta del backend: COPY backend/ /app

# Ajusta si tu settings module tiene otro nombre
ENV DJANGO_SETTINGS_MODULE=backend.settings

EXPOSE 8000
# Gunicorn en producción
CMD ["gunicorn", "backend.wsgi:application", "-b", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "--timeout", "60"]
