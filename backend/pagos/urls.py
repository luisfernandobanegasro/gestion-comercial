from django.urls import path
from .views import CrearIntentoPagoView, ConfirmarPagoStripeView, ReembolsoTotalView

urlpatterns = [
    path("stripe/intent/", CrearIntentoPagoView.as_view(), name="stripe-intent"),
    path("stripe/confirmar/", ConfirmarPagoStripeView.as_view(), name="stripe-confirmar"),
    path("stripe/reembolsar/", ReembolsoTotalView.as_view(), name="stripe-reembolsar"),
]
