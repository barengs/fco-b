from rest_framework import serializers
from .models import Ship, Quota


class ShipSerializer(serializers.ModelSerializer):
    owner_name = serializers.ReadOnlyField(source='owner.full_name')
    captain_name = serializers.ReadOnlyField(source='captain.full_name')
    
    class Meta:
        model = Ship
        fields = ['id', 'name', 'registration_number', 'owner', 'owner_name', 'captain', 'captain_name',
                 'length', 'width', 'gross_tonnage', 'year_built', 'home_port', 'active']


class QuotaSerializer(serializers.ModelSerializer):
    ship_name = serializers.ReadOnlyField(source='ship.name')
    
    class Meta:
        model = Quota
        fields = ['id', 'ship', 'ship_name', 'year', 'quota', 'remaining_quota', 'is_active']


class BestFishingLocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField(allow_null=True)
    longitude = serializers.FloatField(allow_null=True)


class ShipRecommendationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    registration_number = serializers.CharField()
    owner = serializers.CharField()
    captain = serializers.CharField(allow_null=True)
    total_catch = serializers.FloatField()
    average_catch = serializers.FloatField()
    catch_trend = serializers.CharField()
    catch_efficiency = serializers.FloatField()
    best_fishing_location = BestFishingLocationSerializer()
    best_fishing_months = serializers.ListField(child=serializers.CharField())


class AIRecommendationResponseSerializer(serializers.Serializer):
    top_ships = ShipRecommendationSerializer(many=True)
    analysis_period = serializers.CharField()
    recommendation_factors = serializers.CharField()
    total_ships_analyzed = serializers.IntegerField()