#!/usr/bin/env python3
"""
Generate Django models from entities.json configuration
Creates models.py with proper field definitions, relationships, and metadata
"""

import json
import re
from pathlib import Path

# Configuration paths
CONFIG_PATH = Path("config/entities.json")
APP_PATH = Path("adminpanel")


def clean_field_definition(field_def):
    """Clean and validate field definition string"""
    field_def = field_def.replace("models.", "")
    constants = ['CASCADE', 'SET_NULL', 'PROTECT', 'SET_DEFAULT', 'DO_NOTHING']
    for c in constants:
        field_def = field_def.replace(f"models.{c}", c)
    return field_def


def validate_field_definition(field_name, field_def):
    warnings = []
    if "ForeignKey" in field_def and "on_delete" not in field_def:
        warnings.append(f"ForeignKey '{field_name}' missing on_delete parameter")
    if "ForeignKey(" in field_def and not ("'" in field_def or '"' in field_def):
        warnings.append(f"ForeignKey '{field_name}' should quote the related model name")
    if "CharField(" in field_def and "max_length" not in field_def:
        warnings.append(f"CharField '{field_name}' missing max_length parameter")
    return warnings


def generate_model_class(model_name, model_config):
    fields = model_config.get("fields", {})
    meta = model_config.get("meta", {})
    methods = model_config.get("methods", {})
    code = [f"class {model_name}(models.Model):"]

    if not fields:
        code.append("    pass")
        return code

    code.extend([
        f'    """',
        f'    {model_name} model',
        f'    Auto-generated from entities.json configuration',
        f'    """',
        ""
    ])

    all_warnings = []
    for fname, fdef in fields.items():
        if isinstance(fdef, str):
            warnings = validate_field_definition(fname, fdef)
            all_warnings.extend(warnings)
            cleaned = clean_field_definition(fdef)
            code.append(f"    {fname} = models.{cleaned}")
        elif isinstance(fdef, dict):
            ftype = fdef.get("type", "CharField(max_length=255)")
            validators = fdef.get("validators", [])
            help_text = fdef.get("help_text", "")
            line = f"    {fname} = models.{ftype}"
            if validators:
                line += f", validators={validators}"
            if help_text:
                line += f", help_text='{help_text}'"
            code.append(line)
        else:
            code.append(f"    {fname} = models.CharField(max_length=255)  # TODO")

    code.append("")
    code.append("    class Meta:")
    code.append(f"        verbose_name = '{model_name}'")
    code.append(f"        verbose_name_plural = '{model_name}s'")

    if meta:
        for k, v in meta.items():
            if k == "ordering" and isinstance(v, list):
                ordering = ", ".join(f"'{item}'" for item in v)
                code.append(f"        ordering = ({ordering},)")
            elif k == "indexes" and isinstance(v, list):
                indexes = []
                for idx in v:
                    if isinstance(idx, dict) and "fields" in idx:
                        fields_list = ", ".join(f"'{f}'" for f in idx["fields"])
                        indexes.append(f"models.Index(fields=[{fields_list}])")
                if indexes:
                    code.append(f"        indexes = [{', '.join(indexes)}]")
            elif k in ["unique_together", "permissions"] and isinstance(v, list):
                code.append(f"        {k} = {v}")
            elif isinstance(v, str):
                code.append(f"        {k} = '{v}'")

    code.append("")
    code.append("    def __str__(self):")
    code.append("        return self.__unicode__()")
    code.append("")

    # __unicode__ method
    display_field = next((f for f, d in fields.items()
                          if any(t in str(d) for t in ['CharField', 'TextField', 'EmailField']) and
                          ('unique=True' in str(d) or f in ['name', 'title', 'username', 'email'])), None)
    if display_field:
        code.append("    def __unicode__(self):")
        code.append(f"        return str(self.{display_field})")
    else:
        code.append("    def __unicode__(self):")
        code.append(f"        return f'{model_name} {{self.pk}}'")
    code.append("")

    # Custom methods
    for mname, mbody in methods.items():
        code.append(f"    def {mname}(self):")
        code.append(f"        {mbody}")
        code.append("")

    # Utility methods
    code.extend([
        "    def get_absolute_url(self):",
        "        from django.urls import reverse",
        f"        return reverse('{model_name.lower()}-detail', kwargs={{'pk': self.pk}})",
        "",
        "    @classmethod",
        "    def get_recent(cls, limit=10):",
        "        return cls.objects.order_by('-id')[:limit]",
        ""
    ])

    if all_warnings:
        print(f"Warnings for {model_name}:")
        for w in all_warnings:
            print(f"  - {w}")

    return code


def generate_models():
    if not CONFIG_PATH.exists():
        print("No entities.json found.")
        return False

    config = json.loads(CONFIG_PATH.read_text())
    print(f"Loaded configuration with {len(config)} models")

    header = [
        "from django.db import models",
        "from django.db.models import CASCADE, SET_NULL, PROTECT, SET_DEFAULT, DO_NOTHING",
        "from django.contrib.auth.models import User",
        "from django.core.validators import MinValueValidator, MaxValueValidator",
        "from django.utils import timezone",
        "",
        "# Auto-generated models",
        ""
    ]

    model_dependencies = {}
    for mname, mconfig in config.items():
        deps = []
        for fname, fdef in mconfig.get("fields", {}).items():
            match = re.search(r"(ForeignKey|OneToOneField)\s*\(\s*['\"]([^'\"]+)['\"]", str(fdef))
            if match:
                target = match.group(2)
                if target != mname and target in config:
                    deps.append(target)
        model_dependencies[mname] = deps

    def sort_models(deps_map):
        sorted_models = []
        remaining = set(deps_map.keys())
        while remaining:
            ready = [m for m in remaining if all(d in sorted_models for d in deps_map[m])]
            if not ready:
                ready = list(remaining)
            for m in ready:
                sorted_models.append(m)
                remaining.remove(m)
        return sorted_models

    sorted_names = sort_models(model_dependencies)
    all_lines = header[:]
    for m in sorted_names:
        all_lines += generate_model_class(m, config[m])
        all_lines.append("")

    # Utility functions
    all_lines += [
        "# Utility functions",
        "def get_all_model_counts():",
        "    counts = {}",
    ]
    for m in config:
        all_lines.append(f"    counts['{m.lower()}'] = {m}.objects.count()")
    all_lines += [
        "    return counts",
        "",
        "def get_model_by_name(model_name):",
        "    models_map = {",
    ]
    for m in config:
        all_lines.append(f"        '{m.lower()}': {m},")
    all_lines += [
        "    }",
        "    return models_map.get(model_name.lower())",
    ]

    output_path = APP_PATH / "models.py"
    output_path.write_text("\n".join(all_lines))
    print(f"Models generated at {output_path}")
    return config


def validate_models():
    path = APP_PATH / "models.py"
    if not path.exists():
        print("models.py not found.")
        return False
    try:
        compile(path.read_text(), str(path), 'exec')
        print("models.py is valid.")
        return True
    except Exception as e:
        print(f"Validation failed: {e}")
        return False


def main():
    print("Generating Django models from entities.json...")
    APP_PATH.mkdir(parents=True, exist_ok=True)
    config = generate_models()
    if config and validate_models():
        print(f"Successfully generated {len(config)} models.")
        print("Run the following commands to proceed:")
        print("  python manage.py makemigrations adminpanel")
        print("  python manage.py migrate")
        return True
    return False


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
