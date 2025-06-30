from django.contrib import admin
from .models import *

# Auto-generated Admin from entities.json config

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['pk', 'username', 'guild']
    search_fields = ['username']
    list_filter = ['guild']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['pk', 'match_id', 'start_time', 'winner']
    search_fields = ['match_id']
    list_filter = ['start_time']

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']
    search_fields = ['name']

@admin.register(Guild)
class GuildAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']
    search_fields = ['name']