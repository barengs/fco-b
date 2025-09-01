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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override ship field to accept registration_number
        self.fields['ship'] = serializers.CharField()

    def create(self, validated_data):
        ship_registration = validated_data.pop('ship')
        try:
            ship = Ship.objects.get(registration_number=ship_registration)
            validated_data['ship'] = ship
        except Ship.DoesNotExist:
            raise serializers.ValidationError(f"Kapal dengan nomor registrasi '{ship_registration}' tidak ditemukan")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        ship_registration = validated_data.pop('ship', None)
        if ship_registration:
            try:
                ship = Ship.objects.get(registration_number=ship_registration)
                validated_data['ship'] = ship
            except Ship.DoesNotExist:
                raise serializers.ValidationError(f"Kapal dengan nomor registrasi '{ship_registration}' tidak ditemukan")
        return super().update(instance, validated_data)

    class Meta:
        model = FishCatch
        fields = '__all__'