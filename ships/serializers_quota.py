from rest_framework import serializers


class QuotaPredictionInputSerializer(serializers.Serializer):
    ship_registration_number = serializers.CharField(
        required=True,
        help_text="Nomor registrasi kapal untuk prediksi kuota"
    )
    prediction_months = serializers.IntegerField(
        required=False,
        default=12,
        help_text="Jumlah bulan untuk prediksi (default: 12)"
    )
    algorithm = serializers.ChoiceField(
        choices=['lstm', 'nsga3', 'both'],
        required=False,
        default='both',
        help_text="Algoritma yang digunakan untuk prediksi (lstm, nsga3, atau both)"
    )


class LSTMQuotaPredictionSerializer(serializers.Serializer):
    date = serializers.DateField()
    predicted_quota = serializers.FloatField()
    confidence_interval = serializers.ListField(
        child=serializers.FloatField(),
        help_text="Interval kepercayaan [lower_bound, upper_bound]"
    )


class NSGA3QuotaPredictionSerializer(serializers.Serializer):
    date = serializers.DateField()
    predicted_quota = serializers.FloatField()
    fitness_score = serializers.FloatField()


class QuotaPredictionResponseSerializer(serializers.Serializer):
    ship_registration_number = serializers.CharField()
    ship_name = serializers.CharField()
    prediction_period = serializers.CharField()
    lstm_predictions = LSTMQuotaPredictionSerializer(many=True, required=False)
    nsga3_predictions = NSGA3QuotaPredictionSerializer(many=True, required=False)
    recommendation = serializers.JSONField()


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