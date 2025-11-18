# reportes/models.py
from django.db import models
from django.conf import settings


class PromptLog(models.Model):
    """
    Log de prompts usados en el módulo de reportes.

    - predicted_intent / confidence: salida opcional del modelo IA (si existe).
    - resolved_intent: intención final que realmente se ejecutó.
    - spec_json: spec completa que se usó para construir el queryset.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="prompt_logs",
    )
    prompt_text = models.TextField()
    predicted_intent = models.CharField(max_length=50, null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    resolved_intent = models.CharField(max_length=50)  # intención final
    spec_json = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # opcional: etiqueta humana (después de revisión manual)
    human_label = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["predicted_intent"]),
            models.Index(fields=["resolved_intent"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {self.prompt_text[:60]}"
