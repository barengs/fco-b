from rest_framework import serializers
from .models import FishCatch, CatchDetail
from ships.models import Ship
from fish.models import FishSpecies

class CatchDetailSerializer(serializers.ModelSerializer):
    fish_species_name = serializers.CharField(source='fish_species.name', read_only=True)
    
    class Meta:
        model = CatchDetail
        fields = '__all__'

class FishCatchSerializer(serializers.ModelSerializer):
    ship_name = serializers.CharField(source='ship.name', read_only=True)
    catch_details = CatchDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = FishCatch
        fields = '__all__'