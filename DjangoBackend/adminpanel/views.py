from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import *
from .serializers import *

# Auto-generated ViewSets from entities.json

class PlayerViewSet(viewsets.ModelViewSet):
    """ViewSet for Player model"""
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PlayerCreateUpdateSerializer
        elif self.action == 'list':
            return PlayerListSerializer
        return PlayerSerializer

    @action(detail=False)
    def recent(self, request):
        recent = self.queryset.order_by('-id')[:10]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def stats(self, request):
        return Response({'count': self.queryset.count()})

    @action(detail=False)
    def export(self, request):
        data = self.get_serializer(self.queryset, many=True).data
        return Response(data)

    @action(detail=False)
    def timeline(self, request):
        return Response(self.get_serializer(self.queryset.order_by('id'), many=True).data)

    @action(detail=False)
    def search(self, request):
        term = request.query_params.get('q', '')
        results = self.queryset.filter(id__icontains=term)
        return Response(self.get_serializer(results, many=True).data)

class MatchViewSet(viewsets.ModelViewSet):
    """ViewSet for Match model"""
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MatchCreateUpdateSerializer
        elif self.action == 'list':
            return MatchListSerializer
        return MatchSerializer

    @action(detail=False)
    def recent(self, request):
        recent = self.queryset.order_by('-id')[:10]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def stats(self, request):
        return Response({'count': self.queryset.count()})

    @action(detail=False)
    def export(self, request):
        data = self.get_serializer(self.queryset, many=True).data
        return Response(data)

    @action(detail=False)
    def timeline(self, request):
        return Response(self.get_serializer(self.queryset.order_by('id'), many=True).data)

    @action(detail=False)
    def search(self, request):
        term = request.query_params.get('q', '')
        results = self.queryset.filter(id__icontains=term)
        return Response(self.get_serializer(results, many=True).data)

class ItemViewSet(viewsets.ModelViewSet):
    """ViewSet for Item model"""
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ItemCreateUpdateSerializer
        elif self.action == 'list':
            return ItemListSerializer
        return ItemSerializer

    @action(detail=False)
    def recent(self, request):
        recent = self.queryset.order_by('-id')[:10]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def stats(self, request):
        return Response({'count': self.queryset.count()})

    @action(detail=False)
    def export(self, request):
        data = self.get_serializer(self.queryset, many=True).data
        return Response(data)

    @action(detail=False)
    def timeline(self, request):
        return Response(self.get_serializer(self.queryset.order_by('id'), many=True).data)

    @action(detail=False)
    def search(self, request):
        term = request.query_params.get('q', '')
        results = self.queryset.filter(id__icontains=term)
        return Response(self.get_serializer(results, many=True).data)

class GuildViewSet(viewsets.ModelViewSet):
    """ViewSet for Guild model"""
    queryset = Guild.objects.all()
    serializer_class = GuildSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return GuildCreateUpdateSerializer
        elif self.action == 'list':
            return GuildListSerializer
        return GuildSerializer

    @action(detail=False)
    def recent(self, request):
        recent = self.queryset.order_by('-id')[:10]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def stats(self, request):
        return Response({'count': self.queryset.count()})

    @action(detail=False)
    def export(self, request):
        data = self.get_serializer(self.queryset, many=True).data
        return Response(data)

    @action(detail=False)
    def timeline(self, request):
        return Response(self.get_serializer(self.queryset.order_by('id'), many=True).data)

    @action(detail=False)
    def search(self, request):
        term = request.query_params.get('q', '')
        results = self.queryset.filter(id__icontains=term)
        return Response(self.get_serializer(results, many=True).data)
