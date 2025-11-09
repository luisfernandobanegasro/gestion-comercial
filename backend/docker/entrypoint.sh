#!/bin/bash
# ==============================================
# Smart-Sales-365 — entrypoint.sh
# ==============================================
# Este script se ejecuta al iniciar el contenedor
# Hace migraciones, recolecta estáticos y arranca Gunicorn
# ==============================================

set -e  # si algo falla, termina el proceso inmediatamente

echo "🚀 Iniciando contenedor Smart-Sales-365..."
echo "🧾 Entorno actual: ${DJANGO_SETTINGS_MODULE}"

# Esperar un poco a que la base de datos esté lista
echo "⏳ Esperando conexión con la base de datos..."
python <<'PYCODE'
import time, psycopg2, os, sys
from psycopg2 import OperationalError

db_host = os.getenv("PGHOST")
db_name = os.getenv("PGDATABASE")
db_user = os.getenv("PGUSER")
db_pass = os.getenv("PGPASSWORD")
db_port = os.getenv("PGPORT", "5432")

for i in range(10):
    try:
        psycopg2.connect(
            dbname=db_name, user=db_user, password=db_pass,
            host=db_host, port=db_port, connect_timeout=3
        )
        print("✅ Base de datos disponible.")
        sys.exit(0)
    except OperationalError:
        print(f"⏱ Intento {i+1}/10: aún no responde la base de datos...")
        time.sleep(3)
print("❌ Error: la base de datos no está disponible tras 30s.")
sys.exit(1)
PYCODE

# Ejecutar migraciones
echo "📦 Aplicando migraciones..."
python manage.py migrate --noinput || {
  echo "⚠️ Migraciones fallaron. Reintentando en modo seguro..."
  python manage.py migrate --fake-initial
}

# Recolectar archivos estáticos
echo "🧹 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# (Opcional) crear un superusuario automático si es necesario
# echo "👤 Creando superusuario por defecto (si no existe)..."
# python manage.py shell -c "
# from django.contrib.auth import get_user_model;
# User = get_user_model();
# import os;
# if not User.objects.filter(username=os.getenv('DJANGO_SUPERUSER_USERNAME','admin')).exists():
#     User.objects.create_superuser(os.getenv('DJANGO_SUPERUSER_USERNAME','admin'),
#                                   os.getenv('DJANGO_SUPERUSER_EMAIL','admin@example.com'),
#                                   os.getenv('DJANGO_SUPERUSER_PASSWORD','admin123'))
# "

# Iniciar Gunicorn (servidor de aplicación WSGI)
echo "🔥 Iniciando Gunicorn..."
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

