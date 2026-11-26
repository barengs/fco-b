"""
Fish Views (Presentation Layer)
API Views untuk manajemen data ikan dan tangkapan.
Facade yang menggunakan Application Layer untuk bisnis logic.
"""

from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import FishSpecies, Fish
from .serializers import FishSpeciesSerializer, FishSerializer
from .application.fish_service import FishSpeciesApplicationService, FishApplicationService


class IsAdminOrRegulatorOrReadOnly(permissions.BasePermission):
    """Membatasi perubahan master spesies dan sampel ikan hanya untuk administrator atau regulator."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                getattr(user, 'role', '') in ('admin', 'superadmin', 'regulator')
                or user.is_staff
                or user.is_superuser
            )
        )


@extend_schema_view(
    list=extend_schema(
        tags=['Fish Species'],
        summary='Daftar semua spesies ikan',
        description='Mengambil daftar seluruh spesies ikan dalam katalog'
    ),
    create=extend_schema(
        tags=['Fish Species'],
        summary='Buat spesies ikan baru',
        description='Menambahkan data spesies ikan baru ke katalog'
    ),
    retrieve=extend_schema(
        tags=['Fish Species'],
        summary='Ambil data spesies ikan',
        description='Mengambil informasi detail spesies ikan berdasarkan ID'
    ),
    update=extend_schema(
        tags=['Fish Species'],
        summary='Perbarui spesies ikan',
        description='Memperbarui data spesies ikan'
    ),
    partial_update=extend_schema(
        tags=['Fish Species'],
        summary='Perbarui sebagian spesies ikan',
        description='Memperbarui sebagian atribut data spesies ikan'
    ),
    destroy=extend_schema(
        tags=['Fish Species'],
        summary='Hapus spesies ikan',
        description='Menghapus spesies ikan dari katalog'
    ),
)
class FishSpeciesViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola spesies ikan.
    """
    queryset = FishSpecies.objects.all()
    serializer_class = FishSpeciesSerializer
    permission_classes = [IsAdminOrRegulatorOrReadOnly]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FishSpeciesApplicationService()

    @extend_schema(
        tags=['Fish Species'],
        summary='Impor spesies ikan dari CSV',
        description='Mengimpor data spesies ikan secara massal dari string CSV'
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrRegulatorOrReadOnly])
    def import_species(self, request):
        """Import fish species from CSV data."""
        csv_data = request.data.get('csv_data')
        clear_existing = request.data.get('clear_existing', False)
        if isinstance(clear_existing, str):
            clear_existing = clear_existing.lower() in ('true', '1', 'yes', 'on')

        if not csv_data:
            return Response({'error': 'Silakan isi atau unggah data CSV terlebih dahulu.'}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(csv_data, str) and len(csv_data.encode('utf-8')) > 10 * 1024 * 1024:
            return Response({'error': 'Ukuran data CSV maksimal 10 MB ya.'}, status=status.HTTP_400_BAD_REQUEST)

        if clear_existing:
            user = request.user
            is_admin = user and (user.is_superuser or getattr(user, 'role', '') in ('admin', 'superadmin') or user.is_staff)
            if not is_admin:
                return Response(
                    {'error': 'Maaf, hanya administrator yang diizinkan menghapus seluruh data sebelum impor.'},
                    status=status.HTTP_403_FORBIDDEN
                )

        result = self.service.import_species_from_csv(csv_data=csv_data, clear_existing=clear_existing)
        return Response(result)

    @extend_schema(
        tags=['Fish Species'],
        summary='Unduh template CSV spesies ikan',
        description='Mengunduh file template CSV untuk impor data spesies ikan'
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def download_template(self, request):
        """Download CSV template for importing fish species."""
        content = self.service.get_template_csv()
        response = HttpResponse(content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="fish_species_import_template.csv"'
        return response

    @extend_schema(
        tags=['Fish Species'],
        summary='Unduh template CSV ikan individual',
        description='Mengunduh file template CSV untuk impor data sampel ikan'
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def download_fish_template(self, request):
        """Download CSV template for importing fish catches."""
        content = self.service.get_fish_template_csv()
        response = HttpResponse(content, content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="fish_import_template.csv"'
        return response


@extend_schema_view(
    list=extend_schema(tags=['Fish Species'], summary='Daftar semua sampel ikan'),
    create=extend_schema(tags=['Fish Species'], summary='Tambah sampel ikan baru'),
    retrieve=extend_schema(tags=['Fish Species'], summary='Detail sampel ikan'),
    update=extend_schema(tags=['Fish Species'], summary='Perbarui sampel ikan'),
    partial_update=extend_schema(tags=['Fish Species'], summary='Perbarui sebagian sampel ikan'),
    destroy=extend_schema(tags=['Fish Species'], summary='Hapus sampel ikan'),
)
class FishViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola data tangkapan ikan.
    """
    queryset = Fish.objects.all()
    serializer_class = FishSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrRegulatorOrReadOnly]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FishApplicationService()

    @extend_schema(
        tags=['Fish Species'],
        summary='Impor sampel ikan dari CSV',
        description='Mengimpor data sampel ikan secara massal dari string CSV'
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAdminOrRegulatorOrReadOnly])
    def import_fish(self, request):
        """Import catch data from CSV."""
        csv_data = request.data.get('csv_data')
        clear_existing = request.data.get('clear_existing', False)
        if isinstance(clear_existing, str):
            clear_existing = clear_existing.lower() in ('true', '1', 'yes', 'on')

        if not csv_data:
            return Response({'error': 'Silakan isi atau unggah data CSV terlebih dahulu.'}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(csv_data, str) and len(csv_data.encode('utf-8')) > 10 * 1024 * 1024:
            return Response({'error': 'Ukuran data CSV maksimal 10 MB ya.'}, status=status.HTTP_400_BAD_REQUEST)

        if clear_existing:
            user = request.user
            is_admin = user and (user.is_superuser or getattr(user, 'role', '') in ('admin', 'superadmin') or user.is_staff)
            if not is_admin:
                return Response(
                    {'error': 'Maaf, hanya administrator yang diizinkan menghapus seluruh data sebelum impor.'},
                    status=status.HTTP_403_FORBIDDEN
                )

        result = self.service.import_catches_from_csv(csv_data=csv_data, clear_existing=clear_existing)
        return Response(result)
