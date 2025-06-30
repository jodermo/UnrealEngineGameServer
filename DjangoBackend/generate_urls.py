from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import JsonResponse

# Import views safely - only if they exist
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
        router.register(r'matches', views.MatchViewSet)
    except AttributeError:
        pass  # MatchViewSet not found

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
        except ImportError:
            pass

    return JsonResponse({
        'status': 'ok',
        'views_available': VIEWS_AVAILABLE,
        'configured_models': ['Player', 'Match'],
        'model_counts': model_info,
        'endpoints': {
            'players': '/api/players/',
            'matches': '/api/matches/',
        }
    })

urlpatterns = [
    path('health/', api_health, name='api-health'),
    path('', include(router.urls)),
]