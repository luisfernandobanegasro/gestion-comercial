# ia/train_predictions.py
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
from datetime import timedelta

from django.conf import settings
from django.db import models
from ventas.models import Venta


def get_sales_data():
    """
    Obtiene los datos de ventas diarias de la base de datos y los prepara para el modelo.
    """
    # Obtenemos ventas pagadas, agrupadas por día
    sales = (
        Venta.objects.filter(estado="pagada")
        .values("creado_en__date")
        .annotate(total_ventas=models.Sum("total"))
        .order_by("creado_en__date")
    )

    if not sales:
        return pd.DataFrame()

    df = pd.DataFrame(list(sales))
    df = df.rename(columns={"creado_en__date": "fecha", "total_ventas": "ventas"})
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.set_index("fecha")

    # Asegurarnos de que tenemos un rango de fechas continuo, rellenando días sin ventas con 0
    df = df.asfreq("D", fill_value=0)
    return df


def create_features(df):
    """
    Crea características (features) a partir de la fecha para el modelo.
    """
    df["dia_semana"] = df.index.dayofweek  # Lunes=0, Domingo=6
    df["dia_mes"] = df.index.day
    df["mes"] = df.index.month
    df["anio"] = df.index.year
    df["semana_anio"] = df.index.isocalendar().week.astype(int)
    return df


def train_model():
    """
    Función principal que carga datos, entrena el modelo y lo guarda.
    """
    print("Iniciando entrenamiento del modelo de predicción de ventas...")
    df = get_sales_data()

    # Si no hay datos, no podemos entrenar
    if df.shape[0] < 30:
        print("No hay suficientes datos históricos (< 30 días). No se entrenará el modelo.")
        return None

    df = create_features(df)

    FEATURES = ["dia_semana", "dia_mes", "mes", "anio", "semana_anio"]
    TARGET = "ventas"

    X = df[FEATURES]
    y = df[TARGET]

    # Dividimos los datos para una validación simple
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )

    # Modelo: RandomForestRegressor
    model = RandomForestRegressor(n_estimators=100, random_state=42, min_samples_leaf=2)
    model.fit(X_train, y_train)

    # Evaluamos el modelo (opcional, pero bueno para logging)
    preds = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    print(f"Entrenamiento completado. RMSE en set de prueba: {rmse:.2f}")

    # Guardamos el modelo serializado
    model_path = os.path.join(settings.BASE_DIR, "ia", "sales_prediction_model.joblib")
    joblib.dump(model, model_path)
    print(f"Modelo guardado en: {model_path}")

    return model_path


def generate_predictions(days_to_predict=30):
    """
    Carga el modelo guardado y genera predicciones para los próximos N días.
    """
    model_path = os.path.join(settings.BASE_DIR, "ia", "sales_prediction_model.joblib")
    if not os.path.exists(model_path):
        return []

    model = joblib.load(model_path)
    future_dates = pd.date_range(start=pd.Timestamp.now().date(), periods=days_to_predict + 1)
    future_df = pd.DataFrame(index=future_dates)
    future_df = create_features(future_df)

    predictions = model.predict(
        future_df[["dia_semana", "dia_mes", "mes", "anio", "semana_anio"]]
    )

    return [
        {"fecha": date.strftime("%Y-%m-%d"), "prediccion": float(pred)}
        for date, pred in zip(future_dates, predictions)
    ]
