from django.urls import path
from .views import ReportePromptView, dashboard_data_view

urlpatterns = [
    path("prompt/", ReportePromptView.as_view(), name="reporte_prompt"),
    path("dashboard/", dashboard_data_view, name="dashboard_data"),
]
