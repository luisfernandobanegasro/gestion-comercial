# reportes/logger.py
from typing import Optional, Tuple, Dict, Any
from .models import PromptLog


def log_prompt(
    user,
    prompt: str,
    predicted: Optional[Tuple[str, float]],
    resolved_intent: str,
    spec_dict: Dict[str, Any],
) -> None:
    """
    Registra un uso del módulo de reportes.

    - user: request.user (puede ser anónimo o None)
    - prompt: texto original que escribió/dijo el usuario
    - predicted: (label, prob) o None si no hubo modelo IA
    - resolved_intent: la intención final que realmente ejecutamos
    - spec_dict: spec completa que se usó para generar el queryset
    """
    label, prob = (None, None)
    if predicted:
        label, prob = predicted

    PromptLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        prompt_text=prompt,
        predicted_intent=label,
        confidence=prob,
        resolved_intent=resolved_intent or "",
        spec_json=spec_dict or {},
    )
