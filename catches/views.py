"""
Catch Views (Presentation Layer)
API Views untuk manajemen data tangkapan ikan dan PNBP predictions.
Facade yang menggunakan Application Layer untuk bisnis logic.
"""

import os
import json
from datetime import datetime
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from django.apps import apps
from django.db.models import Sum, Count, Avg

from .models import FishCatch, CatchDetail
from .serializers import FishCatchSerializer, CatchDetailSerializer, FishCatchWithDetailsSerializer
from .presentation.permissions import IsCatchOwnerOrAdmin
from .presentation.views.pnbp_views import (
    predict_pnbp_future,
    get_pnbp_history,
    get_latest_pnbp_predictions,
    get_unified_chart_data,
)
from ships.models import Ship

from catches.application.catch_service import CatchApplicationService
from catches.application.pnbp_service import PNBPredictionService


class IsCatchOwnerOrAdmin(permissions.BasePermission):
    """
    Anti-IDOR: Hanya pemilik kapal, nahkoda kapal terkait, atau admin/regulator yang dapat mengubah/menghapus laporan tangkapan.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'role', '') in ('admin', 'superadmin', 'regulator') or user.is_staff or user.is_superuser:
            return True
        catch_obj = getattr(obj, 'fish_catch', obj)
        ship = getattr(catch_obj, 'ship', None)
        if not ship:
            return False
        user_owner = getattr(user, 'owner', None)
        user_captain = getattr(user, 'captain', None)
        if user_owner and ship.owner_id == user_owner.id:
            return True
        if user_captain and ship.captain_id == user_captain.id:
            return True
        return False


@extend_schema_view(
    list=extend_schema(
        tags=['Catches'],
        summary='Daftar semua laporan tangkapan',
        description='Mengambil daftar semua laporan tangkapan ikan',
    ),
    create=extend_schema(
        tags=['Catches'],
        summary='Tambah laporan tangkapan baru',
    ),
    retrieve=extend_schema(
        tags=['Catches'],
        summary='Detail laporan tangkapan',
    ),
    update=extend_schema(
        tags=['Catches'],
        summary='Perbarui laporan tangkapan',
    ),
    partial_update=extend_schema(
        tags=['Catches'],
        summary='Perbarui sebagian laporan tangkapan',
    ),
    destroy=extend_schema(
        tags=['Catches'],
        summary='Hapus laporan tangkapan',
    ),
)
class FishCatchViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola laporan tangkapan ikan.
    """
    queryset = FishCatch._default_manager.all().order_by('-catch_date')
    serializer_class = FishCatchSerializer
    permission_classes = [permissions.IsAuthenticated, IsCatchOwnerOrAdmin]

    def perform_create(self, serializer):
        serializer.save()


@extend_schema_view(
    list=extend_schema(
        tags=['Catch Details'],
        summary='Daftar semua detail tangkapan',
        description='Mengambil daftar semua detail tangkapan ikan',
    ),
    create=extend_schema(
        tags=['Catch Details'],
        summary='Tambah detail tangkapan baru',
    ),
    retrieve=extend_schema(
        tags=['Catch Details'],
        summary='Detail detail tangkapan',
    ),
    update=extend_schema(
        tags=['Catch Details'],
        summary='Perbarui detail tangkapan',
    ),
    partial_update=extend_schema(
        tags=['Catch Details'],
        summary='Perbarui sebagian detail tangkapan',
    ),
    destroy=extend_schema(
        tags=['Catch Details'],
        summary='Hapus detail tangkapan',
    ),
)
class CatchDetailViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola detail tangkapan ikan.
    """
    queryset = CatchDetail._default_manager.all()
    serializer_class = CatchDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsCatchOwnerOrAdmin]


@extend_schema_view(
    list=extend_schema(
        tags=['Catch Details'],
        summary='Daftar detail tangkapan lengkap dengan relasi',
        description='Mengambil daftar detail tangkapan ikan lengkap dengan informasi ikan, kapal, dan lokasi',
    ),
    retrieve=extend_schema(
        tags=['Catch Details'],
        summary='Detail lengkap tangkapan',
    ),
)
class FishCatchWithDetailsViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola detail tangkapan ikan dengan data lengkap (relasi).
    """
    queryset = CatchDetail._default_manager.all().select_related('fish_catch', 'fish_catch__ship')
    serializer_class = FishCatchWithDetailsSerializer
    permission_classes = [permissions.IsAuthenticated, IsCatchOwnerOrAdmin]


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
    ''',
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def predict_pnbp_future(request):
    """
    API endpoint untuk prediksi PNBP masa depan menggunakan 4 metode analisis.
    """
    try:
        predictor_service = PNBPredictionService()

        use_db_data = request.data.get('use_database_data', True)
        historical_data = None
        if use_db_data:
            historical_data = predictor_service.get_pnbp_history()
        else:
            historical_data = request.data.get('historical_data')
            if not historical_data:
                historical_data = predictor_service.predictor.data_manager.load_historical_data()

        ships_data = request.data.get('ships_data')

        predictions = predictor_service.predict_pnbp_future(
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
            {'error': f'Gagal melakukan prediksi PNBP: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['PNBP Predictions'],
    summary='Ambil data historis PNBP',
    description='Mengambil data historis PNBP dari model Django',
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_pnbp_history(request):
    """
    Ambil data historis PNBP dari model Django.
    """
    try:
        predictor_service = PNBPredictionService()
        historical_data = predictor_service.get_pnbp_history()
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
    summary='Ambil prediksi PNBP terbaru',
    description='Mengambil prediksi PNBP terbaru yang disimpan',
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_latest_pnbp_predictions(request):
    """
    Ambil prediksi PNBP terbaru yang disimpan di file JSON.
    """
    try:
        predictor_service = PNBPredictionService()
        predictions = predictor_service.get_latest_pnbp_predictions()
        return Response({
            'status': 'success',
            'data': predictions,
            'message': 'Prediksi PNBP terbaru berhasil dimuat'
        })
    except Exception as e:
        return Response(
            {'error': 'Gagal memuat prediksi PNBP terbaru'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['PNBP Predictions'],
    summary='Data grafik dashboard terpadu',
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
        predictor_service = PNBPredictionService()
        charts_data = predictor_service.get_unified_chart_data()

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
