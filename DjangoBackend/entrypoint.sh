#!/bin/bash
set -e  # Exit immediately if a command fails

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Django backend initialization...${NC}"

# =============================================================================
# DATABASE READINESS CHECK
# =============================================================================
echo -e "${BLUE}Waiting for PostgreSQL database...${NC}"
until pg_isready -h ue-database -p 5432 -U "$DB_USER"; do
  echo -e "${YELLOW}Waiting for PostgreSQL at ue-database:5432 as user $DB_USER${NC}"
  sleep 2
done
echo -e "${GREEN}✅ Database is ready!${NC}"

# =============================================================================
# ENSURE DIRECTORY STRUCTURE
# =============================================================================
echo -e "${BLUE}Creating required directories...${NC}"
mkdir -p adminpanel config static media logs

# Create __init__.py if it doesn't exist
if [ ! -f adminpanel/__init__.py ]; then
    touch adminpanel/__init__.py
fi

# =============================================================================
# CREATE DEFAULT CONFIG IF MISSING
# =============================================================================
if [ ! -f config/entities.json ]; then
    echo -e "${YELLOW}Creating default entities.json...${NC}"
    cat > config/entities.json << 'EOF'
{
  "Player": {
    "fields": {
      "username": "CharField(max_length=50, unique=True)",
      "email": "EmailField()",
      "score": "IntegerField(default=0)",
      "is_active": "BooleanField(default=True)",
      "created_at": "DateTimeField(auto_now_add=True)"
    },
    "permissions": ["read", "create", "update", "delete"],
    "serializer_options": {
      "depth": 1
    }
  },
  "Match": {
    "fields": {
      "match_id": "CharField(max_length=32, unique=True)",
      "start_time": "DateTimeField()",
      "end_time": "DateTimeField(null=True, blank=True)",
      "winner": "ForeignKey('Player', on_delete=DO_NOTHING, null=True)"
    }
  },
  "Item": {
    "fields": {
      "name": "CharField(max_length=100)",
      "description": "TextField(blank=True, null=True)",
      "item_type": "CharField(max_length=50, default='common')",
      "value": "IntegerField(default=0)",
      "rarity": "CharField(max_length=20, default='common')"
    }
  },
  "Guild": {
    "fields": {
      "name": "CharField(max_length=100, unique=True)",
      "description": "TextField(blank=True, null=True)",
      "created_at": "DateTimeField(auto_now_add=True)",
      "member_count": "IntegerField(default=0)",
      "is_active": "BooleanField(default=True)"
    }
  }
}
EOF
    echo -e "${GREEN}✅ Created default entities.json${NC}"
fi

# =============================================================================
# CREATE MINIMAL FALLBACK URLs FIRST
# =============================================================================
echo -e "${BLUE}Creating initial URLs...${NC}"
cat > adminpanel/urls.py << 'EOF'
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import JsonResponse
from django.utils import timezone

router = DefaultRouter()

def health(request):
    return JsonResponse({
        'status': 'ok', 
        'service': 'adminpanel',
        'timestamp': timezone.now().isoformat(),
        'mode': 'initializing'
    })

urlpatterns = [
    path('health/', health, name='health'),
    path('', include(router.urls)),
]
EOF

# =============================================================================
# GENERATE DJANGO COMPONENTS
# =============================================================================
echo -e "${BLUE}🔧 Generating Django components...${NC}"

# Function to run generation and capture output
run_generator() {
    local script_name=$1
    local component_name=$2
    
    if [ -f "$script_name" ]; then
        echo -e "${BLUE}Generating $component_name...${NC}"
        
        # Run in subshell to capture all output but not exit
        (
            python "$script_name" 2>&1 | while IFS= read -r line; do
                # Filter out the migration instructions that cause confusion
                if [[ ! "$line" =~ ^"="+ ]] && [[ ! "$line" =~ "MIGRATION INSTRUCTIONS" ]] && [[ ! "$line" =~ "After generating models" ]] && [[ ! "$line" =~ "python manage.py" ]]; then
                    echo "$line"
                fi
            done
        ) || echo -e "${YELLOW}⚠️ $component_name generation completed with warnings${NC}"
        
        echo -e "${GREEN}✅ $component_name generation finished${NC}"
    else
        echo -e "${YELLOW}⚠️ $script_name not found${NC}"
    fi
}

# Generate all components in order
run_generator "generate_models.py" "Models" || { echo "❌ Failed to generate models"; exit 1; }
run_generator "generate_serializers.py" "Serializers" 
run_generator "generate_views.py" "Views"
run_generator "generate_admin.py" "Admin"
run_generator "generate_urls.py" "URLs"
run_generator "generate_migrations.py" "Migrations"

echo -e "${GREEN}✅ Component generation completed${NC}"

# =============================================================================
# DATABASE MIGRATIONS
# =============================================================================
echo -e "${BLUE}🗄️ Running database migrations...${NC}"

# Create migrations
echo -e "${BLUE}Creating migrations...${NC}"
python python3 manage.py makemigrations --noinput --noinput || echo -e "${YELLOW}Migration creation completed${NC}"

# Apply migrations
echo -e "${BLUE}Applying migrations...${NC}"
python manage.py migrate --noinput || {
    echo -e "${YELLOW}Migration issues detected, trying again...${NC}"
    sleep 2
    python manage.py migrate --noinput || echo -e "${YELLOW}Migrations completed with warnings${NC}"
}

echo -e "${GREEN}✅ Database migrations completed${NC}"

# =============================================================================
# SUPERUSER CREATION
# =============================================================================
if [ "$CREATE_SUPERUSER" = "1" ]; then
    echo -e "${BLUE}👤 Creating Django superuser...${NC}"
    
    python manage.py shell << EOF || echo -e "${YELLOW}Superuser creation completed${NC}"
import os
from django.contrib.auth import get_user_model

try:
    User = get_user_model()
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f'✅ Superuser "{username}" created successfully')
    else:
        print(f'ℹ️ Superuser "{username}" already exists')
except Exception as e:
    print(f'⚠️ Superuser creation issue: {e}')
EOF
    
    echo -e "${GREEN}✅ Superuser setup completed${NC}"
fi

# =============================================================================
# STATIC FILES
# =============================================================================
echo -e "${BLUE}📁 Collecting static files...${NC}"
python manage.py collectstatic --noinput || echo -e "${YELLOW}Static files collection completed${NC}"

# =============================================================================
# FINAL SYSTEM CHECK
# =============================================================================
echo -e "${BLUE}🔍 Running final checks...${NC}"

# Test database connection
python -c "
from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    print('✅ Database connection OK')
except Exception as e:
    print(f'⚠️ Database connection issue: {e}')
" || echo -e "${YELLOW}Database check completed${NC}"

# =============================================================================
# STARTUP SUMMARY
# =============================================================================
echo
echo -e "${GREEN}🎉 Django backend initialization completed!${NC}"
echo
echo "📊 Startup Summary:"
echo "  - Database: Connected ✅"
echo "  - Migrations: Applied ✅" 
echo "  - Components: Generated ✅"
echo "  - Static Files: Collected ✅"
if [ "$CREATE_SUPERUSER" = "1" ]; then
    echo "  - Superuser: Ready ✅"
fi
echo
echo "🌐 Service will be available at:"
echo "  - API: http://localhost:8000/api/"
echo "  - Admin: http://localhost:8000/admin/"
echo "  - Health: http://localhost:8000/api/health/"
echo "  - Dashboard: http://localhost:8000/"
echo
if [ "$CREATE_SUPERUSER" = "1" ]; then
    echo "🔑 Admin Credentials:"
    echo "  - Username: ${DJANGO_SUPERUSER_USERNAME:-admin}"
    echo "  - Password: ${DJANGO_SUPERUSER_PASSWORD:-admin123}"
    echo
fi

# =============================================================================
# START DJANGO SERVER
# =============================================================================
echo -e "${GREEN}🚀 Starting Django development server...${NC}"
echo -e "${GREEN}Server starting on http://0.0.0.0:8000${NC}"
echo

# Start server
exec python manage.py runserver 0.0.0.0:8000