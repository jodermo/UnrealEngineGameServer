# Generate Django models from your entities.json config
import json
from pathlib import Path

CONFIG_PATH = Path("config/entities.json")
APP_PATH = Path("adminpanel")

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
                        # Process field definition and ensure proper Django imports
                        field_def = field_definition
                        
                        # Handle Django constants that need models. prefix
                        django_constants = ['SET_NULL', 'CASCADE', 'PROTECT', 'SET_DEFAULT', 'DO_NOTHING']
                        for constant in django_constants:
                            if f'on_delete={constant}' in field_def:
                                field_def = field_def.replace(f'on_delete={constant}', f'on_delete=models.{constant}')
                        
                        # Remove any existing models. prefix to avoid double prefixing
                        field_def = field_def.replace("models.", "")
                        
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

def generate_urls(config=None):
    """Generate URLs based on config"""
    try:
        if config is None:
            # Try to load config if not provided
            if CONFIG_PATH.exists():
                config = json.loads(CONFIG_PATH.read_text())
            else:
                config = {}
        
        code = [
            "from django.urls import path, include",
            "from rest_framework.routers import DefaultRouter",
            "from django.http import JsonResponse",
            "",
            "# Import views safely",
            "try:",
            "    from . import views",
            "    VIEWS_AVAILABLE = True",
            "except ImportError:",
            "    VIEWS_AVAILABLE = False",
            "",
            "router = DefaultRouter()",
            "",
            "# Register ViewSets if views are available",
            "if VIEWS_AVAILABLE:"
        ]
        
        for model_name in config.keys():
            route = model_name.lower() + 's'
            code.extend([
                f"    try:",
                f"        router.register(r'{route}', views.{model_name}ViewSet)",
                f"    except AttributeError:",
                f"        pass"
            ])
        
        code.extend([
            "",
            "def api_health(request):",
            "    model_info = {}",
            "    if VIEWS_AVAILABLE:",
            "        try:",
            "            from . import models"
        ])
        
        for model_name in config.keys():
            code.extend([
                f"            try:",
                f"                model_info['{model_name.lower()}s'] = models.{model_name}.objects.count()",
                f"            except:",
                f"                model_info['{model_name.lower()}s'] = 'unavailable'"
            ])
        
        code.extend([
            "        except ImportError:",
            "            pass",
            "",
            "    return JsonResponse({",
            "        'status': 'ok',",
            "        'views_available': VIEWS_AVAILABLE,",
            f"        'configured_models': {list(config.keys())},",
            "        'model_counts': model_info,",
            "        'endpoints': {"
        ])
        
        for model_name in config.keys():
            route = model_name.lower() + 's'
            code.append(f"            '{route}': '/api/{route}/',")
        
        code.extend([
            "        }",
            "    })",
            "",
            "urlpatterns = [",
            "    path('health/', api_health, name='api-health'),",
            "    path('', include(router.urls)),",
            "]"
        ])
        
        urls_code = "\n".join(code)
        (APP_PATH / "urls.py").write_text(urls_code)
        print("URLs generated successfully")
        
    except Exception as e:
        print(f"Error generating URLs: {e}")

def main():
    print("Generating Django components from entities.json...")
    
    # Generate all components
    config = generate_models()
    if config:
        generate_serializers(config)
        generate_views(config)
        generate_admin(config)
        
        # Generate URLs last
        generate_urls(config)
        
        print(f"Generated components for {len(config)} models:")
        for model_name in config.keys():
            print(f"   - {model_name}")
        
        print("Next steps:")
        print("   1. Run: python manage.py makemigrations")
        print("   2. Run: python manage.py migrate")
        print("   3. Create superuser: python manage.py createsuperuser")
        print("   4. Test API at: http://localhost:8000/api/health/")

if __name__ == "__main__":
    main()