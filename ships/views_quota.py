"""
Views for Quota Prediction using LSTM and NSGA-III algorithms
LSTM performs initial prediction, then NSGA-III optimizes the results.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps
from datetime import datetime, timedelta
from .serializers_quota import (
    QuotaPredictionInputSerializer, 
    QuotaPredictionResponseSerializer
)
from .ml_models import (
    predict_and_optimize_quota, 
    generate_quota_recommendation
)


@extend_schema(
    tags=['Quota Prediction'],
    summary='Prediksi Kuota Kapal dengan LSTM dan NSGA-III',
    description='''Memprediksi kuota penangkapan ikan untuk kapal berdasarkan nomor registrasi 
    menggunakan algoritma LSTM dan NSGA-III berdasarkan data historis pelaporan penangkapan.
    
    Cara kerja:
    1. LSTM melakukan prediksi awal berdasarkan tren historis
    2. NSGA-III mengoptimasi hasil LSTM berdasarkan faktor keberlanjutan dan dampak lingkungan
    
    Fitur:
    - Prediksi kuota menggunakan LSTM yang dioptimasi dengan NSGA-III
    - Interval kepercayaan untuk prediksi
    - Skor kebugaran untuk hasil optimasi
    - Rekomendasi kuota berdasarkan hasil optimasi''',
    request=QuotaPredictionInputSerializer,
    responses={
        200: QuotaPredictionResponseSerializer,
        400: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string', 'description': 'Pesan kesalahan validasi'}
            }
        },
        404: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string', 'description': 'Kapal tidak ditemukan'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_ship_quota(request):
    """
    Endpoint untuk memprediksi kuota penangkapan ikan berdasarkan nomor registrasi kapal
    menggunakan algoritma LSTM dan NSGA-III secara berurutan:
    1. LSTM melakukan prediksi awal
    2. NSGA-III mengoptimasi hasil LSTM
    """
    # Validate input data
    serializer = QuotaPredictionInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid input data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Extract validated data
    # Type checker workaround - we know validated_data is not None after successful validation
    validated_data = serializer.validated_data
    ship_registration_number = validated_data['ship_registration_number']  # type: ignore
    prediction_months = validated_data.get('prediction_months', 12)  # type: ignore
    
    # Get Ship model dynamically
    Ship = apps.get_model('ships', 'Ship')
    
    # Verify ship exists
    try:
        ship = Ship._default_manager.get(registration_number=ship_registration_number)
    except ObjectDoesNotExist:
        return Response(
            {'error': f'Kapal dengan nomor registrasi {ship_registration_number} tidak ditemukan'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Run sequential prediction and optimization
    # 1. LSTM prediction -> 2. NSGA-III optimization
    optimized_results = predict_and_optimize_quota(ship_registration_number, prediction_months)
    
    # Check if there was an error
    if isinstance(optimized_results, dict) and "error" in optimized_results:
        return Response(
            {'error': optimized_results["error"]},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate recommendation
    recommendation = generate_quota_recommendation(optimized_results)
    
    # Prepare response data
    # Format the results for the response
    lstm_predictions = []
    nsga3_predictions = []
    
    for result in optimized_results:
        # LSTM predictions
        lstm_predictions.append({
            "date": result["date"],  # type: ignore
            "predicted_quota": result["lstm_predicted_quota"],  # type: ignore
            "confidence_interval": result["confidence_interval"]  # type: ignore
        })
        
        # NSGA-III optimized predictions
        nsga3_predictions.append({
            "date": result["date"],  # type: ignore
            "predicted_quota": result["optimized_quota"],  # type: ignore
            "fitness_score": result["fitness_score"]  # type: ignore
        })
    
    response_data = {
        'ship_registration_number': ship_registration_number,
        'ship_name': ship.name,
        'prediction_period': f"{prediction_months} bulan ke depan",
        'lstm_predictions': lstm_predictions,
        'nsga3_predictions': nsga3_predictions,
        'recommendation': recommendation
    }
    
    # Validate response with serializer
    response_serializer = QuotaPredictionResponseSerializer(data=response_data)
    if response_serializer.is_valid():
        return Response(response_serializer.validated_data)
    else:
        return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)