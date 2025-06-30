from django.contrib import admin
from .models import *

# Auto-generated Admin from entities.json config

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['pk'] + [f.name for f in Player._meta.fields[1:6]]  # Show first 5 fields
    search_fields = ['pk']
    list_filter = []

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['pk'] + [f.name for f in Match._meta.fields[1:6]]  # Show first 5 fields
    search_fields = ['pk']
    list_filter = []
