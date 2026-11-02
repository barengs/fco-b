"""
Fish Views (Presentation Layer)
API Views untuk manajemen data ikan dan tangkapan.
Facade yang menggunakan Application Layer untuk bisnis logic.
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import FishSpecies, Fish
from .serializers import FishSpeciesSerializer, FishSerializer
from .application.fish_service import FishSpeciesApplicationService, FishApplicationService


class FishSpeciesViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola spesies ikan.
    """
    queryset = FishSpecies.objects.all()
    serializer_class = FishSpeciesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FishSpeciesApplicationService()

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def import_species(self, request):
        """Import fish species from CSV data."""
        csv_data = request.data.get('csv_data')
        clear_existing = request.data.get('clear_existing', False)

        if not csv_data:
            return Response({'error': 'Data CSV wajib diisi'}, status=status.HTTP_400_BAD_REQUEST)

        result = self.service.import_species_from_csv(csv_data=csv_data, clear_existing=clear_existing)
        return Response(result)


@extend_schema_view(
    list=extend_schema(tags=['Fish'], summary='Daftar semua ikan'),
    create=extend_schema(tags=['Fish'], summary='Tambah ikan baru'),
    retrieve=extend_schema(tags=['Fish'], summary='Detail ikan'),
    update=extend_schema(tags=['Fish'], summary='Perbarui ikan'),
    partial_update=extend_schema(tags=['Fish'], summary='Perbarui sebagian ikan'),
    destroy=extend_schema(tags=['Fish'], summary='Hapus ikan'),
)
class FishViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola data tangkapan ikan.
    """
    queryset = Fish.objects.all()
    serializer_class = FishSerializer
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = FishApplicationService()

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def import_fish(self, request):
        """Import catch data from CSV."""
        csv_data = request.data.get('csv_data')
        clear_existing = request.data.get('clear_existing', False)

        if not csv_data:
            return Response({'error': 'Data CSV wajib diisi'}, status=status.HTTP_400_BAD_REQUEST)

        result = self.service.import_catches_from_csv(csv_data=csv_data, clear_existing=clear_existing)
        return Response(result)
