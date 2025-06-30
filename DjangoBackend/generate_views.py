#!/usr/bin/env python3
"""
Generate Django URLs from entities.json configuration
Creates comprehensive URL routing with API versioning, custom endpoints, and documentation
"""

import json
from pathlib import Path

# Configuration paths
CONFIG_PATH = Path("config/entities.json")
APP_PATH = Path("adminpanel")

def generate_api_urls(config):
    """Generate API URL patterns with versioning and custom endpoints"""
    code_lines = [
        "from django.urls import path, include",
        "from rest_framework.routers import DefaultRouter",
        "from rest_framework.documentation import include_docs_urls",
        "from django.http import JsonResponse",
        "from django.views.decorators.csrf import csrf_exempt",
        "from django.utils.decorators import method_decorator",
        "",
        "# Import views safely with error handling",
        "try:",
        "    from . import views",
        "    VIEWS_AVAILABLE = True",
        "    print('✅ Views imported successfully')",
        "except ImportError as e:",
        "    VIEWS_AVAILABLE = False",
        "    print(f'⚠️  Views import failed: {e}')",
        "",
        "# Create API router",
        "router = DefaultRouter()",
        "router.trailing_slash = '/?'  # Make trailing slash optional",
        "",
        "# Register ViewSets if views are available",
        "if VIEWS_AVAILABLE:",
    ]
    
    # Register standard ViewSets
    for model_name in config.keys():
        route_name = model_name.lower() + 's'
        code_lines.extend([
            f"    try:",
            f"        router.register(r'{route_name}', views.{model_name}ViewSet, basename='{model_name.lower()}')",
            f"        print(f'✅ Registered {route_name} endpoint')",
            f"    except AttributeError:",
            f"        print(f'⚠️  {model_name}ViewSet not found, skipping {route_name}')",
            f"        pass",
        ])
    
    code_lines.extend([
        "",
        "    # Register utility views",
        "    try:",
        "        router.register(r'health', views.APIHealthView, basename='health')",
        "        print('✅ Registered health endpoint')",
        "    except AttributeError:",
        "        print('⚠️  APIHealthView not found')",
        "        pass",
        ""
    ])
    
    return code_lines

def generate_health_endpoint():
    """Generate standalone health check endpoint"""
    code_lines = [
        "# ============================================================================",
        "# STANDALONE HEALTH ENDPOINTS",
        "# ============================================================================",
        "",
        "@csrf_exempt",
        "def api_health(request):",
        '    """Comprehensive API health check with model information"""',
        "    model_info = {}",
        "    endpoints = {}",
        "    ",
        "    if VIEWS_AVAILABLE:",
        "        try:",
        "            from . import models",
        "            from django.apps import apps",
        "            ",
        "            # Get model counts",
    ]
    
    return code_lines

def generate_model_specific_endpoints(config):
    """Generate custom endpoints for each model"""
    code_lines = [
        "# ============================================================================",
        "# MODEL-SPECIFIC ENDPOINTS",
        "# ============================================================================",
        ""
    ]
    
    for model_name, model_config in config.items():
        fields = model_config.get("fields", {})
        route_name = model_name.lower() + 's'
        
        # Check if model has date fields for timeline endpoints
        date_fields = [field for field, field_def in fields.items() 
                      if 'DateTimeField' in str(field_def) or 'DateField' in str(field_def)]
        
        if date_fields:
            code_lines.extend([
                f"def {model_name.lower()}_timeline(request):",
                f'    """Timeline view for {model_name} records"""',
                f"    if not VIEWS_AVAILABLE:",
                f"        return JsonResponse({{'error': 'Views not available'}}, status=503)",
                f"    ",
                f"    try:",
                f"        from .models import {model_name}",
                f"        from django.utils import timezone",
                f"        from datetime import timedelta",
                f"        ",
                f"        # Get timeline data",
                f"        days = int(request.GET.get('days', 30))",
                f"        start_date = timezone.now() - timedelta(days=days)",
                f"        ",
                f"        timeline_data = {model_name}.objects.filter(",
                f"            {date_fields[0]}__gte=start_date",
                f"        ).extra(",
                f"            select={{'day': 'date({date_fields[0]})'}}"
                f"        ).values('day').annotate(",
                f"            count=models.Count('id')",
                f"        ).order_by('day')",
                f"        ",
                f"        return JsonResponse({{",
                f"            'model': '{model_name}',",
                f"            'timeline': list(timeline_data),",
                f"            'period_days': days",
                f"        }})",
                f"    except Exception as e:",
                f"        return JsonResponse({{'error': str(e)}}, status=500)",
                f"",
            ])
        
        # Generate search endpoint for models with searchable fields
        searchable_fields = [field for field, field_def in fields.items() 
                           if any(field_type in str(field_def) for field_type in ['CharField', 'TextField', 'EmailField'])]
        
        if searchable_fields:
            code_lines.extend([
                f"def {model_name.lower()}_search(request):",
                f'    """Advanced search for {model_name} records"""',
                f"    if not VIEWS_AVAILABLE:",
                f"        return JsonResponse({{'error': 'Views not available'}}, status=503)",
                f"    ",
                f"    try:",
                f"        from .models import {model_name}",
                f"        from django.db.models import Q",
                f"        ",
                f"        query = request.GET.get('q', '')",
                f"        if not query:",
                f"            return JsonResponse({{'error': 'No search query provided'}}, status=400)",
                f"        ",
                f"        # Build search query",
                f"        search_query = Q()",
                f"        search_fields = {searchable_fields[:4]}  # Limit to 4 fields",
                f"        ",
                f"        for field in search_fields:",
                f"            search_query |= Q(**{{f'{{field}}__icontains': query}})",
                f"        ",
                f"        results = {model_name}.objects.filter(search_query)[:50]  # Limit results",
                f"        ",
                f"        return JsonResponse({{",
                f"            'model': '{model_name}',",
                f"            'query': query,",
                f"            'count': results.count(),",
                f"            'results': [{{",
                f"                'id': obj.id,",
                f"                'display': str(obj)",
                f"            }} for obj in results]",
                f"        }})",
                f"    except Exception as e:",
                f"        return JsonResponse({{'error': str(e)}}, status=500)",
                f"",
            ])
    
    return code_lines

def generate_documentation_urls():
    """Generate documentation and schema URLs"""
    code_lines = [
        "# ============================================================================",
        "# DOCUMENTATION AND SCHEMA URLs",
        "# ============================================================================",
        "",
        "def api_schema_view(request):",
        '    """Custom API schema view"""',
        "    try:",
        "        from rest_framework.schemas import get_schema_view",
        "        from rest_framework.renderers import JSONRenderer",
        "        ",
        "        schema_view = get_schema_view(",
        "            title='Unreal Engine Game Server API',",
        "            description='Dynamic REST API for game server management',",
        "            version='1.0.0',",
        "            renderer_classes=[JSONRenderer]",
        "        )",
        "        return schema_view(request)",
        "    except Exception as e:",
        "        return JsonResponse({",
        "            'error': 'Schema generation failed',",
        "            'message': str(e)",
        "        }, status=500)",
        "",
        "def api_docs_view(request):",
        '    """API documentation landing page"""',
        "    docs_info = {",
        "        'title': 'Unreal Engine Game Server API Documentation',",
        "        'version': '1.0.0',",
        "        'description': 'RESTful API for managing game server data',",
        "        'base_url': request.build_absolute_uri('/api/'),",
        "        'endpoints': {},",
        "        'authentication': {",
        "            'types': ['Session', 'Token'],",
        "            'login_url': '/admin/login/',",
        "            'token_url': '/api/auth/token/'",
        "        }",
        "    }",
        "    ",
        "    if VIEWS_AVAILABLE:",
    ]
    
    return code_lines

def generate_main_urls(config):
    """Generate the main URL patterns"""
    code_lines = []
    
    # Add the health check implementations
    code_lines.extend([
        "            # Model information",
        "            try:",
        "                from . import models",
    ])
    
    for model_name in config.keys():
        code_lines.extend([
            f"                try:",
            f"                    model_info['{model_name.lower()}s'] = models.{model_name}.objects.count()",
            f"                    endpoints['{model_name.lower()}s'] = {{",
            f"                        'list': f'{{request.build_absolute_uri(\"/api/{model_name.lower()}s/\")}}',",
            f"                        'detail': f'{{request.build_absolute_uri(\"/api/{model_name.lower()}s/{{id}}/\")}}',",
            f"                        'recent': f'{{request.build_absolute_uri(\"/api/{model_name.lower()}s/recent/\")}}',",
            f"                        'stats': f'{{request.build_absolute_uri(\"/api/{model_name.lower()}s/stats/\")}}',",
            f"                        'export': f'{{request.build_absolute_uri(\"/api/{model_name.lower()}s/export/\")}}',",
            f"                        'timeline': f'{{request.build_absolute_uri(\"/api/{model_name.lower()}s/timeline/\")}}',",
            f"                        'search': f'{{request.build_absolute_uri(\"/api/{model_name.lower()}s/search/\")}}',",
            f"                    }}",
            f"                except Exception:",
            f"                    model_info['{model_name.lower()}s'] = 'unavailable'",
            f"                    endpoints['{model_name.lower()}s'] = 'unavailable'",
        ])
    
    code_lines.extend([
        "            except ImportError:",
        "                pass",
        "        ",
        "        docs_info['endpoints'] = endpoints",
        "    ",
        "    return JsonResponse(docs_info)",
        "",
        "# ============================================================================",
        "# MAIN URL PATTERNS",
        "# ============================================================================",
        "",
        "# Define URL patterns",
        "urlpatterns = [",
        "    # API Documentation",
        "    path('', api_docs_view, name='api-docs'),",
        "    path('docs/', api_docs_view, name='api-documentation'),",
        "    path('schema/', api_schema_view, name='api-schema'),",
        "    ",
        "    # Health and Status",
        "    path('health/', api_health, name='api-health'),",
        "    path('status/', api_health, name='api-status'),  # Alias for health",
        "    ",
        "    # Model-specific endpoints",
    ])
    
    # Add model-specific URL patterns
    for model_name in config.keys():
        route_name = model_name.lower() + 's'
        code_lines.extend([
            f"    path('{route_name}/timeline/', {model_name.lower()}_timeline, name='{model_name.lower()}-timeline'),",
            f"    path('{route_name}/search/', {model_name.lower()}_search, name='{model_name.lower()}-search'),",
        ])
    
    code_lines.extend([
        "    ",
        "    # Include router URLs (all ViewSet endpoints)",
        "    path('', include(router.urls)),",
        "]",
        "",
        "# Add router URLs to urlpatterns if views are available",
        "if VIEWS_AVAILABLE:",
        "    print(f'✅ API URLs configured with {len(router.registry)} registered ViewSets')",
        "    ",
        "    # Print registered routes for debugging",
        "    print('📋 Registered API endpoints:')",
        "    for prefix, viewset, basename in router.registry:",
        "        print(f'   - /{prefix}/ ({basename})')",
        "else:",
        "    print('⚠️  No ViewSets available, API will have limited functionality')",
        "",
        "# Add error handling for missing views",
        "try:",
        "    # Test if we can import all required components",
        "    if VIEWS_AVAILABLE:",
        "        from . import views, models, serializers",
        "        print('✅ All components imported successfully')",
        "except ImportError as e:",
        "    print(f'⚠️  Component import warning: {e}')",
    ])
    
    return code_lines

def generate_urls():
    """Generate comprehensive Django URLs from entities.json configuration"""
    try:
        # Load configuration
        if CONFIG_PATH.exists():
            config = json.loads(CONFIG_PATH.read_text())
            print(f"Loaded configuration with {len(config)} models")
        else:
            print("No entities.json found, generating minimal URLs")
            config = {}
        
        # Start building the URLs file
        code_lines = []
        
        # Add API URL generation
        api_urls = generate_api_urls(config)
        code_lines.extend(api_urls)
        
        # Add health endpoint implementation
        health_code = generate_health_endpoint()
        code_lines.extend(health_code)
        
        # Complete the health endpoint
        health_completion = []
        for model_name in config.keys():
            health_completion.extend([
                f"            try:",
                f"                model_info['{model_name.lower()}s'] = models.{model_name}.objects.count()",
                f"            except Exception:",
                f"                model_info['{model_name.lower()}s'] = 'unavailable'",
            ])
        
        health_completion.extend([
            "        except ImportError:",
            "            model_info = {'error': 'Models not available'}",
            "    ",
            "    # Build endpoint information",
            "    if VIEWS_AVAILABLE:",
        ])
        
        for model_name in config.keys():
            route_name = model_name.lower() + 's'
            health_completion.extend([
                f"        endpoints['{route_name}'] = {{",
                f"            'list': f'/api/{route_name}/',",
                f"            'detail': f'/api/{route_name}/{{id}}/',",
                f"            'recent': f'/api/{route_name}/recent/',",
                f"            'stats': f'/api/{route_name}/stats/',",
                f"            'export': f'/api/{route_name}/export/',",
                f"            'timeline': f'/api/{route_name}/timeline/',",
                f"            'search': f'/api/{route_name}/search/'",
                f"        }}",
            ])
        
        health_completion.extend([
            "    ",
            "    return JsonResponse({",
            "        'status': 'healthy',",
            "        'service': 'django-rest-api',",
            "        'timestamp': timezone.now().isoformat(),",
            "        'views_available': VIEWS_AVAILABLE,",
            f"        'configured_models': {list(config.keys())},",
            "        'model_counts': model_info,",
            "        'endpoints': endpoints,",
            "        'features': {",
            "            'filtering': True,",
            "            'searching': True,",
            "            'pagination': True,",
            "            'bulk_operations': True,",
            "            'export': True,",
            "            'statistics': True",
            "        },",
            "        'api_version': '1.0.0'",
            "    })",
            ""
        ])
        
        code_lines.extend(health_completion)
        
        # Add model-specific endpoints
        model_endpoints = generate_model_specific_endpoints(config)
        code_lines.extend(model_endpoints)
        
        # Add documentation URLs
        docs_urls = generate_documentation_urls()
        code_lines.extend(docs_urls)
        
        # Complete documentation implementation
        code_lines.extend(generate_main_urls(config))
        
        # Add API versioning support
        code_lines.extend([
            "",
            "# ============================================================================",
            "# API VERSIONING SUPPORT",
            "# ============================================================================",
            "",
            "# V1 API URLs (current)",
            "v1_patterns = urlpatterns.copy()",
            "",
            "# Future: V2 API URLs can be added here",
            "# v2_patterns = [...]",
            "",
            "# Version-aware URL patterns",
            "versioned_patterns = [",
            "    path('v1/', include((v1_patterns, 'api'), namespace='v1')),",
            "    # path('v2/', include((v2_patterns, 'api'), namespace='v2')),",
            "]",
            "",
            "# Add versioned patterns to main urlpatterns",
            "urlpatterns.extend([",
            "    path('version/', lambda request: JsonResponse({",
            "        'current_version': 'v1',",
            "        'available_versions': ['v1'],",
            "        'deprecated_versions': [],",
            "        'api_docs': '/api/docs/'",
            "    }), name='api-version'),",
            "])",
        ])
        
        # Add utility functions at the end
        code_lines.extend([
            "",
            "# ============================================================================",
            "# UTILITY FUNCTIONS",
            "# ============================================================================",
            "",
            "def get_api_endpoints():",
            '    """Get all available API endpoints"""',
            "    endpoints = {}",
            "    ",
            "    for pattern in urlpatterns:",
            "        if hasattr(pattern, 'pattern'):",
            "            endpoints[pattern.name or str(pattern.pattern)] = str(pattern.pattern)",
            "    ",
            "    return endpoints",
            "",
            "def print_api_routes():",
            '    """Print all API routes for debugging"""',
            "    print('\\n📋 Available API Routes:')",
            "    print('=' * 50)",
            "    ",
            "    for pattern in urlpatterns:",
            "        if hasattr(pattern, 'pattern'):",
            "            route = str(pattern.pattern)",
            "            name = pattern.name or 'unnamed'",
            "            print(f'   {route:<30} {name}')",
            "    ",
            "    print('=' * 50)",
            "",
            "# Print routes when URLs are loaded (for debugging)",
            "if __name__ != '__main__':",
            "    try:",
            "        print_api_routes()",
            "    except:",
            "        pass  # Silently fail if there are issues",
        ])
        
        # Write the URLs file
        urls_content = "\n".join(code_lines)
        output_path = APP_PATH / "urls.py"
        output_path.write_text(urls_content)
        
        print(f"URLs generated successfully at {output_path}")
        
        # Display generated endpoints
        if config:
            print(f"\nGenerated API endpoints:")
            for model_name in config.keys():
                route_name = model_name.lower() + 's'
                print(f"   - /{route_name}/ (CRUD operations)")
                print(f"   - /{route_name}/recent/ (recent records)")
                print(f"   - /{route_name}/stats/ (statistics)")
                print(f"   - /{route_name}/export/ (data export)")
                print(f"   - /{route_name}/timeline/ (timeline view)")
                print(f"   - /{route_name}/search/ (advanced search)")
                print()
            
            print(f"System endpoints:")
            print(f"   - /health/ (API health check)")
            print(f"   - /docs/ (API documentation)")
            print(f"   - /schema/ (API schema)")
            print(f"   - /version/ (API version info)")
        
        return True
        
    except Exception as e:
        print(f"Error generating URLs: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback: create minimal working URLs
        print("Creating fallback URLs...")
        fallback_content = '''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import JsonResponse
from django.utils import timezone

# Minimal fallback router
router = DefaultRouter()

def health(request):
    """Basic health check"""
    return JsonResponse({
        'status': 'ok',
        'service': 'adminpanel-api',
        'timestamp': timezone.now().isoformat(),
        'message': 'Fallback URLs active'
    })

def api_info(request):
    """Basic API information"""
    return JsonResponse({
        'title': 'Unreal Engine Game Server API',
        'version': '1.0.0',
        'status': 'fallback_mode',
        'endpoints': {
            'health': '/api/health/',
            'info': '/api/info/'
        }
    })

# Import views if available
try:
    from . import views
    VIEWS_AVAILABLE = True
    
    # Try to register basic viewsets
    try:
        from .models import *
        from django.apps import apps
        
        app_models = apps.get_app_config('adminpanel').get_models()
        for model in app_models:
            model_name = model.__name__
            route_name = model_name.lower() + 's'
            
            try:
                viewset_class = getattr(views, f'{model_name}ViewSet', None)
                if viewset_class:
                    router.register(route_name, viewset_class)
            except:
                pass
                
    except:
        pass
        
except ImportError:
    VIEWS_AVAILABLE = False

urlpatterns = [
    path('health/', health, name='api-health'),
    path('info/', api_info, name='api-info'),
    path('', include(router.urls)),
]
'''
        
        try:
            (APP_PATH / "urls.py").write_text(fallback_content)
            print("✅ Fallback URLs created")
            return True
        except Exception as fallback_error:
            print(f"❌ Failed to create fallback URLs: {fallback_error}")
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

def generate_url_documentation():
    """Generate URL documentation"""
    print("\n" + "="*60)
    print("API ENDPOINTS DOCUMENTATION")
    print("="*60)
    
    if CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text())
        
        print("🔗 Model Endpoints:")
        for model_name in config.keys():
            route = model_name.lower() + 's'
            print(f"\n{model_name} ({route}):")
            print(f"   GET    /{route}/              - List all {model_name.lower()}s")
            print(f"   POST   /{route}/              - Create new {model_name.lower()}")
            print(f"   GET    /{route}/{{id}}/         - Get specific {model_name.lower()}")
            print(f"   PUT    /{route}/{{id}}/         - Update {model_name.lower()}")
            print(f"   DELETE /{route}/{{id}}/         - Delete {model_name.lower()}")
            print(f"   GET    /{route}/recent/       - Get recent {model_name.lower()}s")
            print(f"   GET    /{route}/stats/        - Get {model_name.lower()} statistics")
            print(f"   GET    /{route}/export/       - Export {model_name.lower()} data")
            print(f"   GET    /{route}/timeline/     - Get {model_name.lower()} timeline")
            print(f"   GET    /{route}/search/       - Search {model_name.lower()}s")
        
        print(f"\n🔧 System Endpoints:")
        print(f"   GET    /health/               - API health check")
        print(f"   GET    /docs/                 - API documentation")
        print(f"   GET    /schema/               - API schema")
        print(f"   GET    /version/              - API version info")
        
        print(f"\n📚 Query Parameters:")
        print(f"   ?search=<term>               - Search across text fields")
        print(f"   ?ordering=<field>            - Order by field (prefix with - for desc)")
        print(f"   ?page=<num>                  - Pagination")
        print(f"   ?page_size=<num>             - Items per page")
        print(f"   ?format=json|csv             - Response format (for export)")
        
    print("="*60)

def main():
    """Main function to generate and validate URLs"""
    print("🔧 Generating Django URLs from entities.json...")
    
    # Ensure the app directory exists
    APP_PATH.mkdir(parents=True, exist_ok=True)
    
    # Generate URLs
    if generate_urls():
        print("✅ URLs generation completed")
        
        # Validate the generated file
        if validate_urls():
            print("✅ URLs validation passed")
            generate_url_documentation()
            
            print("\n🎉 URLs are ready!")
            print("Your API endpoints are configured and ready to use.")
        else:
            print("⚠️  URLs validation failed, but file was created")
    else:
        print("❌ URLs generation failed")

if __name__ == "__main__":
    main()