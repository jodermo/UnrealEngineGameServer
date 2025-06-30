from rest_framework import serializers
from .models import *

# Auto-generated Serializers from entities.json config

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'
        exclude = ['password']
        depth = 2

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'
        depth = 1
