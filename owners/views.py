"""
Owner Views (Presentation Layer)
API Views untuk manajemen pemilik kapal dan nahkoda.
Menggunakan Application Layer untuk bisnis logic.
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Owner, Captain
from .serializers import OwnerSerializer, CaptainSerializer
from .application.owner_service import OwnerApplicationService


class OwnerViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola pemilik kapal (perorangan atau perusahaan)
    """
    queryset = Owner.objects.prefetch_related('ships', 'captains').all()
    serializer_class = OwnerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OwnerApplicationService()

    def get_queryset(self):
        return self.service.get_owners_queryset(
            search=self.request.query_params.get('search', None)
        )


@extend_schema_view(
    list=extend_schema(
        tags=['Captains'],
        summary='Daftar semua nahkoda',
        description='Mengambil daftar semua nahkoda kapal'
    ),
    create=extend_schema(
        tags=['Captains'],
        summary='Buat nahkoda',
        description='Membuat nahkoda kapal baru'
    ),
    retrieve=extend_schema(
        tags=['Captains'],
        summary='Ambil nahkoda',
        description='Mengambil nahkoda tertentu berdasarkan ID'
    ),
    update=extend_schema(
        tags=['Captains'],
        summary='Perbarui nahkoda',
        description='Memperbarui nahkoda yang ada'
    ),
    partial_update=extend_schema(
        tags=['Captains'],
        summary='Perbarui sebagian nahkoda',
        description='Memperbarui sebagian nahkoda yang ada'
    ),
    destroy=extend_schema(
        tags=['Captains'],
        summary='Hapus nahkoda',
        description='Menghapus nahkoda'
    )
)
class CaptainViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola nahkoda kapal
    """
    queryset = Captain.objects.select_related('owner').prefetch_related('ships').all()
    serializer_class = CaptainSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = OwnerApplicationService()

    def get_queryset(self):
        return self.service.get_captains_queryset(
            user=self.request.user,
            owner_id=self.request.query_params.get('owner_id'),
            search=self.request.query_params.get('search')
        )
