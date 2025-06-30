# Generate Django models from your entities.json config
import json
from pathlib import Path

CONFIG_PATH = Path("config/entities.json")
APP_PATH = Path("DjangoBackend/adminpanel")

def generate_models():
    try:
        config = json.loads(CONFIG_PATH.read_text())
        
        code = [
            "from django.db import models",
            "from django.contrib.auth.models import User",
            "",
            "# Auto-generated models from entities.json config",
            ""
        ]
        
        # Generate each model
        for model_name, model_config in config.items():
            code.append(f"class {model_name}(models.Model):")
            
            # Add fields
            fields = model_config.get("fields", {})
            if not fields:
                code.append("    pass  # No fields defined")
            else:
                for field_name, field_definition in fields.items():
                    # Handle string field definitions
                    if isinstance(field_definition, str):
                        # Clean up the field definition
                        field_def = field_definition.replace("models.", "")
                        code.append(f"    {field_name} = models.{field_def}")
                    else:
                        # Handle dict field definitions (for future expansion)
                        code.append(f"    {field_name} = models.CharField(max_length=255)  # TODO: Configure properly")
            
            # Add metadata
            code.extend([
                "",
                "    class Meta:",
                f"        verbose_name = '{model_name}'",
                f"        verbose_name_plural = '{model_name}s'",
                f"        db_table = '{model_name.lower()}'",
                "",
                "    def __str__(self):",
                f"        return f'{model_name} {{self.pk}}'",
                ""
            ])
        
        # Write the models file
        models_code = "\n".join(code)
        (APP_PATH / "models.py").write_text(models_code)
        print("models.py generated from config!")
        
        return config
        
    except Exception as e:
        print(f"Error generating models: {e}")
        return {}

def generate_views(config):
    try:
        code = [
            "from rest_framework import viewsets, permissions",
            "from rest_framework.decorators import action",
            "from rest_framework.response import Response",
            "from django.http import JsonResponse",
            "from .models import *",
            "from .serializers import *",
            "",
            "# Auto-generated ViewSets from entities.json config",
            ""
        ]
        
        for model_name, model_config in config.items():
            permissions_list = model_config.get("permissions", ["read", "create", "update", "delete"])
            
            code.extend([
                f"class {model_name}ViewSet(viewsets.ModelViewSet):",
                f"    queryset = {model_name}.objects.all()",
                f"    serializer_class = {model_name}Serializer",
                f"    permission_classes = [permissions.IsAuthenticatedOrReadOnly]",
                "",
                f"    # Permissions: {permissions_list}",
                ""
            ])
            
            # Add custom actions based on permissions
            if "read" not in permissions_list:
                code.extend([
                    "    def list(self, request):",
                    "        return Response({'error': 'List not permitted'}, status=403)",
                    "",
                    "    def retrieve(self, request, pk=None):",
                    "        return Response({'error': 'Retrieve not permitted'}, status=403)",
                    ""
                ])
            
            if "create" not in permissions_list:
                code.extend([
                    "    def create(self, request):",
                    "        return Response({'error': 'Create not permitted'}, status=403)",
                    ""
                ])
            
            if "update" not in permissions_list:
                code.extend([
                    "    def update(self, request, pk=None):",
                    "        return Response({'error': 'Update not permitted'}, status=403)",
                    "",
                    "    def partial_update(self, request, pk=None):",
                    "        return Response({'error': 'Partial update not permitted'}, status=403)",
                    ""
                ])
            
            if "delete" not in permissions_list:
                code.extend([
                    "    def destroy(self, request, pk=None):",
                    "        return Response({'error': 'Delete not permitted'}, status=403)",
                    ""
                ])
        
        views_code = "\n".join(code)
        (APP_PATH / "views.py").write_text(views_code)
        print("views.py generated from config!")
        
    except Exception as e:
        print(f"Error generating views: {e}")

def generate_serializers(config):
    try:
        code = [
            "from rest_framework import serializers",
            "from .models import *",
            "",
            "# Auto-generated Serializers from entities.json config",
            ""
        ]
        
        for model_name, model_config in config.items():
            serializer_options = model_config.get("serializer_options", {})
            depth = serializer_options.get("depth", 1)
            exclude_fields = serializer_options.get("exclude", [])
            
            code.extend([
                f"class {model_name}Serializer(serializers.ModelSerializer):",
                "    class Meta:",
                f"        model = {model_name}",
                f"        fields = '__all__'",
            ])
            
            if exclude_fields:
                code.append(f"        exclude = {exclude_fields}")
            
            code.extend([
                f"        depth = {depth}",
                ""
            ])
        
        serializers_code = "\n".join(code)
        (APP_PATH / "serializers.py").write_text(serializers_code)
        print("serializers.py generated from config!")
        
    except Exception as e:
        print(f"Error generating serializers: {e}")

def generate_admin(config):
    try:
        code = [
            "from django.contrib import admin",
            "from .models import *",
            "",
            "# Auto-generated Admin from entities.json config",
            ""
        ]
        
        for model_name in config.keys():
            code.extend([
                f"@admin.register({model_name})",
                f"class {model_name}Admin(admin.ModelAdmin):",
                f"    list_display = ['pk'] + [f.name for f in {model_name}._meta.fields[1:6]]  # Show first 5 fields",
                f"    search_fields = ['pk']",
                f"    list_filter = []",
                ""
            ])
        
        admin_code = "\n".join(code)
        (APP_PATH / "admin.py").write_text(admin_code)
        print("admin.py generated from config!")
        
    except Exception as e:
        print(f"Error generating admin: {e}")

def main():
    print("Generating Django components from entities.json...")
    
    # Generate all components
    config = generate_models()
    if config:
        generate_serializers(config)
        generate_views(config)
        generate_admin(config)
        
        # Generate URLs last
        pass
        generate_urls()
        
        print(f"\nGenerated components for {len(config)} models:")
        for model_name in config.keys():
            print(f"   - {model_name}")
        
        print("\nNext steps:")
        print("   1. Run: python manage.py makemigrations")
        print("   2. Run: python manage.py migrate")
        print("   3. Create superuser: python manage.py createsuperuser")
        print("   4. Test API at: http://localhost:8000/api/health/")

if __name__ == "__main__":
    main()