# ia/train_intents.py
from __future__ import annotations
import os, joblib, numpy as np
from dataclasses import dataclass
from typing import List, Tuple
from django.conf import settings
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report
from .dataset import get_full_dataset

MODEL_PATH = os.path.join(settings.BASE_DIR, "ia", "prompt_intent_model.joblib")

SPANISH_STOPWORDS = [
    "a","acá","ahí","al","algo","algún","alguna","algunas","alguno","algunos","allá","alli","allí",
    "ante","antes","aquel","aquella","aquellas","aquello","aquellos","aquí","arriba","así","aun","aún",
    "bajo","bastante","bien","cada","casi","como","con","contra","cual","cuales","cualquier","cualquiera",
    "cualquieras","cuan","cuando","cuanta","cuantas","cuanto","cuantos","de","del","demasiado","dentro",
    "desde","donde","dos","el","él","ella","ellas","ello","ellos","en","encima","entonces","entre","era",
    "eran","eres","es","esa","esas","ese","eso","esos","esta","está","están","estaba","estaban","estado",
    "estados","estar","estas","este","esto","estos","estoy","fin","fue","fueron","gran","grandes","ha",
    "haber","había","habían","han","hasta","hay","incluso","la","las","le","les","lo","los","luego","más",
    "me","mi","mientras","mis","misma","mismas","mismo","mismos","mucho","muchos","muy","nada","ni","ningun",
    "ninguna","ningunas","ninguno","ningunos","no","nos","nosotras","nosotros","nuestra","nuestras","nuestro",
    "nuestros","nunca","o","os","otra","otras","otro","otros","para","pero","poca","pocas","poco","pocos",
    "por","porque","primero","puede","pueden","pues","que","qué","quien","quién","quienes","se","sea","sean",
    "según","ser","si","sí","sido","siempre","sin","sino","sobre","sois","sola","solas","solo","sólo","somos",
    "son","soy","su","sus","tal","también","tampoco","tan","tanta","tantas","tanto","te","tenemos","tener",
    "tengo","ti","tiempo","tiene","tienen","toda","todas","todavía","todo","todos","tu","tus","un","una",
    "unas","uno","unos","usted","ustedes","va","vamos","van","varias","varios","veces","ver","y","ya"
]

def _make_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            analyzer="word",
            ngram_range=(1, 2),
            min_df=1,
            stop_words=SPANISH_STOPWORDS,
        )),
        ("clf", LogisticRegression(max_iter=300, class_weight="balanced")),
    ])

@dataclass
class TrainResult:
    model_path: str
    classes: List[str]
    report: str
    cv_accuracy: float

def train_model() -> TrainResult:
    dataset = get_full_dataset()
    texts = [t for t, y in dataset]
    labels = [y for t, y in dataset]

    pipe = _make_pipeline()

    # Validación cruzada (k=5) para un score estable aun con dataset chico
    skf = StratifiedKFold(n_splits=min(5, len(set(labels))), shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipe, texts, labels, cv=skf, scoring="accuracy")
    cv_acc = float(cv_scores.mean())

    # Split final para reporte
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.25, stratify=labels, random_state=42)
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    report = classification_report(y_test, y_pred, digits=2, zero_division=0)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    print("=== Cross-Validation Accuracy (k-fold) ===")
    print(f"CV Accuracy: {cv_acc:.3f}")
    print("=== Test Report ===")
    print(report)
    print(f"✅ Modelo guardado en: {MODEL_PATH}")

    return TrainResult(model_path=MODEL_PATH, classes=list(pipe.classes_), report=report, cv_accuracy=cv_acc)

def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        return None

def predict_intent(text: str) -> Tuple[str, float]:
    model = load_model()
    if not model:
        return "ventas", 0.0
    proba = model.predict_proba([text])[0]
    idx = int(np.argmax(proba))
    label = model.classes_[idx]
    return label, float(proba[idx])
