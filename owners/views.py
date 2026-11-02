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

    def get_queryset(self):
        qs = Owner.objects.exclude(full_name__startswith='Owner of ').prefetch_related('ships', 'captains')
        search = self.request.query_params.get('search', None)
        if search:
            qs = qs.filter(full_name__icontains=search)
        return qs


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

    def get_queryset(self):
        qs = Captain.objects.select_related('owner').prefetch_related('ships')
        user = self.request.user

        if getattr(user, 'role', '') == 'owner':
            owner_obj = getattr(user, 'owner', None)
            if owner_obj:
                qs = qs.filter(
                    models.Q(owner=owner_obj) | models.Q(ships__owner=owner_obj)
                ).distinct()
            else:
                owner_id = self.request.query_params.get('owner_id')
                if owner_id:
                    qs = qs.filter(
                        models.Q(owner_id=owner_id) | models.Q(ships__owner_id=owner_id)
                    ).distinct()
        else:
            owner_id = self.request.query_params.get('owner_id')
            if owner_id:
                qs = qs.filter(
                    models.Q(owner_id=owner_id) | models.Q(ships__owner_id=owner_id)
                ).distinct()

        search = self.request.query_params.get('search', None)
        if search:
            qs = qs.filter(full_name__icontains=search)
        return qs
