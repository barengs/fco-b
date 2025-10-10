from rest_framework import serializers
from .models import Ship, Quota
from datetime import datetime


class QuotaInfoSerializer(serializers.Serializer):
    """Serializer untuk menampilkan informasi kuota dalam response kapal"""
    year = serializers.IntegerField()
    total_quota = serializers.DecimalField(max_digits=15, decimal_places=2)
    remaining_quota = serializers.DecimalField(max_digits=15, decimal_places=2)
    used_quota = serializers.SerializerMethodField()
    quota_percentage = serializers.SerializerMethodField()

    def get_used_quota(self, obj):
        """Hitung kuota yang sudah digunakan"""
        return obj['total_quota'] - obj['remaining_quota']

    def get_quota_percentage(self, obj):
        """Hitung persentase kuota yang tersisa"""
        if obj['total_quota'] > 0:
            return round((obj['remaining_quota'] / obj['total_quota']) * 100, 2)
        return 0


class ShipSerializer(serializers.ModelSerializer):
    owner_name = serializers.ReadOnlyField(source='owner.full_name')
    captain_name = serializers.ReadOnlyField(source='captain.full_name')
    current_year_quota = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make owner field optional
        self.fields['owner'].required = False
        self.fields['owner'].allow_null = True

    def get_current_year_quota(self, obj):
        """Ambil data kuota untuk tahun berjalan"""
        current_year = datetime.now().year
        try:
            quota = obj.quotas.filter(year=current_year, is_active=True).first()
            if quota:
                return {
                    'year': quota.year,
                    'total_quota': quota.quota,
                    'remaining_quota': quota.remaining_quota,
                    'used_quota': quota.quota - quota.remaining_quota,
                    'quota_percentage': round((quota.remaining_quota / quota.quota) * 100, 2) if quota.quota > 0 else 0
                }
        except:
            pass
        return None

    class Meta:
        model = Ship
        fields = ['id', 'name', 'registration_number', 'owner', 'owner_name', 'captain', 'captain_name',
                  'length', 'width', 'gross_tonnage', 'year_built', 'home_port', 'active', 'current_year_quota']


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