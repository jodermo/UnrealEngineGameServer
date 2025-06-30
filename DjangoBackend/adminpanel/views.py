from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse
from .models import *
from .serializers import *

# Auto-generated ViewSets from entities.json config

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Permissions: ['read', 'update']
    
    def create(self, request):
        return Response({'error': 'Create not permitted'}, status=403)

    def destroy(self, request, pk=None):
        return Response({'error': 'Delete not permitted'}, status=403)

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Permissions: ['read', 'create', 'update', 'delete'] (default)

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class GuildViewSet(viewsets.ModelViewSet):
    queryset = Guild.objects.all()
    serializer_class = GuildSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]