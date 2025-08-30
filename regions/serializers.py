from rest_framework import serializers
from .models import FishingArea

class FishingAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FishingArea
        fields = '__all__'