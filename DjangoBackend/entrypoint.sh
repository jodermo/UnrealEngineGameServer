#!/bin/bash
set -e  # Exit immediately if a command fails

# Wait for the PostgreSQL database to be ready
echo "Waiting for database..."
until pg_isready -h ue-database -p 5432 -U "$DB_USER"; do
  echo "Waiting for PostgreSQL at ue-database:5432 as user $DB_USER"
  sleep 1
done
echo "Database is ready."

# Create a minimal working URLs file first
echo "Creating minimal URLs file..."
cat > adminpanel/urls.py << 'EOF'
from django.urls import path
from django.http import JsonResponse

def health(request):
    return JsonResponse({'status': 'ok', 'service': 'adminpanel'})

urlpatterns = [
    path('health/', health, name='health'),
]
EOF

# Auto-generate Django components if those scripts exist
if [ -f generate_components.py ]; then
  echo "Generating admin..."
  python generate_components.py || true
fi

if [ -f generate_models.py ]; then
  echo "Generating models..."
  python generate_models.py || true
fi

if [ -f generate_views.py ]; then
  echo "Generating views..."
  python generate_views.py || true
fi


if [ -f generate_urls.py ]; then
  echo "Generating URLs..."
  python generate_urls.py || true
fi

if [ -f generate_serializers.py ]; then
  echo "Generating Serializers..."
  python generate_serializers.py || true
fi


# Generate URLs after other components
echo "Generating URLs..."
python -c "
import json
from pathlib import Path

CONFIG_PATH = Path('config/entities.json')
APP_PATH = Path('adminpanel')

try:
    if CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text())
        
        # Generate URLs content
        urls_content = '''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import JsonResponse

router = DefaultRouter()

try:
    from . import views
    VIEWS_AVAILABLE = True
except ImportError:
    VIEWS_AVAILABLE = False

if VIEWS_AVAILABLE:'''

        for model_name in config.keys():
            route = model_name.lower() + 's'
            urls_content += f'''
    try:
        router.register(r'{route}', views.{model_name}ViewSet)
    except AttributeError:
        pass'''

        urls_content += '''

def api_health(request):
    return JsonResponse({
        'status': 'ok',
        'views_available': VIEWS_AVAILABLE,
        'models': list(''' + str(list(config.keys())) + ''')
    })

urlpatterns = [
    path('health/', api_health, name='api-health'),
    path('', include(router.urls)),
]'''
        
        (APP_PATH / 'urls.py').write_text(urls_content)
        print('URLs generated successfully')
    else:
        print('No config file found, keeping minimal URLs')
except Exception as e:
    print(f'URL generation failed: {e}')
"

# Run migrations
echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Optionally create superuser
if [ "$CREATE_SUPERUSER" = "1" ]; then
  echo "Creating Django superuser..."
  python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
username = "${DJANGO_SUPERUSER_USERNAME}"
email = "${DJANGO_SUPERUSER_EMAIL}"
password = "${DJANGO_SUPERUSER_PASSWORD}"
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
EOF
fi

# Start Django server
echo "Starting Django development server on http://0.0.0.0:8000"
exec python manage.py runserver 0.0.0.0:8000