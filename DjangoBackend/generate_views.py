import json
from pathlib import Path

# Path to the JSON configuration file defining model structures
CONFIG_PATH = Path("config/entities.json")

# Path to the Django app directory where the views.py will be written
APP_PATH = Path("DjangoBackend/adminpanel")


# Generates a Django REST Framework ViewSet for a given model name
def write_view(model_name):
    return f"""
class {model_name}ViewSet(viewsets.ModelViewSet):
    queryset = {model_name}.objects.all()
    serializer_class = {model_name}Serializer
"""


# Main function that generates views.py from the JSON config
def generate_views():
    # Read and parse the config/entities.json file
    config = json.loads(CONFIG_PATH.read_text())

    # Begin constructing the views.py file
    code = "from rest_framework import viewsets\n"
    code += "from .models import *\n"
    code += "from .serializers import *\n\n"

    # Loop over each model defined in the config and generate a view class
    for model_name in config:
        code += write_view(model_name) + "\n"

    # Write the final views.py file into the app directory
    (APP_PATH / "views.py").write_text(code)
    print("views.py generated from config!")


# Run the view generation when this script is executed directly
if __name__ == "__main__":
    generate_views()
