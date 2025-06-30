# DjangoBackend/config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def root_status(request):
    """Simple root status endpoint"""
    return JsonResponse({
        "status": "ok",
        "message": "Backend is running",
        "available_paths": [
            "/admin/",
            "/api/",
            "/api/health/",
            "/api/status/"
        ]
    })

urlpatterns = [
    path('', root_status, name='root-status'),
    path('admin/', admin.site.urls),
    path('api/', include('adminpanel.urls')),
]
