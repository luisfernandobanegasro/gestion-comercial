# analitica/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions

# Predicciones de ventas
from ia.train_predictions import generate_predictions

# Interpretación de comandos de voz
from ia.voice_intent import parse_voice_command


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def sales_predictions_view(request):
    days = int(request.query_params.get("days", 30))
    data = generate_predictions(days_to_predict=days)
    return Response(data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def voice_intent_view(request):
    """
    Recibe texto de voz y devuelve la intención detectada.

    body JSON:
    {
        "text": "agrega dos auriculares bt al carrito"
    }

    respuesta:
    {
        "raw": "...",
        "action": "add",
        "quantity": 2,
        "product_name": "auriculares bt"
    }
    """
    text = request.data.get("text", "") or ""
    intent = parse_voice_command(text)

    return Response(
        {
            "raw": intent.raw,
            "action": intent.action,
            "quantity": intent.quantity,
            "product_name": intent.product_name,
        }
    )
