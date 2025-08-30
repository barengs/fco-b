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
    recommendation = serializers.CharField(
        help_text="Rekomendasi kuota berdasarkan prediksi dan optimasi"
    )