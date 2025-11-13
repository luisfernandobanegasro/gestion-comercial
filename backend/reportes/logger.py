# reportes/logger.py
from .models import PromptLog

def log_prompt(user, prompt: str, predicted: tuple | None, resolved_intent: str, spec_dict: dict):
    """
    predicted: (label, prob) o None si no hubo modelo
    """
    label, prob = (None, None)
    if predicted:
        label, prob = predicted
    PromptLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        prompt_text=prompt,
        predicted_intent=label,
        confidence=prob,
        resolved_intent=resolved_intent,
        spec_json=spec_dict,
    )
