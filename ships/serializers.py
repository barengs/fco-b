from rest_framework import serializers
from .models import Ship, Quota
from owners.models import Owner, Captain

class QuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quota
        fields = ['id', 'year', 'quota', 'remaining_quota', 'is_active', 'created_at', 'updated_at']


class ShipSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    captain_name = serializers.CharField(source='captain.name', read_only=True)
    quotas = QuotaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Ship
        fields = '__all__'