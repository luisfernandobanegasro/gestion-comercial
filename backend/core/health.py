# core/health.py
from django.http import JsonResponse
from django.db import connection
from django.db.utils import OperationalError

def health_check(request):
    """
    Devuelve 200 OK si el servidor Django y la base de datos están accesibles.
    Usado por Elastic Beanstalk para verificar el estado del contenedor.
    """
    health = {"status": "ok", "database": False}

    try:
        connection.ensure_connection()
        health["database"] = True
    except OperationalError:
        health["database"] = False

    status = 200 if health["database"] else 500
    return JsonResponse(health, status=status)
