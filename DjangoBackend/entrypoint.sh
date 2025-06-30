#!/bin/bash
set -e  # Exit immediately if a command fails

# Wait for the PostgreSQL database to be ready
echo "Waiting for database..."
until pg_isready -h ue-database -p 5432 -U "$DB_USER" > /dev/null 2>&1; do
  sleep 1
done
echo "Database is ready."

# Auto-generate Django components if those scripts exist
if [ -f generate_components.py ]; then
  echo "Generating Django models, serializers, views, and URLs from config..."
  python generate_components.py || true
fi

if [ -f generate_views.py ]; then
  python generate_views.py || true
fi

if [ -f generate_urls.py ]; then
  python generate_urls.py || true
fi

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
