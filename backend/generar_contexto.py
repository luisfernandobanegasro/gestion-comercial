# backend/generar_contexto.py
import os

# --- Lista de archivos relevantes para Reportes e IA ---
# Si añades o cambias archivos, actualiza esta lista.
ARCHIVOS_RELEVANTES = [
    # Backend - Lógica de Reportes
    "reportes/views.py",
    "reportes/parser.py",
    "reportes/runner.py",
    "reportes/services.py",
    "reportes/urls.py",
    "reportes/catalog.py"
    "reportes/dsl.py"
    "reportes/intent_parser.py"
    "reportes/queries_extra.py"
    "reportes/query_builder.py"

    # Backend - Lógica de IA (Intenciones y Predicciones)
    "ia/train_intents.py",
    "ia/train_predictions.py",

    # Backend - Endpoints de Analítica
    "analitica/views.py",
    "analitica/urls.py",

    # Frontend - Componentes de UI
    "../frontend/src/pages/reportes/Reportes.jsx",
    "../frontend/src/pages/Dashboard.jsx",
]

OUTPUT_FILENAME = "contexto_reportes_ia.txt"

def generar_contexto():
    """
    Concatena el contenido de los archivos relevantes en un solo .txt
    """
    print(f"Generando archivo de contexto: {OUTPUT_FILENAME}...")
    
    try:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as outfile:
            for filepath in ARCHIVOS_RELEVANTES:
                outfile.write("=" * 80 + "\n")
                outfile.write(f"Archivo: {filepath.replace('../', '')}\n")
                outfile.write("=" * 80 + "\n\n")
                
                try:
                    with open(filepath, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read())
                    outfile.write("\n\n")
                except FileNotFoundError:
                    outfile.write(f"*** ERROR: Archivo no encontrado en la ruta: {filepath} ***\n\n")
        print(f"¡Éxito! El archivo '{OUTPUT_FILENAME}' ha sido creado en la carpeta 'backend'.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    generar_contexto()