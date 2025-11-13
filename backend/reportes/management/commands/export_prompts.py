# reportes/management/commands/export_prompts.py
from django.core.management.base import BaseCommand
from reportes.models import PromptLog
import csv, os
from django.conf import settings

class Command(BaseCommand):
    help = "Exporta prompts con baja confianza (o sin predicción) para rotular."

    def add_arguments(self, parser):
        parser.add_argument("--min_prob", type=float, default=0.55, help="Umbral de confianza máximo para exportar")
        parser.add_argument("--limit", type=int, default=200, help="Máximo de filas a exportar")

    def handle(self, *args, **opts):
        qs = PromptLog.objects.order_by("-created_at")
        qs = qs.filter(confidence__isnull=True) | qs.filter(confidence__lte=opts["min_prob"])
        qs = qs.order_by("-created_at")[:opts["limit"]]

        out_dir = os.path.join(settings.BASE_DIR, "ia")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "to_label.csv")

        with open(out_path, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            # columnas: texto, etiqueta_sugerida, confianza, etiqueta_humana (vacía)
            w.writerow(["texto", "predicha", "confianza", "etiqueta_humana"])
            for p in qs:
                w.writerow([p.prompt_text, p.predicted_intent or "", p.confidence or "", ""])

        self.stdout.write(self.style.SUCCESS(f"Exportado a {out_path}. Rellena 'etiqueta_humana' y agrega filas a ia/training_data.csv"))
