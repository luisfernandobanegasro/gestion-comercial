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
except Exception:
    print("❌ Falta psycopg2. Asegúrate de tener 'psycopg2-binary' o 'psycopg2' en requirements.txt.")
    sys.exit(1)

db_url = os.environ.get("DATABASE_URL")
params = {}

if db_url:
    # Soporta postgres:// o postgresql://
    p = urlparse(db_url)
    params = dict(
        dbname=(p.path or "").lstrip("/") or os.environ.get("PGDATABASE"),
        user=p.username or os.environ.get("PGUSER"),
        password=p.password or os.environ.get("PGPASSWORD"),
        host=p.hostname or os.environ.get("PGHOST"),
        port=p.port or os.environ.get("PGPORT") or 5432,
    )
else:
    # Modo PG* (sin DATABASE_URL)
    params = dict(
        dbname=os.environ.get("PGDATABASE"),
        user=os.environ.get("PGUSER"),
        password=os.environ.get("PGPASSWORD"),
        host=os.environ.get("PGHOST"),
        port=int(os.environ.get("PGPORT", "5432")),
    )

# Opcional: SSL
sslmode = os.environ.get("DB_SSLMODE") or os.environ.get("PGSSLMODE")
if sslmode:
    params["sslmode"] = sslmode

missing = [k for k,v in params.items() if v in (None,"")]
if missing:
    print(f"❌ Variables faltantes para conectar a Postgres: {missing}.")
    print("   Define PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD (o usa DATABASE_URL).")
    sys.exit(1)

for i in range(30):
    try:
        conn = psycopg2.connect(connect_timeout=3, **params)
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
