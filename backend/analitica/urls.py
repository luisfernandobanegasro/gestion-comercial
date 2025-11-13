# analitica/urls.py

from django.urls import path
from .views import sales_predictions_view, voice_intent_view

urlpatterns = [
    path("predicciones/ventas/", sales_predictions_view, name="sales_predictions"),
    path("voz/intencion/", voice_intent_view, name="voice_intent"),
]
