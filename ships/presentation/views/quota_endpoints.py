"""
Views for Quota Prediction using LSTM and NSGA-III algorithms
LSTM performs initial prediction, then NSGA-III optimizes the results.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from ...application.quota_service import QuotaApplicationService
from ...serializers_quota import (
    QuotaPredictionInputSerializer,
    QuotaPredictionResponseSerializer,
    ManualQuotaInputSerializer,
    ManualQuotaResponseSerializer
)

_quota_service = QuotaApplicationService()


@extend_schema(
    tags=['Ships'],
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
    Endpoint untuk memprediksi kuota penangkapan ikan berdasarkan nomor registrasi kapal.
    Mendelegasikan orkestrasi ke QuotaApplicationService.
    """
    serializer = QuotaPredictionInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Data permintaan belum lengkap atau tidak sesuai.', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    validated_data = serializer.validated_data
    ship_registration_number = validated_data['ship_registration_number']  # type: ignore
    prediction_months = validated_data.get('prediction_months', 12)  # type: ignore
    epoch_level = validated_data.get('epoch_level', 5)  # type: ignore

    result = _quota_service.predict_quota_for_ship(
        ship_registration_number=ship_registration_number,
        prediction_months=prediction_months,
        epoch_level=epoch_level
    )

    if 'error' in result:
        return Response(
            {'error': result['error']},
            status=result.get('status_code', status.HTTP_400_BAD_REQUEST)
        )

    response_serializer = QuotaPredictionResponseSerializer(data=result['data'])
    if response_serializer.is_valid():
        return Response(response_serializer.validated_data)
    else:
        return Response(
            {'error': 'Format hasil prediksi kuota tidak valid.', 'details': response_serializer.errors},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['Ships'],
    summary='Input Kuota Manual oleh Regulator',
    description='''Fungsi khusus untuk regulator memasukkan kuota real secara manual untuk setiap kapal.
    Regulator dapat memilih kapal mana yang akan diberikan kuota dan memasukkan jumlah kuota per kapal.

    Cara kerja:
    1. Regulator memilih kapal berdasarkan nomor registrasi
    2. Memasukkan tahun kuota dan jumlah kuota dalam kg
    3. Sistem akan membuat atau mengupdate record kuota untuk kapal tersebut
    4. Kuota akan tersimpan dalam database dan dapat digunakan untuk tracking penangkapan

    Hanya user dengan role 'regulator' yang dapat mengakses endpoint ini.

    Contoh penggunaan:
    POST /ships/regulator/manual-quota/
    {
        "ship_registration_number": "ABC123",
        "year": 2024,
        "quota_amount": 1000.50
    }''',
    request=ManualQuotaInputSerializer,
    responses={
        200: ManualQuotaResponseSerializer,
        400: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string', 'description': 'Pesan kesalahan validasi'}
            }
        },
        403: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string', 'description': 'Akses ditolak - hanya untuk regulator'}
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
def regulator_manual_quota_input(request):
    """
    Endpoint khusus regulator untuk input kuota manual per kapal.
    Hanya regulator yang dapat mengakses endpoint ini.
    """
    # Check if user has regulator or admin role
    user_role = getattr(request.user, 'role', None)
    if user_role not in ['regulator', 'admin'] and not request.user.is_staff and not request.user.is_superuser:
        return Response(
            {'error': 'Akses ditolak. Fitur ini khusus untuk regulator atau administrator.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Validate input data
    serializer = ManualQuotaInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Data kuota belum lengkap atau tidak sesuai.', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Extract validated data
    ship_registration_number = serializer.validated_data['ship_registration_number']
    year = serializer.validated_data['year']
    quota_amount = serializer.validated_data['quota_amount']

    result = _quota_service.assign_manual_quota(
        ship_registration_number=ship_registration_number,
        year=year,
        quota_amount=quota_amount
    )

    if 'error' in result:
        return Response(
            {'error': result['error']},
            status=result.get('status_code', status.HTTP_404_NOT_FOUND)
        )

    response_serializer = ManualQuotaResponseSerializer(data=result['data'])
    if response_serializer.is_valid():
        return Response(response_serializer.validated_data)
    else:
        return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)