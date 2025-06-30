#!/usr/bin/env python3
"""
Generate Django REST Framework serializers from entities.json configuration
"""

import json
from pathlib import Path

# Configuration paths
CONFIG_PATH = Path("config/entities.json")
APP_PATH = Path("adminpanel")

def generate_serializers():
    """Generate Django REST Framework serializers based on entities.json"""
    try:
        # Load configuration
        if CONFIG_PATH.exists():
            config = json.loads(CONFIG_PATH.read_text())
            print(f"Loaded configuration with {len(config)} models")
        else:
            print("No entities.json found, cannot generate serializers")
            return False
        
        # Start building the serializers file
        code_lines = [
            "from rest_framework import serializers",
            "from .models import *",
            "",
            "# Auto-generated Serializers from entities.json config",
            ""
        ]
        
        # Generate serializer for each model
        for model_name, model_config in config.items():
            serializer_options = model_config.get("serializer_options", {})
            depth = serializer_options.get("depth", 1)
            exclude_fields = serializer_options.get("exclude", [])
            include_fields = serializer_options.get("include", None)
            read_only_fields = serializer_options.get("read_only", [])
            write_only_fields = serializer_options.get("write_only", [])
            
            # Start serializer class
            code_lines.extend([
                f"class {model_name}Serializer(serializers.ModelSerializer):",
                "    class Meta:",
                f"        model = {model_name}",
            ])
            
            # Handle field selection
            if include_fields:
                code_lines.append(f"        fields = {include_fields}")
            elif exclude_fields:
                code_lines.append(f"        fields = '__all__'")
                code_lines.append(f"        exclude = {exclude_fields}")
            else:
                code_lines.append(f"        fields = '__all__'")
            
            # Add depth for nested relationships
            if depth > 0:
                code_lines.append(f"        depth = {depth}")
            
            # Add read-only fields
            if read_only_fields:
                code_lines.append(f"        read_only_fields = {read_only_fields}")
            
            # Add write-only fields
            if write_only_fields:
                code_lines.append(f"        extra_kwargs = {{")
                for field in write_only_fields:
                    code_lines.append(f"            '{field}': {{'write_only': True}},")
                code_lines.append(f"        }}")
            
            code_lines.append("")
        
        # Add custom serializer methods if needed
        for model_name, model_config in config.items():
            fields = model_config.get("fields", {})
            has_foreign_keys = any("ForeignKey" in str(field_def) for field_def in fields.values())
            has_many_to_many = any("ManyToManyField" in str(field_def) for field_def in fields.values())
            
            if has_foreign_keys or has_many_to_many:
                # Add nested serializer example
                code_lines.extend([
                    f"# Custom nested serializer for {model_name} (optional)",
                    f"# class {model_name}NestedSerializer(serializers.ModelSerializer):",
                    f"#     class Meta:",
                    f"#         model = {model_name}",
                    f"#         fields = '__all__'",
                    f"#         depth = 0  # No nesting for this version",
                    ""
                ])
        
        # Write the serializers file
        serializers_content = "\n".join(code_lines)
        output_path = APP_PATH / "serializers.py"
        output_path.write_text(serializers_content)
        
        print(f"Serializers generated successfully at {output_path}")
        
        # Display generated serializers
        print(f"Generated serializers:")
        for model_name in config.keys():
            print(f"   - {model_name}Serializer")
        
        return True
        
    except Exception as e:
        print(f"Error generating serializers: {e}")
        return False

def validate_serializers():
    """Validate the generated serializers file"""
    serializers_path = APP_PATH / "serializers.py"
    
    if not serializers_path.exists():
        print("serializers.py does not exist")
        return False
    
    try:
        # Try to compile the serializers file
        content = serializers_path.read_text()
        compile(content, str(serializers_path), 'exec')
        print("Serializers file syntax is valid")
        return True
    except SyntaxError as e:
        print(f"Syntax error in serializers.py: {e}")
        return False
    except Exception as e:
        print(f"Error validating serializers.py: {e}")
        return False

def generate_advanced_serializers():
    """Generate advanced serializers with custom fields and validation"""
    try:
        if CONFIG_PATH.exists():
            config = json.loads(CONFIG_PATH.read_text())
        else:
            print("No entities.json found")
            return False
        
        code_lines = [
            "from rest_framework import serializers",
            "from django.contrib.auth.models import User",
            "from .models import *",
            "",
            "# Advanced auto-generated Serializers with custom validation",
            ""
        ]
        
        for model_name, model_config in config.items():
            fields = model_config.get("fields", {})
            serializer_options = model_config.get("serializer_options", {})
            
            code_lines.extend([
                f"class {model_name}Serializer(serializers.ModelSerializer):",
                "    \"\"\"",
                f"    Serializer for {model_name} model with custom validation",
                "    \"\"\"",
                ""
            ])
            
            # Add custom field definitions for foreign keys
            for field_name, field_def in fields.items():
                if "ForeignKey" in str(field_def):
                    related_model = field_def.split("'")[1] if "'" in field_def else field_name.title()
                    code_lines.extend([
                        f"    # Custom field for {field_name} relationship",
                        f"    # {field_name}_detail = {related_model}Serializer(source='{field_name}', read_only=True)",
                        ""
                    ])
            
            # Add validation methods
            code_lines.extend([
                "    def validate(self, data):",
                "        \"\"\"",
                f"        Custom validation for {model_name}",
                "        \"\"\"",
                "        # Add your custom validation logic here",
                "        return data",
                "",
                "    def create(self, validated_data):",
                "        \"\"\"",
                f"        Custom create method for {model_name}",
                "        \"\"\"",
                f"        return {model_name}.objects.create(**validated_data)",
                "",
                "    def update(self, instance, validated_data):",
                "        \"\"\"",
                f"        Custom update method for {model_name}",
                "        \"\"\"",
                "        for attr, value in validated_data.items():",
                "            setattr(instance, attr, value)",
                "        instance.save()",
                "        return instance",
                ""
            ])
            
            # Meta class
            code_lines.extend([
                "    class Meta:",
                f"        model = {model_name}",
                "        fields = '__all__'",
            ])
            
            # Add serializer options
            if serializer_options.get("exclude"):
                code_lines.append(f"        exclude = {serializer_options['exclude']}")
            if serializer_options.get("read_only"):
                code_lines.append(f"        read_only_fields = {serializer_options['read_only']}")
            if serializer_options.get("depth", 0) > 0:
                code_lines.append(f"        depth = {serializer_options['depth']}")
            
            code_lines.extend(["", ""])
        
        # Write advanced serializers
        advanced_content = "\n".join(code_lines)
        advanced_path = APP_PATH / "advanced_serializers.py"
        advanced_path.write_text(advanced_content)
        
        print(f"Advanced serializers generated at {advanced_path}")
        return True
        
    except Exception as e:
        print(f"Error generating advanced serializers: {e}")
        return False

def main():
    """Main function to generate serializers"""
    print("Generating Django REST Framework serializers from entities.json...")
    
    # Ensure the app directory exists
    APP_PATH.mkdir(parents=True, exist_ok=True)
    
    # Generate basic serializers
    if generate_serializers():
        print("Basic serializers generation completed")
        
        # Validate the generated file
        if validate_serializers():
            print("Serializers validation passed")
            
            # Ask if user wants advanced serializers
            print("Basic serializers created successfully!")
            print("Run with --advanced flag to generate advanced serializers with custom validation")
        else:
            print("Serializers validation failed, but file was created")
    else:
        print("Serializers generation failed")

if __name__ == "__main__":
    import sys
    
    if "--advanced" in sys.argv:
        print("Generating advanced serializers...")
        generate_advanced_serializers()
    else:
        main()