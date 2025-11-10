#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Iniciando contenedor Smart-Sales-365..."
echo "🧾 DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-<no-set>}"
echo "🕰️ TZ=${TZ:-<no-set>}"

# ---------- Espera a la base de datos ----------
python - <<'PY'
import os, time, sys
from urllib.parse import urlparse

try:
    import psycopg2
except Exception as e:
    print("❌ Falta psycopg2 en el entorno. Asegúrate de tener 'psycopg2-binary' o 'psycopg2' en requirements.txt.")
    sys.exit(1)

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL no definido en variables de entorno."); sys.exit(1)

p = urlparse(DATABASE_URL)
for i in range(30):
    try:
        conn = psycopg2.connect(
            dbname=p.path.lstrip('/'),
            user=p.username, password=p.password,
            host=p.hostname, port=p.port or 5432,
            connect_timeout=3,
        )
        conn.close()
        print("✅ Base de datos disponible.")
        break
    except Exception as e:
        print(f"⏳ Intento {i+1}/30 esperando DB: {e}")
        time.sleep(2)
else:
    print("❌ No se pudo conectar a la DB a tiempo."); sys.exit(1)
PY

# ---------- Migraciones y static ----------
echo "📦 Aplicando migraciones..."
python manage.py migrate --noinput

echo "🧹 Collectstatic (si corresponde)…"
python manage.py collectstatic --noinput || true

# ---------- Arranque del proceso principal ----------
echo "🔥 Lanzando proceso: $*"
exec "$@"
