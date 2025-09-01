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

class FishCatchWithDetailsSerializer(serializers.ModelSerializer):
    """Serializer for creating FishCatch with nested CatchDetails in a single request"""
    catch_details = CatchDetailSerializer(many=True, write_only=True)
    ship_name = serializers.CharField(source='ship.name', read_only=True)
    catch_details_display = CatchDetailSerializer(many=True, read_only=True, source='catch_details')
    
    class Meta:
        model = FishCatch
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        catch_details_data = validated_data.pop('catch_details', [])
        fish_catch = FishCatch._default_manager.create(**validated_data)
        
        for detail_data in catch_details_data:
            CatchDetail._default_manager.create(fish_catch=fish_catch, **detail_data)
        
        return fish_catch
    
    def update(self, instance, validated_data):
        catch_details_data = validated_data.pop('catch_details', None)
        
        # Update FishCatch fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update catch details if provided
        if catch_details_data is not None:
            # Delete existing details
            instance.catch_details.all().delete()
            # Create new details
            for detail_data in catch_details_data:
                CatchDetail._default_manager.create(fish_catch=instance, **detail_data)
        
        return instance
