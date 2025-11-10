#!/usr/bin/env bash
# ==============================================
# Smart-Sales-365 — entrypoint.sh (production)
# ==============================================

set -euo pipefail

echo "🚀 Iniciando contenedor Smart-Sales-365..."
echo "🧾 DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-<no-set>}"
echo "🕒 TZ=${TIME_ZONE:-UTC}"

# --- Espera a que la DB (Postgres) esté lista ---
echo "⏳ Esperando conexión con la base de datos..."
python - <<'PY'
import os, sys, time
import psycopg2
from psycopg2 import OperationalError

host = os.getenv("PGHOST")
name = os.getenv("PGDATABASE")
user = os.getenv("PGUSER")
pwd  = os.getenv("PGPASSWORD")
port = os.getenv("PGPORT", "5432")

if not all([host, name, user, pwd]):
    print("❌ Variables de DB incompletas (PGHOST/PGDATABASE/PGUSER/PGPASSWORD).")
    sys.exit(1)

for i in range(30):  # ~90s
    try:
        psycopg2.connect(dbname=name, user=user, password=pwd, host=host, port=port, connect_timeout=3).close()
        print("✅ Base de datos disponible.")
        sys.exit(0)
    except OperationalError as e:
        print(f"⏱ Intento {i+1}/30: DB aún no responde... ({e.__class__.__name__})")
        time.sleep(3)

print("❌ DB no disponible tras ~90s. Abortando.")
sys.exit(1)
PY

# --- Migraciones ---
echo "📦 Aplicando migraciones..."
python manage.py migrate --noinput

# --- Colecta estáticos (si aplica) ---
echo "🧹 Collectstatic (si corresponde)..."
if python - <<'PY'
import importlib, sys
try:
    importlib.import_module("django.contrib.staticfiles")
    sys.exit(0)
except ModuleNotFoundError:
    sys.exit(1)
PY
then
  python manage.py collectstatic --noinput
else
  echo "ℹ️ 'staticfiles' no está habilitado; se omite collectstatic."
fi

# --- Lanzar Gunicorn ---
echo "🔥 Iniciando Gunicorn en 0.0.0.0:8000..."
exec gunicorn core.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
