"""
Ship ViewSet (Presentation Layer)
CRUD and actions for managing fishing vessels.
"""

import logging
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema_view, extend_schema
from django.db import models

from ...models import Ship
from ...serializers import ShipSerializer
from ..permissions import IsShipOwnerOrAdmin
from ...application.ship_csv_service import ShipCsvService

logger = logging.getLogger(__name__)

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
    permission_classes = [permissions.IsAuthenticated, IsShipOwnerOrAdmin]

    def _is_privileged(self, user) -> bool:
        return bool(
            user
            and (
                getattr(user, 'role', '') in ('admin', 'superadmin', 'regulator')
                or user.is_staff
                or user.is_superuser
            )
        )

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user or not user.is_authenticated:
            return qs.none()
        if self._is_privileged(user):
            return qs
        user_owner = getattr(user, 'owner', None)
        if user_owner is not None:
            return qs.filter(owner_id=user_owner.id)
        user_captain = getattr(user, 'captain', None)
        if user_captain is not None:
            return qs.filter(captain_id=user_captain.id)
        return qs.none()

    @extend_schema(
        tags=['Ships'],
        summary='Daftar kapal berdasarkan pemilik',
        description='Mengambil seluruh kapal milik user yang login atau ID pemilik spesifik'
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def by_owner(self, request):
        """Dapatkan semua kapal berdasarkan ID pemilik atau pemilik akun login"""
        owner_id = request.GET.get('owner_id')
        user = request.user

        if not self._is_privileged(user):
            user_owner = getattr(user, 'owner', None)
            if not user_owner:
                return Response({'error': 'Maaf, Anda tidak memiliki akses ke data ini.'}, status=status.HTTP_403_FORBIDDEN)
            if owner_id and str(owner_id) != str(user_owner.id):
                return Response({'error': 'Maaf, Anda hanya dapat melihat data armada milik sendiri.'}, status=status.HTTP_403_FORBIDDEN)
            owner_id = user_owner.id

        if not owner_id:
            return Response(
                {'error': 'Parameter owner_id belum diisi.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ships = self.queryset.filter(
                models.Q(owner_id=owner_id) | models.Q(owner__user_id=owner_id)
            ).distinct()
            serializer = self.get_serializer(ships, many=True)
            return Response(serializer.data)
        except Exception:
            logger.exception("Gagal mengambil daftar kapal milik owner %s", owner_id)
            return Response(
                {'error': 'Gagal memuat daftar kapal.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=['Ships'],
        summary='Daftar kapal berdasarkan nahkoda',
        description='Mengambil kapal yang dinahkodai oleh nahkoda tertentu'
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def by_captain(self, request):
        """Dapatkan semua kapal berdasarkan ID nahkoda"""
        captain_id = request.GET.get('captain_id')
        user = request.user

        if not self._is_privileged(user):
            user_captain = getattr(user, 'captain', None)
            if user_captain:
                if captain_id and str(captain_id) != str(user_captain.id):
                    return Response({'error': 'Maaf, Anda tidak memiliki akses ke data ini.'}, status=status.HTTP_403_FORBIDDEN)
                captain_id = user_captain.id
            elif not getattr(user, 'owner', None):
                return Response({'error': 'Maaf, Anda tidak memiliki akses ke data ini.'}, status=status.HTTP_403_FORBIDDEN)

        if not captain_id:
            return Response(
                {'error': 'Parameter captain_id belum diisi.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ships = self.get_queryset().filter(captain_id=captain_id)
            serializer = self.get_serializer(ships, many=True)
            return Response(serializer.data)
        except Exception:
            logger.exception("Gagal mengambil daftar kapal milik nahkoda %s", captain_id)
            return Response(
                {'error': 'Gagal memuat daftar kapal.'},
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
                {'error': 'Silakan pilih atau unggah file CSV terlebih dahulu.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        MAX_UPLOAD_SIZE = 10 * 1024 * 1024
        if csv_file_upload and getattr(csv_file_upload, 'size', 0) > MAX_UPLOAD_SIZE:
            return Response(
                {'error': 'Ukuran file CSV maksimal 10 MB ya.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if clear_existing:
            user = request.user
            is_admin = user and (user.is_superuser or getattr(user, 'role', '') in ('admin', 'superadmin') or user.is_staff)
            if not is_admin:
                return Response(
                    {'error': 'Maaf, hanya administrator yang diizinkan menghapus seluruh data sebelum impor.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            Ship._default_manager.all().delete()

        try:
            result = ShipCsvService.parse_and_import(csv_file_upload=csv_file_upload, csv_data=csv_data)
            return Response({
                'message': 'Data kapal berhasil diimpor.',
                **result
            })
        except ValueError as ve:
            return Response(
                {'error': str(ve)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            logger.exception("Gagal mengimpor data kapal dari CSV")
            return Response(
                {'error': 'Gagal mengimpor file CSV. Silakan periksa kembali format kolom dan isinya.'},
                status=status.HTTP_400_BAD_REQUEST
            )
