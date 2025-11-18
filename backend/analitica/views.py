# analitica/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status

from analitica.services import (
    generate_sales_predictions,
    get_daily_sales_series,
    _resolve_period_days,
)

# Interpretación de comandos de voz
from ia.voice_intent import parse_voice_command, find_best_product


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def sales_predictions_view(request):
    """
    GET /analitica/predicciones/ventas/

    Query params:
      - period: 7d | 30d | 365d (default 30d)
      - days:   override de cantidad de días a predecir
      - product_id: filtrar por producto
      - category_id: filtrar por categoría
    """
    period = request.query_params.get("period", "30d")
    days_param = request.query_params.get("days")
    product_id_param = request.query_params.get("product_id")
    category_id_param = request.query_params.get("category_id")

    try:
        days_override = int(days_param) if days_param is not None else None
    except (TypeError, ValueError):
        days_override = None

    try:
        product_id = int(product_id_param) if product_id_param else None
    except (TypeError, ValueError):
        product_id = None

    try:
        category_id = int(category_id_param) if category_id_param else None
    except (TypeError, ValueError):
        category_id = None

    # Predicciones (ya respetan filtros)
    preds = generate_sales_predictions(
        period=period,
        days_override=days_override,
        product_id=product_id,
        category_id=category_id,
    )

    # Histórico para el mismo período (para las barras)
    period_days = days_override or _resolve_period_days(period)
    historico = get_daily_sales_series(
        days_back=period_days,
        product_id=product_id,
        category_id=category_id,
    )

    return Response(
        {
            "period": period,
            "product_id": product_id,
            "category_id": category_id,
            "historico": historico,
            "predicciones": preds,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def voice_intent_view(request):
    """
    Recibe texto de voz y devuelve la intención detectada y,
    si es posible, el producto correspondiente.

    body JSON:
    {
        "text": "agrega dos auriculares bt al carrito"
    }

    respuesta:
    {
        "raw": "...",
        "action": "add",
        "quantity": 2,
        "product_name": "auriculares bt",
        "product": {
            "id": 5,
            "nombre": "Auriculares BT",
            "precio": "40.00",
            "stock": 56
        }
    }
    """
    text = request.data.get("text", "") or ""
    intent = parse_voice_command(text)

    response_data = {
        "raw": intent.raw,
        "action": intent.action,
        "quantity": intent.quantity,
        "product_name": intent.product_name,
        "product": None,
    }

    if intent.action in ("add", "remove") and intent.product_name:
        product = find_best_product(intent.product_name)
        if product:
            response_data["product"] = {
                "id": product.id,
                "nombre": product.nombre,
                "precio": str(product.precio),
                "stock": product.stock,
            }

    return Response(response_data, status=status.HTTP_200_OK)
