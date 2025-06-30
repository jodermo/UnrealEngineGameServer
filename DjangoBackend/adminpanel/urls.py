from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import JsonResponse

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
        pass  # PlayerViewSet not found
    try:
        router.register(r'matchs', views.MatchViewSet)
    except AttributeError:
        pass  # MatchViewSet not found
    try:
        router.register(r'items', views.ItemViewSet)
    except AttributeError:
        pass  # ItemViewSet not found
    try:
        router.register(r'guilds', views.GuildViewSet)
    except AttributeError:
        pass  # GuildViewSet not found

def api_health(request):
    """Health check endpoint with model information"""
    model_info = {}
    if VIEWS_AVAILABLE:
        try:
            from . import models
            try:
                model_info['players'] = models.Player.objects.count()
            except Exception:
                model_info['players'] = 'unavailable'
            try:
                model_info['matchs'] = models.Match.objects.count()
            except Exception:
                model_info['matchs'] = 'unavailable'
            try:
                model_info['items'] = models.Item.objects.count()
            except Exception:
                model_info['items'] = 'unavailable'
            try:
                model_info['guilds'] = models.Guild.objects.count()
            except Exception:
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
            'matchs': '/api/matchs/',
            'items': '/api/items/',
            'guilds': '/api/guilds/',
        },
        'api_docs': '/api/schema/',
        'admin_panel': '/admin/'
    })

def api_status(request):
    """Simple status endpoint"""
    return JsonResponse({'status': 'running', 'service': 'django-backend'})

urlpatterns = [
    path('health/', api_health, name='api-health'),
    path('status/', api_status, name='api-status'),
    path('', include(router.urls)),
]