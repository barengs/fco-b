"""
PNBP Prediction Views (Presentation Layer)
API Views for forecasting and serving unified PNBP dashboard analytics.
"""

from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ...application.pnbp_service import PNBPredictionService


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
        service = PNBPredictionService()
        use_db_data = request.data.get('use_database_data', True)
        historical_data = None
        if use_db_data:
            historical_data = service.get_pnbp_history()
        else:
            historical_data = request.data.get('historical_data')
            if not historical_data:
                historical_data = service.predictor.data_manager.load_historical_data()

        ships_data = request.data.get('ships_data')
        predictions = service.predict_pnbp_future(
            historical_data=historical_data,
            ships_data=ships_data,
        )

        return Response({
            'status': 'success',
            'data': predictions,
            'message': 'Prediksi PNBP berhasil dihasilkan'
        })
    except Exception as e:
        return Response(
            {'error': f'Gagal memproses kalkulasi prediksi: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['PNBP Predictions'],
    summary='Dapatkan data historis PNBP',
    description='Mengambil data historis PNBP dari model Django.'
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_pnbp_history(request):
    """
    API endpoint untuk mendapatkan data historis PNBP.
    """
    try:
        service = PNBPredictionService()
        historical_data = service.get_pnbp_history()
        return Response({
            'status': 'success',
            'data': historical_data,
            'count': len(historical_data),
            'message': 'Data historis PNBP berhasil dimuat'
        })
    except Exception as e:
        return Response(
            {'error': 'Gagal memuat data historis PNBP'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['PNBP Predictions'],
    summary='Dapatkan hasil prediksi PNBP terakhir',
    description='Mengambil hasil prediksi PNBP yang tersimpan.'
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_latest_pnbp_predictions(request):
    """
    API endpoint untuk mendapatkan hasil prediksi PNBP terakhir.
    """
    try:
        service = PNBPredictionService()
        predictions_data = service.get_latest_pnbp_predictions()
        if predictions_data:
            return Response({
                'status': 'success',
                'data': predictions_data,
                'message': 'Prediksi PNBP terbaru berhasil dimuat'
            })
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
    tags=['PNBP Predictions'],
    summary='Data terpadu untuk semua grafik dashboard',
    description='Menggabungkan data historis PNBP, predictions, dan kuota dalam satu response',
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_unified_chart_data(request):
    """
    Endpoint untuk mendapatkan data terpadu semua grafik dashboard.
    Menggabungkan historical PNBP, predictions, dan quota data dalam satu response.
    """
    try:
        service = PNBPredictionService()
        result = service.get_unified_chart_data()
        return Response(result)
    except Exception as e:
        return Response(
            {'error': 'Gagal memuat data grafik'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )