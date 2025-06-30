from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter
from django.http import JsonResponse
import os

# Import views safely
try:
    from . import views
    VIEWS_AVAILABLE = True
except ImportError:
    VIEWS_AVAILABLE = False

router = DefaultRouter()

# Register ViewSets if views are available
if VIEWS_AVAILABLE:
    try:
        router.register(r'players', views.PlayerViewSet)
    except AttributeError:
        pass
    try:
        router.register(r'matches', views.MatchViewSet)
    except AttributeError:
        pass
    try:
        router.register(r'items', views.ItemViewSet)
    except AttributeError:
        pass
    try:
        router.register(r'guilds', views.GuildViewSet)
    except AttributeError:
        pass

def api_health(request):
    model_info = {}
    if VIEWS_AVAILABLE:
        try:
            from . import models
            try:
                model_info['players'] = models.Player.objects.count()
            except:
                model_info['players'] = 'unavailable'
            try:
                model_info['matches'] = models.Match.objects.count()
            except:
                model_info['matches'] = 'unavailable'
            try:
                model_info['items'] = models.Item.objects.count()
            except:
                model_info['items'] = 'unavailable'
            try:
                model_info['guilds'] = models.Guild.objects.count()
            except:
                model_info['guilds'] = 'unavailable'
        except ImportError:
            pass

    return JsonResponse({
        'status': 'ok',
        'service': 'django-backend',
        'views_available': VIEWS_AVAILABLE,
        'configured_models': ['Player', 'Match', 'Item', 'Guild'],
        'model_counts': model_info,
        'endpoints': {
            'players': '/api/players/',
            'matches': '/api/matches/',
            'items': '/api/items/',
            'guilds': '/api/guilds/',
        },
        'api_docs': '/api/schema/',
        'admin_panel': '/admin/'
    })

def serve_index(request):
    """Serve index.html from www directory"""
    try:
        from pathlib import Path
        index_path = Path(settings.BASE_DIR) / 'www' / 'index.html'
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return HttpResponse(content, content_type='text/html')
        else:
            # Fallback HTML if index.html doesn't exist
            fallback_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Unreal Engine Game Server</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #333; border-bottom: 3px solid #007cba; padding-bottom: 10px; }
                    .api-link { display: inline-block; margin: 10px; padding: 12px 20px; background: #007cba; color: white; text-decoration: none; border-radius: 5px; }
                    .api-link:hover { background: #005a8b; }
                    .status { color: #28a745; font-weight: bold; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎮 Unreal Engine Game Server</h1>
                    <p class="status">✅ Django Backend Running</p>
                    <h2>Available Endpoints:</h2>
                    <a href="/api/health/" class="api-link">API Health</a>
                    <a href="/api/players/" class="api-link">Players</a>
                    <a href="/api/matches/" class="api-link">Matches</a>
                    <a href="/api/items/" class="api-link">Items</a>
                    <a href="/api/guilds/" class="api-link">Guilds</a>
                    <a href="/admin/" class="api-link">Admin Panel</a>
                    <a href="/api/schema/" class="api-link">API Docs</a>
                    
                    <h2>Quick Start:</h2>
                    <ul>
                        <li>API available at: <code>/api/</code></li>
                        <li>Admin panel: <code>/admin/</code></li>
                        <li>API documentation: <code>/api/schema/</code></li>
                    </ul>
                    
                    <p><em>To customize this page, create www/index.html</em></p>
                </div>
            </body>
            </html>
            """
            return HttpResponse(fallback_html, content_type='text/html')
    except Exception as e:
        return HttpResponse(f'Error serving index: {e}', status=500)

urlpatterns = [
    # Root URL serves index.html from www directory
    path('', serve_index, name='index'),
    
    # API endpoints
    path('api/health/', api_health, name='api-health'),
    path('api/', include(router.urls)),
    
    # Admin
    path('admin/', include('django.contrib.admin.urls')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Serve files from www directory at root (except for already defined URLs)
    from django.views.static import serve
    from django.urls import re_path
    
    def serve_www_files(request, path):
        """Serve files from www directory"""
        from pathlib import Path
        import mimetypes
        
        try:
            file_path = Path(settings.BASE_DIR) / 'www' / path
            if file_path.exists() and file_path.is_file():
                content_type, _ = mimetypes.guess_type(str(file_path))
                with open(file_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type=content_type)
                    return response
        except Exception:
            pass
        
        from django.http import Http404
        raise Http404("File not found")
    
    # Add catch-all pattern for www files (this should be last)
    urlpatterns += [
        re_path(r'^(?P<path>.*)$', serve_www_files, name='www-files'),
    ]