import uuid
from rest_framework import serializers
from django.utils import timezone
from .models import SmartScale, ScaleReading
from fish.models import FishSpecies
from ships.models import Ship, Quota
from regions.models import FishingArea
from catches.models import FishCatch, CatchDetail


class SmartScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartScale
        fields = ['id', 'device_id', 'name', 'port_name', 'api_key', 'is_active', 'last_seen', 'created_at']
        read_only_fields = ['id', 'last_seen', 'created_at']


class IoTWeightInputSerializer(serializers.Serializer):
    """
    Minimalist payload received from a raw IoT smart scale sensor.
    Only 'device_id' and 'weight' are required by the hardware microcontroller.
    """
    device_id = serializers.CharField(max_length=50, required=True, help_text="Identitas perangkat timbangan pintar (e.g. SCALE-BENOAS-01)")
    weight = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0, required=True, help_text="Total berat hasil timbangan di sensor (kg)")
    unit = serializers.CharField(max_length=20, default='kg', required=False, help_text="Opsional: Satuan berat (default: kg)")
    api_key = serializers.CharField(max_length=64, required=False, allow_blank=True, help_text="Opsional: Kunci API perangkat")


class ScaleReadingSerializer(serializers.ModelSerializer):
    """
    Serializer to display IoT readings to the frontend operator in real-time.
    """
    scale_name = serializers.CharField(source='scale.name', read_only=True)
    port_name = serializers.CharField(source='scale.port_name', read_only=True)

    class Meta:
        model = ScaleReading
        fields = [
            'id',
            'device_id',
            'scale_name',
            'port_name',
            'weight',
            'unit',
            'tare',
            'is_stable',
            'status',
            'session_id',
            'fish_catch',
            'catch_detail',
            'operator_notes',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class HarborWeighingCatchSaveSerializer(serializers.Serializer):
    """
    Serializer used by harbor operator on frontend to save fish catch
    after selecting fish species, using weight directly obtained from IoT scale.
    """
    reading_id = serializers.UUIDField(
        required=True,
        help_text="UUID dari pembacaan timbangan IoT (ScaleReading ID)"
    )
    ship_registration_number = serializers.CharField(
        max_length=100,
        required=True,
        help_text="Nomor registrasi kapal"
    )
    fish_species_id = serializers.IntegerField(
        required=True,
        help_text="ID Jenis Ikan yang dipilih operator"
    )
    wpp_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID Wilayah Penangkapan (FishingArea / WPP)"
    )
    catch_type = serializers.ChoiceField(
        choices=FishCatch.CATCH_TYPE_CHOICES,
        default='pelagic',
        required=False,
        help_text="Jenis penangkapan: pelagic, demersal, reef"
    )
    catch_date = serializers.DateField(
        required=False,
        default=timezone.now().date,
        help_text="Tanggal penangkapan (default: hari ini)"
    )
    location_latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        default=-8.7483,
        help_text="Latitude lokasi (default koordinat pelabuhan jika tidak diisi)"
    )
    location_longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        default=115.1672,
        help_text="Longitude lokasi"
    )
    operator_notes = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Catatan tambahan operator"
    )

    def validate_reading_id(self, value):
        try:
            reading = ScaleReading.objects.get(id=value)
        except ScaleReading.DoesNotExist:
            raise serializers.ValidationError("Data pembacaan timbangan tidak ditemukan.")
        if reading.status == 'saved':
            raise serializers.ValidationError("Data pembacaan timbangan ini sudah pernah disimpan.")
        return reading

    def validate_ship_registration_number(self, value):
        try:
            ship = Ship.objects.get(registration_number=value)
        except Ship.DoesNotExist:
            raise serializers.ValidationError(f"Kapal dengan nomor registrasi '{value}' tidak ditemukan.")
        return ship

    def validate_fish_species_id(self, value):
        try:
            species = FishSpecies.objects.get(id=value)
        except FishSpecies.DoesNotExist:
            raise serializers.ValidationError(f"Spesies ikan dengan ID {value} tidak ditemukan.")
        return species

    def validate_wpp_id(self, value):
        if not value:
            return None
        try:
            return FishingArea.objects.get(id=value)
        except FishingArea.DoesNotExist:
            raise serializers.ValidationError(f"Wilayah WPP dengan ID {value} tidak ditemukan.")
