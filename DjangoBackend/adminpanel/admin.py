from django.contrib import admin
from .models import *

# Auto-generated Admin interfaces from entities.json config

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """
    Admin interface for Player model
    """

    list_display = ['id', 'username', 'email', 'created_at']
    search_fields = ['username', 'email']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    list_per_page = 25
    ordering = ['-id']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    """
    Admin interface for Match model
    """

    list_display = ['id', 'match_id', 'start_time', 'end_time', 'winner']
    search_fields = ['match_id']
    list_filter = ['start_time', 'end_time', 'winner']
    list_per_page = 25
    ordering = ['-id']

    # Custom methods for foreign key relationships
    def winner_info(self, obj):
        if obj.winner:
            return str(obj.winner)
        return '-'
    winner_info.short_description = 'Winner'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """
    Admin interface for Item model
    """

    list_display = ['id', 'name', 'description', 'item_type', 'value', 'rarity']
    search_fields = ['name', 'description', 'item_type', 'rarity']
    list_per_page = 25
    ordering = ['-id']


@admin.register(Guild)
class GuildAdmin(admin.ModelAdmin):
    """
    Admin interface for Guild model
    """

    list_display = ['id', 'name', 'description', 'created_at', 'member_count', 'is_active']
    search_fields = ['name', 'description']
    list_filter = ['created_at', 'is_active']
    readonly_fields = ['created_at']
    list_per_page = 25
    ordering = ['-id']


# Customize admin site header and title
admin.site.site_header = 'Unreal Engine Game Server Admin'
admin.site.site_title = 'UE Game Admin'
admin.site.index_title = 'Game Server Administration'

# Add custom admin actions
def export_selected_as_json(modeladmin, request, queryset):
    """Export selected items as JSON"""
    from django.http import JsonResponse
    import json
    
    data = []
    for obj in queryset:
        item = {}
        for field in obj._meta.fields:
            value = getattr(obj, field.name)
            if hasattr(value, 'isoformat'):  # DateTime fields
                value = value.isoformat()
            item[field.name] = value
        data.append(item)
    
    response = JsonResponse(data, safe=False)
    response['Content-Disposition'] = 'attachment; filename="export.json"'
    return response

export_selected_as_json.short_description = 'Export selected as JSON'

# Register the action globally for all models
admin.site.add_action(export_selected_as_json)