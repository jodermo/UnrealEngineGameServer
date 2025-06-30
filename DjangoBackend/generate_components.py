import json
from pathlib import Path

# Path to the JSON config file and Django app folder
CONFIG_PATH = Path("config/entities.json")
APP_PATH = Path("DjangoBackend/adminpanel")  # Adjust if your app name is different
APP_PATH.mkdir(parents=True, exist_ok=True)

# Converts CamelCase to snake_case (currently unused, but could be useful)
def snake(name):
    return "".join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip("_")

# Generates a Django model class from the field definitions
def write_model(name, fields):
    model_code = f"class {name}(models.Model):\n"
    for field_name, field_def in fields.items():
        if isinstance(field_def, dict):
            field_type = field_def["type"]
            validators = field_def.get("validators", [])
            model_code += f"    {field_name} = models.{field_type}"
            if validators:
                model_code += f", validators={validators}"
            model_code += "\n"
    return model_code

# Registers the model in Django admin
def write_admin(name):
    return f"admin.site.register({name})\n"

# Generates a Django REST Framework serializer
def write_serializer(name, fields):
    nested_lines = ""
    serializer_code = f"class {name}Serializer(serializers.ModelSerializer):\n"

    for field_name, field_type in fields.items():
        # Handle ForeignKey relationships by injecting nested serializers
        if "ForeignKey(" in field_type:
            related_model = field_type.split("ForeignKey(")[1].split(",")[0].strip("'\"")
            serializer_code += f"    {field_name} = {related_model}Serializer(read_only=True)\n"
            nested_lines += f"\n\n{write_serializer(related_model, {})}"  # Dummy fields for now

    serializer_code += "    class Meta:\n"
    serializer_code += f"        model = {name}\n"
    serializer_code += "        fields = '__all__'\n"

    return serializer_code + nested_lines

# Generates a DRF ViewSet for each model
def write_view(name):
    return f"""
class {name}ViewSet(viewsets.ModelViewSet):
    queryset = {name}.objects.all()
    serializer_class = {name}Serializer
"""

# Main code generation function
def generate():
    config = json.loads(CONFIG_PATH.read_text())

    # Ensure the output folder exists
    APP_PATH.mkdir(parents=True, exist_ok=True)

    # Boilerplate imports
    models_code = "from django.db import models\n\n"
    admin_code = "from django.contrib import admin\nfrom .models import *\n\n"
    serializers_code = "from rest_framework import serializers\nfrom .models import *\n\n"
    views_code = "from rest_framework import viewsets\nfrom .models import *\nfrom .serializers import *\n\n"

    generated_serializers = set()

    for name, details in config.items():
        fields = details.get("fields", {})

        models_code += write_model(name, fields) + "\n"
        admin_code += write_admin(name) + "\n"

        # Avoid regenerating nested serializers
        if name not in generated_serializers:
            serializers_code += write_serializer(name, fields) + "\n"
            generated_serializers.add(name)

        views_code += write_view(name) + "\n"

    # Write out the generated files
    (APP_PATH / "models.py").write_text(models_code)
    (APP_PATH / "admin.py").write_text(admin_code)
    (APP_PATH / "serializers.py").write_text(serializers_code)
    (APP_PATH / "views.py").write_text(views_code)

    print("Components generated from config!")

if __name__ == "__main__":
    generate()
