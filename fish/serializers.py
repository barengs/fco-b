from rest_framework import serializers
from .models import FishSpecies, Fish

class FishSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FishSpecies
        fields = '__all__'

class FishSerializer(serializers.ModelSerializer):
    species_name = serializers.CharField(source='species.name', read_only=True)
    
    class Meta:
        model = Fish
        fields = '__all__'