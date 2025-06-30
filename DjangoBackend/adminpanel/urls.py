import json
from pathlib import Path

# Path to the JSON config file that defines your Django models
CONFIG_PATH = Path("config/entities.json")

# Path to the Django app where the generated urls.py will be saved
APP_PATH = Path("DjangoBackend/adminpanel")


# Convert PascalCase or camelCase to snake_case
def snake(name):
    return "".join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip("_")


# Simple pluralizer to make route names like player → players or category → categories
def plural(name):
    if name.endswith("y") and name[-2] not in "aeiou":
        return name[:-1] + "ies"
    elif name.endswith("s"):
        return name + "es"
    else:
        return name + "s"


# Generate the Django URL routing code using DRF routers
def write_urls(config):
    code = [
        "from django.urls import path, include",
        "from rest_framework.routers import DefaultRouter",
        "from . import views\n",  # Import all views
        "router = DefaultRouter()"  # Initialize DRF's default router
    ]

    # Register each model's ViewSet to a route
    for model_name in config:
        route = plural(snake(model_name).lower())  # Convert to plural snake_case for the endpoint
        code.append(f"router.register(r'{route}', views.{model_name}ViewSet)")

    # Final URL patterns using the router
    code.append("\nurlpatterns = [")
    code.append("    path('', include(router.urls)),")
    code.append("]")

    return "\n".join(code)


# Main function to generate urls.py from the JSON config
def generate_urls():
    config = json.loads(CONFIG_PATH.read_text())  # Read and parse the JSON config
    urls_code = write_urls(config)  # Generate the URL routing code
    (APP_PATH / "urls.py").write_text(urls_code)  # Write to urls.py file in the app
    print("✅ urls.py generated from config!")


# Execute the script if run directly
if __name__ == "__main__":
    generate_urls()
