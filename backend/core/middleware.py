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

def _clean_payload(payload):
    """Elimina campos sensibles de un payload antes de guardarlo."""
    if not isinstance(payload, dict):
        return payload
    sensitive_keys = ['password', 'token', 'access_token', 'refresh_token', 'new_password']
    return {k: "[REDACTED]" if k in sensitive_keys else v for k, v in payload.items()}

class AuditoriaMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        try:
            user = getattr(request, "user", None)

            # Capturamos request body solo para métodos que mutan
            payload = None
            if request.method in ("POST", "PUT", "PATCH", "DELETE"):
                try:
                    if request.body:
                        payload = _clean_payload(json.loads(request.body.decode("utf-8")))
                except Exception:
                    payload = None  # nunca romper por payload malformado

            # Módulo/acción a partir de la ruta resuelta
            modulo = "web"
            accion = "request"
            resolver_match = getattr(request, "resolver_match", None)
            if resolver_match:
                # Módulo a partir del namespace de la URL
                if resolver_match.namespace:
                    modulo = resolver_match.namespace
                
                # Acción más descriptiva a partir de la vista
                view = getattr(resolver_match.func, 'view_class', None)
                if view:
                    action_map = {
                        'list': 'Listar', 'create': 'Crear',
                        'retrieve': 'Ver Detalle', 'update': 'Actualizar',
                        'partial_update': 'Actualizar Parcialmente', 'destroy': 'Eliminar'
                    }
                    view_action = getattr(view, 'action', 'request')
                    action_name = action_map.get(view_action, view_action.replace('_', ' ').title())
                    model_name = getattr(view.queryset.model, '_meta', {}).verbose_name or 'Recurso'
                    accion = f"{action_name} {model_name}"

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
