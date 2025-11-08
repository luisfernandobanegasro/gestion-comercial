#!/usr/bin/env bash
set -e

# Opcional: espera a que la DB responda (si usas Postgres en RDS)
# python - <<'PY'
# import os, time, psycopg2
# from urllib.parse import urlparse
# url = os.getenv("DATABASE_URL", "")
# if url:
#     for _ in range(30):
#         try:
#             psycopg2.connect(url).close()
#             break
#         except Exception:
#             time.sleep(1)
# PY

# Migraciones automáticas
python manage.py migrate --noinput

# Puedes cargar fixtures iniciales si quieres (comenta si no aplica)
# python manage.py loaddata initial_data.json || true

# Ejecuta el comando que venga del CMD del Dockerfile
exec "$@"
