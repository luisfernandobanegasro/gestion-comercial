# reportes/management/commands/train_models.py
from django.core.management.base import BaseCommand
import ia.train_intents as ti
try:
    import ia.train_predictions as tp
    HAS_PRED = True
except Exception:
    HAS_PRED = False

class Command(BaseCommand):
    help = "Reentrena IA de intenciones y, si existe, el modelo de predicciones."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Entrenando modelo de intenciones..."))
        res = ti.train_model()
        self.stdout.write(self.style.SUCCESS(f"✔ CV Acc: {res.cv_accuracy:.3f}"))  # indicador estable

        if HAS_PRED:
            self.stdout.write(self.style.MIGRATE_HEADING("Entrenando modelo de predicciones..."))
            try:
                tp.train_model()
                self.stdout.write(self.style.SUCCESS("✔ Predicciones: OK"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Predicciones: {e}"))
