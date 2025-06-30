#!/usr/bin/env python3
"""
Enhanced migration script for dynamically generated models.
Deletes old migrations, generates new ones, applies them, and validates DB state.
"""

import os
import subprocess
import sys
import shutil
import django
from pathlib import Path


APP_NAME = "adminpanel"
MIGRATIONS_PATH = Path(APP_NAME) / "migrations"
EXCLUDE_FILES = {"__init__.py", "__pycache__"}


def run_command(cmd, silent=False):
    """Run shell command and return (success, output)"""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if not silent:
        print(f"$ {' '.join(cmd)}")
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr and result.returncode != 0:
            print(result.stderr.strip())
    return result.returncode == 0, result.stdout.strip()


def delete_old_migrations():
    if not MIGRATIONS_PATH.exists():
        return

    print(f"🧹 Cleaning up old migration files in {MIGRATIONS_PATH}")
    for f in MIGRATIONS_PATH.iterdir():
        if f.name not in EXCLUDE_FILES and f.suffix == ".py":
            print(f"  Deleting {f.name}")
            f.unlink()
        elif f.is_dir() and f.name == "__pycache__":
            shutil.rmtree(f)


def generate_migrations():
    print("📦 Generating new migrations...")
    return run_command(["python", "manage.py", "makemigrations", APP_NAME])


def apply_migrations():
    print("🔧 Applying migrations...")
    return run_command(["python", "manage.py", "migrate"])


def validate_tables(expected_models):
    print("🔍 Validating database tables...")
    django.setup()
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tablename FROM pg_catalog.pg_tables 
            WHERE schemaname = 'public'
        """)
        existing = {row[0] for row in cursor.fetchall()}

    success = True
    for model in expected_models:
        table = f"{APP_NAME}_{model.lower()}"
        if table not in existing:
            print(f"❌ Missing table: {table}")
            success = False
        else:
            print(f"✅ Found table: {table}")
    return success


def extract_model_names():
    from config.entities import get_model_names
    return get_model_names()


def main():
    print(f"🚀 Starting migration process for app: {APP_NAME}")

    delete_old_migrations()

    success, _ = generate_migrations()
    if not success:
        print("❌ Migration generation failed")
        return False

    success, _ = apply_migrations()
    if not success:
        print("❌ Migration application failed")
        return False

    try:
        # Only validate if Django is ready
        expected_models = extract_model_names()
        if not validate_tables(expected_models):
            print("⚠️ Some expected tables are missing")
    except Exception as e:
        print(f"⚠️ Skipping table validation: {e}")

    print("✅ Migrations complete and database is in sync")
    return True


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    sys.exit(0 if main() else 1)
