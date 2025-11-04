#!/usr/bin/env bash
set -e

# Mostrar settings activos (útil para logs)
echo "DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}"

# Migraciones (la DB debe estar accesible por variables PG*)
python manage.py migrate --noinput

# Puedes seedear data inicial si lo necesitas (opcional)
# python manage.py loaddata initial_data.json || true

# Ejecuta el CMD del contenedor (gunicorn)
exec "$@"
