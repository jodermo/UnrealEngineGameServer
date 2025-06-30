#!/usr/bin/env python3
"""
Generate Django admin configuration from entities.json
Creates admin.py with customized admin interfaces for each model
"""

import json
from pathlib import Path

# Configuration paths
CONFIG_PATH = Path("config/entities.json")
APP_PATH = Path("adminpanel")

def generate_admin():
    """Generate Django admin interfaces based on entities.json configuration"""
    try:
        # Load configuration
        if CONFIG_PATH.exists():
            config = json.loads(CONFIG_PATH.read_text())
            print(f"Loaded configuration with {len(config)} models")
        else:
            print("No entities.json found, creating basic admin")
            config = {}
        
        # Start building the admin file
        code_lines = [
            "from django.contrib import admin",
            "from .models import *",
            "",
            "# Auto-generated Admin interfaces from entities.json config",
            ""
        ]
        
        # Generate admin class for each model
        for model_name, model_config in config.items():
            fields = model_config.get("fields", {})
            admin_options = model_config.get("admin_options", {})
            
            # Determine which fields to display in list view
            list_display_fields = []
            search_fields = []
            list_filter_fields = []
            readonly_fields = []
            
            # Analyze fields to auto-configure admin
            for field_name, field_def in fields.items():
                field_def_str = str(field_def)
                
                # Add to search fields if it's a text field
                if any(field_type in field_def_str for field_type in ['CharField', 'TextField', 'EmailField']):
                    search_fields.append(field_name)
                
                # Add to list filter if it's a boolean, choice, or foreign key
                if any(field_type in field_def_str for field_type in ['BooleanField', 'ForeignKey', 'DateTimeField']):
                    list_filter_fields.append(field_name)
                
                # Add to readonly if it's an auto field
                if 'auto_now' in field_def_str or 'auto_now_add' in field_def_str:
                    readonly_fields.append(field_name)
                
                # Always include in list display (limit to first 6 fields for readability)
                if len(list_display_fields) < 6:
                    list_display_fields.append(field_name)
            
            # Always include 'id' as first field in list display
            if 'id' not in list_display_fields:
                list_display_fields.insert(0, 'id')
            
            # Apply admin options from config if provided
            if admin_options:
                list_display_fields = admin_options.get("list_display", list_display_fields)
                search_fields = admin_options.get("search_fields", search_fields)
                list_filter_fields = admin_options.get("list_filter", list_filter_fields)
                readonly_fields = admin_options.get("readonly_fields", readonly_fields)
            
            # Generate admin class
            code_lines.extend([
                f"@admin.register({model_name})",
                f"class {model_name}Admin(admin.ModelAdmin):",
                f"    \"\"\"",
                f"    Admin interface for {model_name} model",
                f"    \"\"\"",
                ""
            ])
            
            # Configure list display
            if list_display_fields:
                formatted_fields = [f"'{field}'" for field in list_display_fields[:6]]  # Limit to 6 fields
                code_lines.append(f"    list_display = [{', '.join(formatted_fields)}]")
            
            # Configure search fields
            if search_fields:
                formatted_search = [f"'{field}'" for field in search_fields[:4]]  # Limit to 4 search fields
                code_lines.append(f"    search_fields = [{', '.join(formatted_search)}]")
            
            # Configure list filters
            if list_filter_fields:
                formatted_filters = [f"'{field}'" for field in list_filter_fields[:4]]  # Limit to 4 filters
                code_lines.append(f"    list_filter = [{', '.join(formatted_filters)}]")
            
            # Configure readonly fields
            if readonly_fields:
                formatted_readonly = [f"'{field}'" for field in readonly_fields]
                code_lines.append(f"    readonly_fields = [{', '.join(formatted_readonly)}]")
            
            # Add pagination and ordering
            code_lines.extend([
                f"    list_per_page = 25",
                f"    ordering = ['-id']",
                ""
            ])
            
            # Add custom methods for foreign key relationships
            foreign_keys = [field for field, field_def in fields.items() 
                          if 'ForeignKey' in str(field_def)]
            
            if foreign_keys:
                code_lines.extend([
                    f"    # Custom methods for foreign key relationships",
                ])
                
                for fk_field in foreign_keys:
                    code_lines.extend([
                        f"    def {fk_field}_info(self, obj):",
                        f"        if obj.{fk_field}:",
                        f"            return str(obj.{fk_field})",
                        f"        return '-'",
                        f"    {fk_field}_info.short_description = '{fk_field.title()}'",
                        ""
                    ])
            
            # Add custom actions if specified in config
            actions = admin_options.get("actions", [])
            if actions:
                code_lines.extend([
                    f"    actions = {actions}",
                    ""
                ])
            
            # Add fieldsets for better organization if many fields
            if len(fields) > 6:
                basic_fields = list(fields.keys())[:4]
                advanced_fields = list(fields.keys())[4:]
                
                code_lines.extend([
                    f"    fieldsets = (",
                    f"        ('Basic Information', {{",
                    f"            'fields': {basic_fields}",
                    f"        }}),",
                    f"        ('Additional Details', {{",
                    f"            'fields': {advanced_fields},",
                    f"            'classes': ('collapse',),",
                    f"        }}),",
                    f"    )",
                    ""
                ])
            
            code_lines.append("")
        
        # Add custom admin site configuration
        code_lines.extend([
            "# Customize admin site header and title",
            "admin.site.site_header = 'Unreal Engine Game Server Admin'",
            "admin.site.site_title = 'UE Game Admin'",
            "admin.site.index_title = 'Game Server Administration'",
            "",
            "# Add custom admin actions",
            "def export_selected_as_json(modeladmin, request, queryset):",
            "    \"\"\"Export selected items as JSON\"\"\"",
            "    from django.http import JsonResponse",
            "    import json",
            "    ",
            "    data = []",
            "    for obj in queryset:",
            "        item = {}",
            "        for field in obj._meta.fields:",
            "            value = getattr(obj, field.name)",
            "            if hasattr(value, 'isoformat'):  # DateTime fields",
            "                value = value.isoformat()",
            "            item[field.name] = value",
            "        data.append(item)",
            "    ",
            "    response = JsonResponse(data, safe=False)",
            "    response['Content-Disposition'] = 'attachment; filename=\"export.json\"'",
            "    return response",
            "",
            "export_selected_as_json.short_description = 'Export selected as JSON'",
            "",
            "# Register the action globally for all models",
            "admin.site.add_action(export_selected_as_json)",
        ])
        
        # Write the admin file
        admin_content = "\n".join(code_lines)
        output_path = APP_PATH / "admin.py"
        output_path.write_text(admin_content)
        
        print(f"Admin interfaces generated successfully at {output_path}")
        
        # Display generated admin classes
        if config:
            print(f"\nGenerated admin classes:")
            for model_name in config.keys():
                print(f"   - {model_name}Admin")
            print(f"\nFeatures added:")
            print(f"   - List displays with relevant fields")
            print(f"   - Search functionality")
            print(f"   - Filtering options")
            print(f"   - Custom fieldsets for complex models")
            print(f"   - JSON export action")
            print(f"   - Custom admin site branding")
        
        return True
        
    except Exception as e:
        print(f"Error generating admin: {e}")
        
        # Fallback: create minimal admin
        print("Creating fallback admin...")
        fallback_content = '''from django.contrib import admin
from .models import *

# Fallback admin registration
# Register all models with basic admin interface

# Try to register models dynamically
try:
    from django.apps import apps
    app_models = apps.get_app_config('adminpanel').get_models()
    
    for model in app_models:
        if not admin.site.is_registered(model):
            admin.site.register(model)
            
except Exception as e:
    print(f"Could not auto-register models: {e}")

# Customize admin site
admin.site.site_header = 'Unreal Engine Game Server Admin'
admin.site.site_title = 'UE Game Admin'
admin.site.index_title = 'Game Server Administration'
'''
        
        try:
            (APP_PATH / "admin.py").write_text(fallback_content)
            print("Fallback admin created")
            return True
        except Exception as fallback_error:
            print(f"Failed to create fallback admin: {fallback_error}")
            return False

def validate_admin():
    """Validate the generated admin file"""
    admin_path = APP_PATH / "admin.py"
    
    if not admin_path.exists():
        print("admin.py does not exist")
        return False
    
    try:
        # Try to compile the admin file
        content = admin_path.read_text()
        compile(content, str(admin_path), 'exec')
        print("Admin file syntax is valid")
        return True
    except SyntaxError as e:
        print(f"Syntax error in admin.py: {e}")
        return False
    except Exception as e:
        print(f"Error validating admin.py: {e}")
        return False

def generate_advanced_admin():
    """Generate advanced admin with inline editing and custom views"""
    try:
        if CONFIG_PATH.exists():
            config = json.loads(CONFIG_PATH.read_text())
        else:
            print("No entities.json found")
            return False
        
        code_lines = [
            "from django.contrib import admin",
            "from django.urls import path",
            "from django.http import JsonResponse",
            "from django.template.response import TemplateResponse",
            "from .models import *",
            "",
            "# Advanced admin with custom views and inlines",
            ""
        ]
        
        # Generate inline classes for ForeignKey relationships
        inline_classes = []
        for model_name, model_config in config.items():
            fields = model_config.get("fields", {})
            
            # Find models that reference this model
            for other_model, other_config in config.items():
                if other_model != model_name:
                    other_fields = other_config.get("fields", {})
                    for field_name, field_def in other_fields.items():
                        if f"ForeignKey('{model_name}'" in str(field_def):
                            inline_class = f"{other_model}Inline"
                            if inline_class not in inline_classes:
                                code_lines.extend([
                                    f"class {inline_class}(admin.TabularInline):",
                                    f"    model = {other_model}",
                                    f"    extra = 1",
                                    f"    fields = ('__all__',)",
                                    ""
                                ])
                                inline_classes.append(inline_class)
        
        # Generate advanced admin classes
        for model_name, model_config in config.items():
            fields = model_config.get("fields", {})
            
            code_lines.extend([
                f"@admin.register({model_name})",
                f"class {model_name}Admin(admin.ModelAdmin):",
                f"    \"\"\"Advanced admin for {model_name}\"\"\"",
                ""
            ])
            
            # Add inlines if this model is referenced by others
            related_inlines = [inline for inline in inline_classes 
                             if inline.replace('Inline', '') in [other for other in config.keys() if other != model_name]]
            
            if related_inlines:
                code_lines.append(f"    inlines = [{', '.join(related_inlines)}]")
            
            # Add custom admin view
            code_lines.extend([
                f"    change_list_template = 'admin/{model_name.lower()}_change_list.html'",
                "",
                f"    def get_urls(self):",
                f"        urls = super().get_urls()",
                f"        custom_urls = [",
                f"            path('stats/', self.stats_view, name='{model_name.lower()}_stats'),",
                f"        ]",
                f"        return custom_urls + urls",
                "",
                f"    def stats_view(self, request):",
                f"        context = {{",
                f"            'title': f'{model_name} Statistics',",
                f"            'total_count': {model_name}.objects.count(),",
                f"            # Add more statistics here",
                f"        }}",
                f"        return TemplateResponse(request, 'admin/stats.html', context)",
                ""
            ])
        
        # Write advanced admin
        advanced_content = "\n".join(code_lines)
        advanced_path = APP_PATH / "advanced_admin.py"
        advanced_path.write_text(advanced_content)
        
        print(f"Advanced admin generated at {advanced_path}")
        return True
        
    except Exception as e:
        print(f"Error generating advanced admin: {e}")
        return False

def main():
    """Main function to generate admin interfaces"""
    print("🔧 Generating Django admin interfaces from entities.json...")
    
    # Ensure the app directory exists
    APP_PATH.mkdir(parents=True, exist_ok=True)
    
    # Generate admin
    if generate_admin():
        print("Admin generation completed")
        
        # Validate the generated file
        if validate_admin():
            print("✅ Admin validation passed")
            print("\nNext steps:")
            print("   1. Run: python manage.py collectstatic")
            print("   2. Access admin at: http://localhost:8000/admin/")
            print("   3. Login with your superuser credentials")
        else:
            print("⚠️  Admin validation failed, but file was created")
    else:
        print("❌ Admin generation failed")

if __name__ == "__main__":
    import sys
    
    if "--advanced" in sys.argv:
        print("Generating advanced admin with inlines and custom views...")
        generate_advanced_admin()
    else:
        main()