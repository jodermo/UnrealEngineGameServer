import os

INSTALLED_APPS = [
    'rest_framework',  # Django REST Framework for APIs
    'adminpanel',      # Your custom admin app
    'django.contrib.admin',  # Optional: if using Django admin
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'uegame'),  # Default fallback values
        'USER': os.getenv('DB_USER', 'admin'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'securepassword'),
        'HOST': 'ue-database',  # Service name from docker-compose
        'PORT': '5432',
    }
}
