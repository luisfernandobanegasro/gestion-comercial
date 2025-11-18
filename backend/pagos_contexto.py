# backend/generar_contexto_ventas.py
import os

# --- Lista de archivos relevantes para Ventas / Carrito ---
# Ajusta o añade rutas si mueves algo de lugar.
ARCHIVOS_RELEVANTES = [
    # Ventas
    "ventas/models.py",
    "ventas/serializers.py",
    "ventas/views.py",
    "ventas/urls.py",      # si usas urls propias del app

    # Registro del router (si las ventas se registran aquí)
    "core/urls.py",

    # Catálogo
    "catalogo/models.py",
    "catalogo/serializers.py",
    "catalogo/views.py",

    # Clientes
    "clientes/models.py",
    "clientes/serializers.py",
    "clientes/views.py",
]

OUTPUT_FILENAME = "contexto_ventas_carrito.txt"


def generar_contexto():
    """
    Concatena el contenido de los archivos relevantes en un solo .txt
    para poder compartir contexto fácilmente.
    """
    print(f"Generando archivo de contexto: {OUTPUT_FILENAME}...")

    try:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as outfile:
            for filepath in ARCHIVOS_RELEVANTES:
                outfile.write("=" * 80 + "\n")
                outfile.write(f"Archivo: {filepath}\n")
                outfile.write("=" * 80 + "\n\n")

                try:
                    with open(filepath, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read())
                    outfile.write("\n\n")
                except FileNotFoundError:
                    outfile.write(
                        f"*** ERROR: Archivo no encontrado en la ruta: {filepath} ***\n\n"
                    )

        print(f"¡Éxito! El archivo '{OUTPUT_FILENAME}' ha sido creado en la carpeta 'backend'.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")


if __name__ == "__main__":
    generar_contexto()
