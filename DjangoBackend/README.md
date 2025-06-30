# DjangoBackend – Admin & API for Unreal Game Server

This folder contains a Django-based backend for managing and monitoring your Unreal Engine dedicated server. It includes a RESTful API and optional admin panel to manage players, matches, scores, and other gameplay data.

#### Features

  - Django 4.x with PostgreSQL support

  - REST API with Django REST Framework

  - Admin dashboard for in-game data

  - Dockerized and ready for container orchestration

  - Auto-migration and optional superuser setup

  - Modular config-driven model generation (optional)


#### Folder Structure

  ```bash
  DjangoBackend/
├── adminpanel/            # Main Django app (models, views, admin, API)
├── entrypoint.sh          # Initializes DB, runs migrations, creates superuser
├── manage.py              # Django CLI tool
├── requirements.txt       # Python dependencies
├── settings/              # Django project config (optional split layout)
├── __init__.py

  ```

### Dynamic Backend-API And Database Generation

#### Ecample `entities.json`

(DjangoBackend/config/[entities.json](config/entities.json))

  ```bash
  {
  "Player": {
    "fields": {
      "username": "CharField(max_length=50, unique=True)",
      "email": "EmailField()",
      "score": "IntegerField(default=0)",
      "is_active": "BooleanField(default=True)"
    }
  },
  "Match": {
    "fields": {
      "match_id": "CharField(max_length=32, unique=True)",
      "start_time": "DateTimeField()",
      "end_time": "DateTimeField(null=True, blank=True)",
      "winner": "ForeignKey('Player', on_delete=models.DO_NOTHING, null=True)"
    }
  }
}
  ```