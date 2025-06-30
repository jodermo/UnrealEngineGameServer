#!/usr/bin/env python3
"""
Dynamic URL generation script for Django backend
Generates urls.py based on entities.json configuration
"""

import json
from pathlib import Path

# Configuration paths
CONFIG_PATH = Path("config/entities.json")
APP_PATH = Path("adminpanel")

def generate_urls():
    """Generate Django URLs based on the entities.json configuration"""
    try:
        # Load configuration
        if CONFIG_PATH.exists():
            config = json.loads(CONFIG_PATH.read_text())
            print(f"Loaded configuration with {len(config)} models")
        else:
            print("No entities.json found, generating minimal URLs")
            config = {}
        
        # Start building the URLs file
        code_lines = [
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
        
        # Add router registrations for each model
        for model_name in config.keys():
            route_name = model_name.lower() + 's'  # e.g., 'players', 'matches'
            code_lines.extend([
                f"    try:",
                f"        router.register(r'{route_name}', views.{model_name}ViewSet)",
                f"    except AttributeError:",
                f"        pass  # {model_name}ViewSet not found"
            ])
        
        # Add health check endpoint
        code_lines.extend([
            "",
            "def api_health(request):",
            "    \"\"\"Health check endpoint with model information\"\"\"",
            "    model_info = {}",
            "    if VIEWS_AVAILABLE:",
            "        try:",
            "            from . import models"
        ])
        
        # Add model count checks for each configured model
        for model_name in config.keys():
            route_name = model_name.lower() + 's'
            code_lines.extend([
                f"            try:",
                f"                model_info['{route_name}'] = models.{model_name}.objects.count()",
                f"            except Exception:",
                f"                model_info['{route_name}'] = 'unavailable'"
            ])
        
        # Complete the health check function
        code_lines.extend([
            "        except ImportError:",
            "            pass",
            "",
            "    return JsonResponse({",
            "        'status': 'ok',",
            "        'service': 'django-backend',",
            "        'views_available': VIEWS_AVAILABLE,",
            f"        'configured_models': {list(config.keys())},",
            "        'model_counts': model_info,",
            "        'endpoints': {"
        ])
        
        # Add endpoint documentation
        for model_name in config.keys():
            route_name = model_name.lower() + 's'
            code_lines.append(f"            '{route_name}': '/api/{route_name}/',")
        
        # Complete the response
        code_lines.extend([
            "        },",
            "        'api_docs': '/api/schema/',",
            "        'admin_panel': '/admin/'",
            "    })",
            ""
        ])
        
        # Add additional utility endpoints
        code_lines.extend([
            "def api_status(request):",
            "    \"\"\"Simple status endpoint\"\"\"",
            "    return JsonResponse({'status': 'running', 'service': 'django-backend'})",
            ""
        ])
        
        # Define URL patterns
        code_lines.extend([
            "urlpatterns = [",
            "    path('health/', api_health, name='api-health'),",
            "    path('status/', api_status, name='api-status'),",
            "    path('', include(router.urls)),",
            "]"
        ])
        
        # Write the generated URLs file
        urls_content = "\n".join(code_lines)
        output_path = APP_PATH / "urls.py"
        output_path.write_text(urls_content)
        
        print(f"URLs generated successfully at {output_path}")
        
        # Display generated endpoints
        if config:
            print(f"\nGenerated API endpoints:")
            for model_name in config.keys():
                route_name = model_name.lower() + 's'
                print(f"   - /{route_name}/ ({model_name} CRUD operations)")
            print(f"   - /health/ (API health check)")
            print(f"   - /status/ (Simple status)")
        
        return True
        
    except Exception as e:
        print(f"Error generating URLs: {e}")
        
        # Fallback: create minimal working URLs
        print("Creating fallback URLs...")
        fallback_content = '''from django.urls import path
from django.http import JsonResponse

def health(request):
    return JsonResponse({'status': 'ok', 'service': 'adminpanel'})

def status(request):
    return JsonResponse({'status': 'running', 'service': 'adminpanel'})

urlpatterns = [
    path('health/', health, name='health'),
    path('status/', status, name='status'),
]
'''
        
        try:
            (APP_PATH / "urls.py").write_text(fallback_content)
            print("Fallback URLs created")
            return True
        except Exception as fallback_error:
            print(f"Failed to create fallback URLs: {fallback_error}")
            return False

def validate_urls():
    """Validate the generated URLs file"""
    urls_path = APP_PATH / "urls.py"
    
    if not urls_path.exists():
        print("urls.py does not exist")
        return False
    
    try:
        # Try to compile the URLs file
        content = urls_path.read_text()
        compile(content, str(urls_path), 'exec')
        print("URLs file syntax is valid")
        return True
    except SyntaxError as e:
        print(f"Syntax error in urls.py: {e}")
        return False
    except Exception as e:
        print(f"Error validating urls.py: {e}")
        return False

def main():
    """Main function to generate and validate URLs"""
    print("🔧 Generating Django URLs from entities.json...")
    
    # Ensure the app directory exists
    APP_PATH.mkdir(parents=True, exist_ok=True)
    
    # Generate URLs
    if generate_urls():
        print("URL generation completed")
        
        # Validate the generated file
        if validate_urls():
            print("All done! URLs are ready to use")
        else:
            print("URL validation failed, but file was created")
    else:
        print("URL generation failed")

if __name__ == "__main__":
    main()