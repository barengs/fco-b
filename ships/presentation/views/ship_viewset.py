"""
Ship ViewSet (Presentation Layer)
CRUD and actions for managing fishing vessels.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema_view, extend_schema
from django.db import models

from ...models import Ship
from ...serializers import ShipSerializer
from ..permissions import IsShipOwnerOrAdmin
from ...application.ship_csv_service import ShipCsvService

@extend_schema_view(
    list=extend_schema(
        tags=['Ships'],
        summary='Daftar semua kapal',
        description='Mengambil daftar semua kapal penangkap ikan dengan informasi kuota tahun berjalan',
    ),
    retrieve=extend_schema(
        tags=['Ships'],
        summary='Detail kapal',
        description='Mengambil detail informasi satu kapal penangkap ikan berdasarkan ID',
    ),
    create=extend_schema(
        tags=['Ships'],
        summary='Tambah kapal baru',
        description='Mendaftarkan kapal penangkap ikan baru ke dalam sistem',
    ),
    update=extend_schema(
        tags=['Ships'],
        summary='Perbarui data kapal',
        description='Memperbarui seluruh data kapal penangkap ikan',
    ),
    partial_update=extend_schema(
        tags=['Ships'],
        summary='Perbarui sebagian data kapal',
        description='Memperbarui sebagian data kapal penangkap ikan',
    ),
    destroy=extend_schema(
        tags=['Ships'],
        summary='Hapus kapal',
        description='Menghapus data kapal penangkap ikan dari sistem',
    ),
)
class ShipViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola kapal penangkap ikan.
    """
    queryset = Ship.objects.select_related('owner', 'captain').prefetch_related('quotas').all()
    serializer_class = ShipSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsShipOwnerOrAdmin]

    @extend_schema(
        tags=['Ships'],
        summary='Daftar kapal berdasarkan pemilik',
        description='Mengambil seluruh kapal milik user yang login atau ID pemilik spesifik'
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def by_owner(self, request):
        """Dapatkan semua kapal berdasarkan ID pemilik atau pemilik akun login"""
        owner_id = request.GET.get('owner_id')
        user = request.user

        if not owner_id and user and user.is_authenticated and hasattr(user, 'owner') and user.owner:
            owner_id = user.owner.id

        if not owner_id:
            return Response(
                {'error': 'Parameter owner_id diperlukan'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ships = self.queryset.filter(
                models.Q(owner_id=owner_id) | models.Q(owner__user_id=owner_id)
            ).distinct()
            serializer = self.get_serializer(ships, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Error retrieving ships: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Ships'],
        summary='Daftar kapal berdasarkan nahkoda',
        description='Mengambil kapal yang dinahkodai oleh nahkoda tertentu'
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def by_captain(self, request):
        """Dapatkan semua kapal berdasarkan ID nahkoda"""
        captain_id = request.GET.get('captain_id')

        if not captain_id:
            return Response(
                {'error': 'Parameter captain_id diperlukan'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ships = self.queryset.filter(captain_id=captain_id)
            serializer = self.get_serializer(ships, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Error retrieving ships: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Ships'],
        summary='Riwayat tangkapan kapal',
        description='Mengambil seluruh riwayat laporan tangkapan untuk kapal tertentu'
    )
    @action(detail=True, methods=['get'])
    def catch_reports(self, request, pk=None):
        """Dapatkan semua laporan tangkapan untuk kapal tertentu"""
        ship = self.get_object()
        catches = ship.catch_reports.all()
        from catches.serializers import FishCatchSerializer
        serializer = FishCatchSerializer(catches, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['Ships'],
        summary='Unduh template CSV impor kapal',
        description='Mengunduh file template CSV untuk impor data armada kapal'
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def download_template(self, request):
        """
        Download CSV template for ship import (delegated to application layer service)
        """
        return ShipCsvService.generate_template()

    @extend_schema(
        tags=['Ships'],
        summary='Impor kapal dari CSV',
        description='Mengimpor data armada kapal secara massal dari string atau file CSV'
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def import_ships(self, request):
        """
        Import ships from CSV data provided in the request (delegated to application layer service)
        """
        csv_data = request.data.get('csv_data')
        csv_file_upload = request.FILES.get('csv_file') or request.FILES.get('csv_data')
        clear_existing = request.data.get('clear_existing', False)

        if not csv_data and not csv_file_upload:
            return Response(
                {'error': 'Pilih atau unggah file CSV terlebih dahulu'},
                status=status.HTTP_400_BAD_REQUEST
            )

        MAX_UPLOAD_SIZE = 10 * 1024 * 1024
        if csv_file_upload and getattr(csv_file_upload, 'size', 0) > MAX_UPLOAD_SIZE:
            return Response(
                {'error': 'Ukuran file melebihi batas maksimal 10 MB'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if clear_existing:
            user = request.user
            is_admin = user and (user.is_superuser or getattr(user, 'role', '') in ('admin', 'superadmin') or user.is_staff)
            if not is_admin:
                return Response(
                    {'error': 'Hanya administrator yang diizinkan menggunakan opsi hapus seluruh data (clear_existing)'},
                    status=status.HTTP_403_FORBIDDEN
                )
            Ship._default_manager.all().delete()

        try:
            result = ShipCsvService.parse_and_import(csv_file_upload=csv_file_upload, csv_data=csv_data)
            return Response({
                'message': 'Data kapal berhasil diimpor',
                **result
            })
        except Exception as e:
            return Response(
                {'error': f'Gagal mengimpor CSV: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
