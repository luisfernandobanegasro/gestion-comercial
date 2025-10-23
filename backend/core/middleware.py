import json
from django.utils.deprecation import MiddlewareMixin
from auditoria.models import RegistroAuditoria

def _get_client_ip(request):
    # Respeta proxies reversos si en algún momento usas uno
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        # toma el primer IP de la cadena
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

class AuditoriaMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        try:
            user = getattr(request, "user", None)

            # Capturamos request body solo para métodos que mutan
            payload = None
            if request.method in ("POST", "PUT", "PATCH", "DELETE"):
                try:
                    if request.body:
                        payload = json.loads(request.body.decode("utf-8"))
                except Exception:
                    payload = None  # nunca romper por payload malformado

            # Módulo/acción a partir de la ruta resuelta
            modulo = "web"
            accion = "request"
            try:
                if request.path.startswith("/api/"):
                    partes = request.path.split("/")
                    if len(partes) > 2 and partes[2]:
                        modulo = partes[2]
                if getattr(request, "resolver_match", None):
                    # url_name o view_name de la ruta
                    accion = request.resolver_match.url_name or request.resolver_match.view_name or accion
            except Exception:
                pass

            RegistroAuditoria.objects.create(
                usuario=user if getattr(user, "is_authenticated", False) else None,
                accion=str(accion)[:100],
                modulo=str(modulo)[:50],
                ip=_get_client_ip(request),
                user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:255],
                ruta=request.path[:255],
                metodo=request.method[:10],
                estado=getattr(response, "status_code", None),
                payload=payload,
            )
        except Exception:
            # La auditoría jamás debe romper la respuesta
            pass

        return response
