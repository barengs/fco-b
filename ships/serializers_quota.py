from rest_framework import serializers


class QuotaPredictionInputSerializer(serializers.Serializer):
    ship_registration_number = serializers.CharField(
        required=True,
        help_text="Nomor registrasi kapal untuk prediksi kuota"
    )
    prediction_months = serializers.IntegerField(
        required=False,
        default=12,
        min_value=6,
        max_value=12,
        help_text="Jumlah bulan untuk prediksi (6-12 bulan, default: 12)"
    )
    epoch_level = serializers.IntegerField(
        required=False,
        default=5,
        min_value=1,
        max_value=5,
        help_text="""Level epoch untuk training LSTM (1-5):
        1: 4 epoch (20% - cepat tapi kurang akurat)
        2: 8 epoch (40% - sedang)
        3: 12 epoch (60% - balance)
        4: 16 epoch (80% - akurat tapi lambat)
        5: 20 epoch (100% - maksimal akurat)"""
    )


class LSTMQuotaPredictionSerializer(serializers.Serializer):
    date = serializers.DateField()
    predicted_value = serializers.FloatField()


class NSGA3OptimizedPredictionSerializer(serializers.Serializer):
    date = serializers.DateField()
    optimized_value = serializers.FloatField()


class QuotaPredictionResponseSerializer(serializers.Serializer):
    ship_registration_number = serializers.CharField()
    ship_name = serializers.CharField()
    epoch_level = serializers.IntegerField()
    epoch_used = serializers.IntegerField()
    confidence = serializers.FloatField()
    lstm_predictions = LSTMQuotaPredictionSerializer(many=True)
    nsga_optimized = NSGA3OptimizedPredictionSerializer(many=True)
    recommended_quota = serializers.FloatField()
    training_time = serializers.CharField()


class ManualQuotaInputSerializer(serializers.Serializer):
    """Serializer for manual quota input by regulator"""
    ship_registration_number = serializers.CharField(
        required=True,
        max_length=100,
        help_text="Nomor registrasi kapal yang akan diberikan kuota (misalnya: ABC123)"
    )
    year = serializers.IntegerField(
        required=True,
        min_value=2020,
        max_value=2050,
        help_text="Tahun kuota (misalnya: 2024)"
    )
    quota_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0,
        required=True,
        help_text="Jumlah kuota dalam kilogram (misalnya: 1000.50)"
    )

    def validate_ship_registration_number(self, value):
        """Validate that the ship exists"""
        from ships.models import Ship
        if not Ship.objects.filter(registration_number=value).exists():
            raise serializers.ValidationError(f"Kapal dengan nomor registrasi {value} tidak ditemukan")
        return value


class ManualQuotaResponseSerializer(serializers.Serializer):
    """Response serializer for manual quota input"""
    ship_registration_number = serializers.CharField(
        help_text="Nomor registrasi kapal"
    )
    ship_name = serializers.CharField(
        help_text="Nama kapal"
    )
    year = serializers.IntegerField(
        help_text="Tahun kuota"
    )
    quota_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Jumlah kuota yang dialokasikan (kg)"
    )
    remaining_quota = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Sisa kuota yang tersedia (kg)"
    )
    message = serializers.CharField(
        help_text="Pesan konfirmasi pendaftaran kuota"
    )