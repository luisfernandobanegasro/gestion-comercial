# backend/inspect_models_standalone.py
import os
import sys
import django

def setup_django():
    """
    Configura el entorno de Django para poder usar los modelos
    fuera del contexto de manage.py.
    """
    # Añade la ruta del proyecto (backend) al sys.path
    project_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_path)
    
    # Apunta a tu archivo de settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    # Carga la configuración de Django
    django.setup()

def inspect_and_write():
    """
    Inspecciona los modelos y escribe la estructura en un archivo.
    """
    from django.apps import apps
    from django.conf import settings

    output_filename = "models_structure.txt"
    
    project_apps = [
        app_config.name for app_config in apps.get_app_configs()
        if app_config.path.startswith(str(settings.BASE_DIR))
    ]

    print(f"Inspeccionando modelos de las apps: {', '.join(project_apps)}")

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("=====================================================\n")
        f.write("=      Estructura de Modelos del Proyecto Django      =\n")
        f.write("=====================================================\n\n")

        for app_name in project_apps:
            app_config = apps.get_app_config(app_name.split('.')[-1])
            models = app_config.get_models()
            
            if not models: continue

            f.write(f"--- App: {app_config.name} ---\n")
            for model in models:
                f.write(f"\n  Modelo: {model.__name__}\n  {'-'*20}\n")
                for field in model._meta.get_fields():
                    field_type = field.__class__.__name__
                    if field.is_relation:
                        related_model = field.related_model.__name__ if field.related_model else 'N/A'
                        f.write(f"    - {field.name} ({field_type}) -> Relación con '{related_model}'\n")
                    else:
                        f.write(f"    - {field.name} ({field_type})\n")
            f.write("\n")

    print(f"¡Éxito! La estructura de los modelos ha sido guardada en '{output_filename}'.")

if __name__ == "__main__":
    setup_django()
    inspect_and_write()