#!/usr/bin/env python3
"""
Generate Django REST Framework serializers from entities.json configuration
Creates comprehensive serializers with validation, nested relationships, and custom methods
"""

import json
from pathlib import Path
import re

# Configuration paths
CONFIG_PATH = Path("config/entities.json")
APP_PATH = Path("adminpanel")

def analyze_field_relationships(config):
    """Analyze relationships between models for nested serializers"""
    relationships = {}
    
    for model_name, model_config in config.items():
        relationships[model_name] = {
            'foreign_keys': [],
            'many_to_many': [],
            'reverse_relations': []
        }
        
        fields = model_config.get("fields", {})
        for field_name, field_def in fields.items():
            field_def_str = str(field_def)
            
            # Find ForeignKey relationships
            if "ForeignKey" in field_def_str:
                match = re.search(r"ForeignKey\s*\(\s*['\"]([^'\"]+)['\"]", field_def_str)
                if match:
                    related_model = match.group(1)
                    relationships[model_name]['foreign_keys'].append({
                        'field': field_name,
                        'related_model': related_model
                    })
            
            # Find ManyToManyField relationships
            if "ManyToManyField" in field_def_str:
                match = re.search(r"ManyToManyField\s*\(\s*['\"]([^'\"]+)['\"]", field_def_str)
                if match:
                    related_model = match.group(1)
                    relationships[model_name]['many_to_many'].append({
                        'field': field_name,
                        'related_model': related_model
                    })
    
    # Find reverse relationships
    for model_name in config.keys():
        for other_model, other_config in config.items():
            if other_model != model_name:
                other_fields = other_config.get("fields", {})
                for field_name, field_def in other_fields.items():
                    field_def_str = str(field_def)
                    if f"ForeignKey('{model_name}'" in field_def_str:
                        relationships[model_name]['reverse_relations'].append({
                            'field': f"{other_model.lower()}_set",
                            'related_model': other_model,
                            'source_field': field_name
                        })
    
    return relationships

def generate_basic_serializer(model_name, model_config, relationships):
    """Generate a basic model serializer"""
    serializer_options = model_config.get("serializer_options", {})
    fields = model_config.get("fields", {})
    
    code_lines = [
        f"class {model_name}Serializer(serializers.ModelSerializer):",
        f'    """',
        f'    Basic serializer for {model_name} model',
        f'    Handles standard CRUD operations with configurable depth',
        f'    """',
        ""
    ]
    
    # Add custom field definitions for relationships
    model_relationships = relationships.get(model_name, {})
    
    # Add nested serializers for ForeignKey fields (optional)
    for fk in model_relationships.get('foreign_keys', []):
        related_model = fk['related_model']
        field_name = fk['field']
        if related_model in relationships:  # Only if the related model exists in our config
            code_lines.extend([
                f"    # Nested serializer for {field_name} (uncomment to enable)",
                f"    # {field_name}_detail = {related_model}Serializer(source='{field_name}', read_only=True)",
                ""
            ])
    
    # Add custom validation methods
    validation_rules = serializer_options.get("validation", {})
    if validation_rules:
        code_lines.extend([
            "    def validate(self, data):",
            f'        """Custom validation for {model_name}"""',
        ])
        
        for field_name, rule in validation_rules.items():
            code_lines.append(f"        # Validate {field_name}: {rule}")
        
        code_lines.extend([
            "        return data",
            ""
        ])
    
    # Add field-specific validation methods
    for field_name, field_def in fields.items():
        field_def_str = str(field_def)
        if "EmailField" in field_def_str:
            code_lines.extend([
                f"    def validate_{field_name}(self, value):",
                f"        \"\"\"Validate {field_name} field\"\"\"",
                f"        if value and not '@' in value:",
                f"            raise serializers.ValidationError('Invalid email format')",
                f"        return value",
                ""
            ])
        elif "unique=True" in field_def_str and "CharField" in field_def_str:
            code_lines.extend([
                f"    def validate_{field_name}(self, value):",
                f"        \"\"\"Validate uniqueness of {field_name}\"\"\"",
                f"        if value:",
                f"            # Add custom uniqueness validation if needed",
                f"            pass",
                f"        return value",
                ""
            ])
    
    # Add custom create method
    code_lines.extend([
        "    def create(self, validated_data):",
        f'        """Custom create method for {model_name}"""',
        "        # Handle nested relationships if needed",
        f"        return {model_name}.objects.create(**validated_data)",
        ""
    ])
    
    # Add custom update method
    code_lines.extend([
        "    def update(self, instance, validated_data):",
        f'        """Custom update method for {model_name}"""',
        "        # Handle nested relationships if needed",
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
    ])
    
    # Handle field configuration
    exclude_fields = serializer_options.get("exclude", [])
    include_fields = serializer_options.get("include", None)
    read_only_fields = serializer_options.get("read_only", [])
    write_only_fields = serializer_options.get("write_only", [])
    
    if include_fields:
        code_lines.append(f"        fields = {include_fields}")
    elif exclude_fields:
        code_lines.append(f"        fields = '__all__'")
        code_lines.append(f"        exclude = {exclude_fields}")
    else:
        code_lines.append(f"        fields = '__all__'")
    
    # Add depth for nested relationships
    depth = serializer_options.get("depth", 1)
    if depth > 0:
        code_lines.append(f"        depth = {depth}")
    
    # Add read-only fields
    if read_only_fields:
        code_lines.append(f"        read_only_fields = {read_only_fields}")
    
    # Add extra kwargs for write-only fields
    if write_only_fields:
        code_lines.append(f"        extra_kwargs = {{")
        for field in write_only_fields:
            code_lines.append(f"            '{field}': {{'write_only': True}},")
        code_lines.append(f"        }}")
    
    code_lines.extend(["", ""])
    return code_lines

def generate_nested_serializer(model_name, model_config, relationships):
    """Generate nested serializer for detailed representations"""
    code_lines = [
        f"class {model_name}NestedSerializer(serializers.ModelSerializer):",
        f'    """',
        f'    Nested serializer for {model_name} with related objects',
        f'    Use for detailed views where you need related data',
        f'    """',
        ""
    ]
    
    model_relationships = relationships.get(model_name, {})
    
    # Add nested fields for all relationships
    for fk in model_relationships.get('foreign_keys', []):
        related_model = fk['related_model']
        field_name = fk['field']
        if related_model in relationships:
            code_lines.append(f"    {field_name} = {related_model}Serializer(read_only=True)")
    
    for m2m in model_relationships.get('many_to_many', []):
        related_model = m2m['related_model']
        field_name = m2m['field']
        if related_model in relationships:
            code_lines.append(f"    {field_name} = {related_model}Serializer(many=True, read_only=True)")
    
    # Add reverse relationships
    for reverse_rel in model_relationships.get('reverse_relations', []):
        field_name = reverse_rel['field']
        related_model = reverse_rel['related_model']
        code_lines.append(f"    {field_name} = {related_model}Serializer(many=True, read_only=True)")
    
    if any([
        model_relationships.get('foreign_keys'),
        model_relationships.get('many_to_many'),
        model_relationships.get('reverse_relations')
    ]):
        code_lines.append("")
    
    code_lines.extend([
        "    class Meta:",
        f"        model = {model_name}",
        "        fields = '__all__'",
        "        depth = 0  # Explicit depth to avoid infinite recursion",
        "",
        ""
    ])
    
    return code_lines

def generate_list_serializer(model_name, model_config):
    """Generate lightweight serializer for list views"""
    fields = model_config.get("fields", {})
    
    # Determine key fields for list view
    list_fields = ['id']
    for field_name, field_def in fields.items():
        field_def_str = str(field_def)
        # Include important fields but avoid heavy relationships
        if any(field_type in field_def_str for field_type in ['CharField', 'EmailField', 'BooleanField']):
            if 'unique=True' in field_def_str or field_name in ['name', 'title', 'username', 'email', 'status']:
                list_fields.append(field_name)
        elif "DateTimeField" in field_def_str and any(date_field in field_name for date_field in ['created', 'updated', 'modified']):
            list_fields.append(field_name)
    
    code_lines = [
        f"class {model_name}ListSerializer(serializers.ModelSerializer):",
        f'    """',
        f'    Lightweight serializer for {model_name} list views',
        f'    Optimized for performance with minimal fields',
        f'    """',
        "",
        "    class Meta:",
        f"        model = {model_name}",
        f"        fields = {list_fields[:6]}  # Limit to 6 most important fields",
        "        read_only_fields = ['id']",
        "",
        ""
    ]
    
    return code_lines

def generate_create_update_serializer(model_name, model_config):
    """Generate serializer optimized for create/update operations"""
    fields = model_config.get("fields", {})
    
    # Determine writable fields
    writable_fields = []
    readonly_fields = ['id']
    
    for field_name, field_def in fields.items():
        field_def_str = str(field_def)
        if 'auto_now' in field_def_str or 'auto_now_add' in field_def_str:
            readonly_fields.append(field_name)
        else:
            writable_fields.append(field_name)
    
    code_lines = [
        f"class {model_name}CreateUpdateSerializer(serializers.ModelSerializer):",
        f'    """',
        f'    Serializer optimized for {model_name} create/update operations',
        f'    Excludes auto-generated fields and focuses on user input',
        f'    """',
        ""
    ]
    
    # Add validation for required relationships
    for field_name, field_def in fields.items():
        field_def_str = str(field_def)
        if "ForeignKey" in field_def_str and "null=True" not in field_def_str:
            code_lines.extend([
                f"    def validate_{field_name}(self, value):",
                f"        \"\"\"Validate required {field_name} relationship\"\"\"",
                f"        if not value:",
                f"            raise serializers.ValidationError('{field_name} is required')",
                f"        return value",
                ""
            ])
    
    code_lines.extend([
        "    class Meta:",
        f"        model = {model_name}",
        f"        fields = '__all__'",
        f"        read_only_fields = {readonly_fields}",
        "",
        ""
    ])
    
    return code_lines

def generate_serializers():
    """Generate comprehensive Django REST Framework serializers"""
    try:
        # Load configuration
        if CONFIG_PATH.exists():
            config = json.loads(CONFIG_PATH.read_text())
            print(f"Loaded configuration with {len(config)} models")
        else:
            print("No entities.json found, cannot generate serializers")
            return False
        
        # Analyze relationships
        relationships = analyze_field_relationships(config)
        
        # Start building the serializers file
        code_lines = [
            "from rest_framework import serializers",
            "from django.contrib.auth.models import User",
            "from .models import *",
            "",
            "# Auto-generated Serializers from entities.json config",
            "# Generated by: DjangoBackend/generate_serializers.py",
            "",
            "# ============================================================================",
            "# BASIC SERIALIZERS",
            "# ============================================================================",
            ""
        ]
        
        # Generate basic serializers for each model
        for model_name, model_config in config.items():
            basic_serializer = generate_basic_serializer(model_name, model_config, relationships)
            code_lines.extend(basic_serializer)
        
        # Generate specialized serializers
        code_lines.extend([
            "# ============================================================================",
            "# LIST SERIALIZERS (Optimized for list views)",
            "# ============================================================================",
            ""
        ])
        
        for model_name, model_config in config.items():
            list_serializer = generate_list_serializer(model_name, model_config)
            code_lines.extend(list_serializer)
        
        code_lines.extend([
            "# ============================================================================",
            "# NESTED SERIALIZERS (With related objects)",
            "# ============================================================================",
            ""
        ])
        
        for model_name, model_config in config.items():
            nested_serializer = generate_nested_serializer(model_name, model_config, relationships)
            code_lines.extend(nested_serializer)
        
        code_lines.extend([
            "# ============================================================================",
            "# CREATE/UPDATE SERIALIZERS (Optimized for forms)",
            "# ============================================================================",
            ""
        ])
        
        for model_name, model_config in config.items():
            create_update_serializer = generate_create_update_serializer(model_name, model_config)
            code_lines.extend(create_update_serializer)
        
        # Add utility functions
        code_lines.extend([
            "# ============================================================================",
            "# UTILITY FUNCTIONS",
            "# ============================================================================",
            "",
            "def get_serializer_for_model(model_name, serializer_type='basic'):",
            '    """Get appropriate serializer class for a model"""',
            "    serializers_map = {",
        ])
        
        for model_name in config.keys():
            code_lines.extend([
                f"        '{model_name.lower()}': {{",
                f"            'basic': {model_name}Serializer,",
                f"            'list': {model_name}ListSerializer,",
                f"            'nested': {model_name}NestedSerializer,",
                f"            'create_update': {model_name}CreateUpdateSerializer,",
                f"        }},",
            ])
        
        code_lines.extend([
            "    }",
            "    ",
            "    model_serializers = serializers_map.get(model_name.lower(), {})",
            "    return model_serializers.get(serializer_type)",
            "",
            "def get_all_serializers():",
            '    """Get all available serializers"""',
            "    return {",
        ])
        
        for model_name in config.keys():
            code_lines.append(f"        '{model_name}': {model_name}Serializer,")
        
        code_lines.extend([
            "    }",
        ])
        
        # Write the serializers file
        serializers_content = "\n".join(code_lines)
        output_path = APP_PATH / "serializers.py"
        output_path.write_text(serializers_content)
        
        print(f"Serializers generated successfully at {output_path}")
        
        # Display generated serializers
        print(f"\nGenerated serializers:")
        for model_name in config.keys():
            rel_info = relationships.get(model_name, {})
            fk_count = len(rel_info.get('foreign_keys', []))
            m2m_count = len(rel_info.get('many_to_many', []))
            reverse_count = len(rel_info.get('reverse_relations', []))
            
            print(f"   - {model_name}Serializer (basic)")
            print(f"   - {model_name}ListSerializer (optimized)")
            print(f"   - {model_name}NestedSerializer (with relations)")
            print(f"   - {model_name}CreateUpdateSerializer (forms)")
            
            if fk_count + m2m_count + reverse_count > 0:
                print(f"     → Relations: {fk_count} FK, {m2m_count} M2M, {reverse_count} reverse")
            print()
        
        return True
        
    except Exception as e:
        print(f"Error generating serializers: {e}")
        import traceback
        traceback.print_exc()
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

def main():
    """Main function to generate and validate serializers"""
    print("🔧 Generating Django REST Framework serializers from entities.json...")
    
    # Ensure the app directory exists
    APP_PATH.mkdir(parents=True, exist_ok=True)
    
    # Generate serializers
    if generate_serializers():
        print("✅ Serializers generation completed")
        
        # Validate the generated file
        if validate_serializers():
            print("✅ Serializers validation passed")
            
            print("\n🎉 Serializers are ready!")
            print("Available serializer types for each model:")
            print("   - Basic: Standard CRUD operations")
            print("   - List: Optimized for list views")
            print("   - Nested: Includes related objects")
            print("   - CreateUpdate: Optimized for forms")
        else:
            print("⚠️  Serializers validation failed, but file was created")
    else:
        print("❌ Serializers generation failed")

if __name__ == "__main__":
    main()