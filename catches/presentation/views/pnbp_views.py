"""
PNBP Prediction Views (Presentation Layer)
API Views for forecasting and serving unified PNBP dashboard analytics.
"""

import os
import json
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ...infrastructure.pnbp_predictor import PNBPredictor

@extend_schema(
    tags=['PNBP Predictions'],
    summary='Prediksi PNBP masa depan menggunakan 4 metode',
    description='''
    Melakukan prediksi PNBP (Penerimaan Negara Bukan Pajak) sektor perikanan menggunakan 4 metode:

    1. **Analisis Regresi** - Menganalisis hubungan antara variabel produksi, harga ikan, biaya operasional, dan kapasitas kapal
    2. **Jaringan Saraf (Neural Network)** - Mendeteksi pola non-linear dan tren jangka panjang pada data historis
    3. **Optimasi Multi-Objektif (NSGA-III)** - Mencari kombinasi optimal yang memaksimalkan pendapatan dengan menjaga keberlanjutan
    4. **Peramalan Deret Waktu** - Memprediksi berdasarkan pola musiman dan fluktuasi tahunan

    Hasil akhir adalah rata-rata tertimbang dengan bobot: Regresi 25%, Neural Network 35%, NSGA-III 25%, Time Series 15%.
    '''
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def predict_pnbp_future(request):
    """
    API endpoint untuk prediksi PNBP masa depan menggunakan 4 metode analisis.
    """
    try:
        # Initialize predictor
        predictor = PNBPredictor()

        # Get historical data from database if requested
        use_db_data = request.data.get('use_database_data', True)

        if use_db_data:
            historical_data = predictor.get_historical_data_from_django()
        else:
            # Use provided data or load from file
            historical_data = request.data.get('historical_data')
            if not historical_data:
                historical_data = predictor.data_manager.load_historical_data()

        # Get ships data if provided
        ships_data = request.data.get('ships_data')

        # Run prediction pipeline
        predictions = predictor.run_prediction_pipeline(historical_data, ships_data)

        # Optionally save results
        if request.data.get('save_results', False):
            predictor.save_results(predictions)

        return Response({
            'status': 'success',
            'predictions': predictions,
            'message': 'Prediksi PNBP berhasil dibuat'
        })

    except Exception as e:
        return Response(
            {'error': 'Gagal memproses kalkulasi prediksi'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['PNBP Predictions'],
    summary='Dapatkan data historis PNBP',
    description='Mengambil data historis PNBP dari database Django atau file JSON.'
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_pnbp_history(request):
    """
    API endpoint untuk mendapatkan data historis PNBP.
    """
    try:
        predictor = PNBPredictor()

        # Get data source preference
        source = request.query_params.get('source', 'database')

        if source == 'database':
            historical_data = predictor.get_historical_data_from_django()
        else:
            historical_data = predictor.data_manager.load_historical_data()

        return Response({
            'status': 'success',
            'source': source,
            'data_count': len(historical_data),
            'historical_data': historical_data
        })

    except Exception as e:
        return Response(
            {'error': 'Gagal memuat data historis PNBP'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['PNBP Predictions'],
    summary='Dapatkan hasil prediksi PNBP terakhir',
    description='Mengambil hasil prediksi PNBP yang tersimpan dari file JSON.'
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_latest_pnbp_predictions(request):
    """
    API endpoint untuk mendapatkan hasil prediksi PNBP terakhir.
    """
    try:
        filename = "pnbp_predictions.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                predictions_data = json.load(f)

            return Response({
                'status': 'success',
                'predictions': predictions_data
            })
        else:
            return Response({
                'status': 'not_found',
                'message': 'Belum ada riwayat prediksi tersimpan'
            }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response(
            {'error': 'Gagal memuat data prediksi'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['Charts'],
    summary='Data terpadu untuk semua grafik dashboard',
    description='''Endpoint untuk mendapatkan data terpadu dari semua endpoint grafik dalam satu response.
    Menggabungkan data historis PNBP, prediksi PNBP masa depan, dan prediksi kuota kapal.

    Response mencakup:
    - Historical PNBP data untuk trend charts
    - Latest PNBP predictions untuk forecast charts
    - Ship quota predictions untuk perbandingan LSTM vs NSGA-III
    - Aggregated statistics untuk summary cards
    ''',
    responses={
        200: {
            'type': 'object',
            'properties': {
                'status': {'type': 'string', 'example': 'success'},
                'charts_data': {
                    'type': 'object',
                    'properties': {
                        'historical_pnbp': {
                            'type': 'object',
                            'description': 'Data untuk grafik PNBP historis'
                        },
                        'pnbp_predictions': {
                            'type': 'object',
                            'description': 'Data untuk grafik prediksi PNBP'
                        },
                        'quota_predictions': {
                            'type': 'object',
                            'description': 'Data untuk grafik prediksi kuota'
                        },
                        'summary_stats': {
                            'type': 'object',
                            'description': 'Statistik ringkasan untuk dashboard cards'
                        }
                    }
                }
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_unified_chart_data(request):
    """
    Endpoint untuk mendapatkan data terpadu semua grafik dashboard.
    Menggabungkan historical PNBP, predictions, dan quota data dalam satu response.
    """
    try:
        # Initialize predictor
        predictor = PNBPredictor()

        # 1. Get historical PNBP data
        historical_data = predictor.get_historical_data_from_django()

        # 2. Get latest PNBP predictions
        pnbp_predictions = None
        filename = "pnbp_predictions.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                pnbp_predictions = json.load(f)

        # 3. Get sample quota prediction (you can modify this to get data for specific ships)
        # For demo purposes, we'll get data for the first ship in historical data
        quota_predictions = None
        if historical_data:
            # Find ships with data
            ships_with_data = list(set([item.get('nama_kapal') for item in historical_data if item.get('nama_kapal')]))
            if ships_with_data:
                from ships.ml_models import predict_and_optimize_quota
                try:
                    # Get quota prediction for first ship
                    ship_name = ships_with_data[0]
                    # We need to get registration number from ship name
                    from ships.models import Ship
                    ship_obj = Ship.objects.filter(name=ship_name).first()
                    if ship_obj:
                        quota_result = predict_and_optimize_quota(ship_obj.registration_number, 6, 3)
                        if not isinstance(quota_result, dict) or "error" not in quota_result:
                            quota_predictions = {
                                'ship_name': ship_name,
                                'ship_registration': ship_obj.registration_number,
                                'predictions': quota_result
                            }
                except Exception as e:
                    print(f"Error getting quota predictions: {e}")

        # 4. Calculate summary statistics
        summary_stats = {}
        if historical_data:
            pnbp_values = [item.get('total_pnbp', 0) for item in historical_data if item.get('total_pnbp')]
            volume_values = [item.get('total_volume', 0) for item in historical_data if item.get('total_volume')]

            if pnbp_values:
                summary_stats = {
                    'total_historical_records': len(historical_data),
                    'total_pnbp_sum': sum(pnbp_values),
                    'avg_pnbp_per_record': sum(pnbp_values) / len(pnbp_values),
                    'max_pnbp': max(pnbp_values),
                    'min_pnbp': min(pnbp_values),
                    'total_volume_sum': sum(volume_values) if volume_values else 0,
                    'avg_volume_per_record': sum(volume_values) / len(volume_values) if volume_values else 0,
                    'unique_ships': len(set([item.get('nama_kapal') for item in historical_data if item.get('nama_kapal')]))
                }

        # Prepare unified response
        charts_data = {
            'historical_pnbp': {
                'data': historical_data,
                'count': len(historical_data),
                'chart_type': 'line',
                'x_axis': 'timestamp',
                'y_axis': 'total_pnbp',
                'title': 'Historical PNBP Trends'
            },
            'pnbp_predictions': {
                'data': pnbp_predictions,
                'available': pnbp_predictions is not None,
                'chart_type': 'bar',
                'title': 'PNBP Prediction Methods Comparison'
            },
            'quota_predictions': {
                'data': quota_predictions,
                'available': quota_predictions is not None,
                'chart_type': 'line',
                'title': 'Ship Quota Predictions (LSTM vs NSGA-III)'
            },
            'summary_stats': summary_stats
        }

        return Response({
            'status': 'success',
            'charts_data': charts_data,
            'message': 'Data grafik berhasil dimuat'
        })

    except Exception as e:
        return Response(
            {'error': 'Gagal memuat data grafik'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )