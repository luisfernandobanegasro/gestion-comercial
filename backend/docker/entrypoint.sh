#!/usr/bin/env bash
set -e

# Pequeña espera opcional si la DB tarda en estar lista (RDS)
if [ -n "$PGHOST" ]; then
  echo "Esperando a la base de datos $PGHOST:$PGPORT ..."
  for i in {1..30}; do
    python - <<'PY'
import os, socket, sys
host=os.getenv("PGHOST","127.0.0.1"); port=int(os.getenv("PGPORT","5432"))
s=socket.socket(); s.settimeout(1)
try:
    s.connect((host, port)); print("DB OK")
except Exception as e:
    print("DB no disponible:", e); sys.exit(1)
PY
    if [ $? -eq 0 ]; then break; fi
    sleep 1
  done || true
fi

echo "Aplicando migraciones..."
python manage.py migrate --noinput

# Repetimos por seguridad (idempotente)
echo "Colectando estáticos..."
python manage.py collectstatic --noinput

echo "Arrancando: $*"
exec "$@"
