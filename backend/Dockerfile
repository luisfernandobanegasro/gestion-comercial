# backend/Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    libpq-dev \
    libjpeg62-turbo-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Tu workflow construye con contexto ./backend, así que este archivo existe:
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# Copia TODO lo que hay dentro de ./backend (manage.py, core/, apps, etc.)
COPY . /app

# 👉 Tu proyecto real es "core"
ENV DJANGO_SETTINGS_MODULE=core.settings

EXPOSE 8000
# 👉 y tu WSGI también es "core.wsgi"
CMD ["gunicorn", "core.wsgi:application", "-b", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "--timeout", "60"]
