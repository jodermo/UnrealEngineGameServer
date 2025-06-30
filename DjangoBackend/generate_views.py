#!/usr/bin/env python3
"""
Generate Django REST Framework ViewSets from entities.json
Creates views.py with model-specific ViewSets for automatic API exposure
"""

import json
from pathlib import Path

CONFIG_PATH = Path("config/entities.json")
APP_PATH = Path("adminpanel")


def generate_views():
    """Generate DRF ViewSets for each model from entities.json"""
    if not CONFIG_PATH.exists():
        print("entities.json not found.")
        return False

    try:
        config = json.loads(CONFIG_PATH.read_text())
        print(f"Loaded configuration with {len(config)} models")

        lines = [
            "from rest_framework import viewsets",
            "from rest_framework.response import Response",
            "from rest_framework.decorators import action",
            "from .models import *",
            "from .serializers import *",
            "",
            "# Auto-generated ViewSets from entities.json",
            ""
        ]

        for model_name, model_config in config.items():
            lc_name = model_name.lower()
            viewset_class = f"{model_name}ViewSet"
            base_serializer = f"{model_name}Serializer"
            create_update_serializer = f"{model_name}CreateUpdateSerializer"
            list_serializer = f"{model_name}ListSerializer"

            lines.extend([
                f"class {viewset_class}(viewsets.ModelViewSet):",
                f"    \"\"\"ViewSet for {model_name} model\"\"\"",
                f"    queryset = {model_name}.objects.all()",
                f"    serializer_class = {base_serializer}",
                "",
                f"    def get_serializer_class(self):",
                f"        if self.action in ['create', 'update', 'partial_update']:",
                f"            return {create_update_serializer}",
                f"        elif self.action == 'list':",
                f"            return {list_serializer}",
                f"        return {base_serializer}",
                ""
            ])

            # Add custom actions
            lines.extend([
                f"    @action(detail=False)",
                f"    def recent(self, request):",
                f"        recent = self.queryset.order_by('-id')[:10]",
                f"        serializer = self.get_serializer(recent, many=True)",
                f"        return Response(serializer.data)",
                "",
                f"    @action(detail=False)",
                f"    def stats(self, request):",
                f"        return Response({{'count': self.queryset.count()}})",
                "",
                f"    @action(detail=False)",
                f"    def export(self, request):",
                f"        data = self.get_serializer(self.queryset, many=True).data",
                f"        return Response(data)",
                "",
                f"    @action(detail=False)",
                f"    def timeline(self, request):",
                f"        return Response(self.get_serializer(self.queryset.order_by('id'), many=True).data)",
                "",
                f"    @action(detail=False)",
                f"    def search(self, request):",
                f"        term = request.query_params.get('q', '')",
                f"        results = self.queryset.filter(id__icontains=term)",
                f"        return Response(self.get_serializer(results, many=True).data)",
                "",
            ])

        # Write the views.py file
        output_path = APP_PATH / "views.py"
        output_path.write_text("\n".join(lines))
        print(f"ViewSets generated at {output_path}")
        return True

    except Exception as e:
        print(f"Error generating views: {e}")
        return False


def validate_views():
    """Validate generated views.py file"""
    views_path = APP_PATH / "views.py"
    if not views_path.exists():
        print("views.py does not exist.")
        return False

    try:
        compile(views_path.read_text(), str(views_path), 'exec')
        print("views.py is valid.")
        return True
    except SyntaxError as e:
        print(f"Syntax error in views.py: {e}")
        return False
    except Exception as e:
        print(f"Error validating views.py: {e}")
        return False


def main():
    print("🔧 Generating Django ViewSets from entities.json...")
    APP_PATH.mkdir(parents=True, exist_ok=True)
    if generate_views():
        if validate_views():
            print("✅ Views generation and validation completed.")
        else:
            print("⚠️ Views generated, but validation failed.")
    else:
        print("❌ Views generation failed.")


if __name__ == "__main__":
    main()
