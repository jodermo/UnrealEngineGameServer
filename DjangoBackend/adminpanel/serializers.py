from rest_framework import serializers
from .models import *

class PlayerSerializer(serializers.ModelSerializer):
    guild = GuildSerializer(read_only=True)
    class Meta:
        model = Player
        fields = '__all__'


class GuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guild
        fields = '__all__'

class MatchSerializer(serializers.ModelSerializer):
    winner = PlayerSerializer(read_only=True)
    class Meta:
        model = Match
        fields = '__all__'


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class GuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guild
        fields = '__all__'

