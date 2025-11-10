# ---- Base ----
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Dependencias nativas para psycopg2, Pillow, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala requirements primero (cache de capas)
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copia el proyecto
COPY . /app

# Zona horaria (ajústala si quieres)
ENV TZ=America/La_Paz

# Puerto interno (gunicorn escuha aquí)
EXPOSE 8000

# ENTRYPOINT hace: wait DB + migrate + collectstatic, luego "exec CMD"
COPY entrypoint.sh /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

# Proceso principal (gunicorn). Ajusta el módulo WSGI si tu paquete no es "core".
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
