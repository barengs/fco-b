from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Owner, Captain
from .serializers import OwnerSerializer, CaptainSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.contrib.auth import get_user_model

User = get_user_model()


@extend_schema_view(
    list=extend_schema(
        tags=['Owners'],
        summary='Daftar semua pemilik', 
        description='Mengambil daftar semua pemilik kapal (perorangan atau perusahaan)'
    ),
    create=extend_schema(
        tags=['Owners'],
        summary='Buat pemilik', 
        description='Membuat pemilik kapal baru'
    ),
    retrieve=extend_schema(
        tags=['Owners'],
        summary='Ambil pemilik', 
        description='Mengambil pemilik tertentu berdasarkan ID'
    ),
    update=extend_schema(
        tags=['Owners'],
        summary='Perbarui pemilik', 
        description='Memperbarui pemilik yang ada'
    ),
    partial_update=extend_schema(
        tags=['Owners'],
        summary='Perbarui sebagian pemilik', 
        description='Memperbarui sebagian pemilik yang ada'
    ),
    destroy=extend_schema(
        tags=['Owners'],
        summary='Hapus pemilik', 
        description='Menghapus pemilik'
    )
)
class OwnerViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola pemilik kapal (perorangan atau perusahaan)
    """
    queryset = Owner.objects.prefetch_related('ships', 'captains').all()  # type: ignore
    serializer_class = OwnerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

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
    queryset = Captain.objects.select_related('owner').prefetch_related('ships').all()  # type: ignore
    serializer_class = CaptainSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]