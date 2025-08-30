from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import FishCatch, CatchDetail
from .serializers import FishCatchSerializer, CatchDetailSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(summary='Daftar semua laporan tangkapan ikan', description='Mengambil daftar semua laporan tangkapan ikan'),
    create=extend_schema(summary='Buat laporan tangkapan ikan', description='Membuat laporan tangkapan ikan baru'),
    retrieve=extend_schema(summary='Ambil laporan tangkapan ikan', description='Mengambil laporan tangkapan ikan tertentu berdasarkan ID'),
    update=extend_schema(summary='Perbarui laporan tangkapan ikan', description='Memperbarui laporan tangkapan ikan yang ada'),
    partial_update=extend_schema(summary='Perbarui sebagian laporan tangkapan ikan', description='Memperbarui sebagian laporan tangkapan ikan yang ada'),
    destroy=extend_schema(summary='Hapus laporan tangkapan ikan', description='Menghapus laporan tangkapan ikan')
)
class FishCatchViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola laporan tangkapan ikan
    """
    queryset = FishCatch.objects.all()  # type: ignore
    serializer_class = FishCatchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Secara opsional membatasi tangkapan yang dikembalikan berdasarkan kapal atau rentang tanggal tertentu"""
        queryset = FishCatch.objects.all()  # type: ignore
        ship_id = self.request.query_params.get('ship_id', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if ship_id is not None:
            queryset = queryset.filter(ship_id=ship_id)
        
        if start_date is not None:
            queryset = queryset.filter(catch_date__gte=start_date)
            
        if end_date is not None:
            queryset = queryset.filter(catch_date__lte=end_date)
            
        return queryset

@extend_schema_view(
    list=extend_schema(summary='Daftar semua detail tangkapan', description='Mengambil daftar semua detail tangkapan (spesies dan jumlah)'),
    create=extend_schema(summary='Buat detail tangkapan', description='Membuat detail tangkapan baru'),
    retrieve=extend_schema(summary='Ambil detail tangkapan', description='Mengambil detail tangkapan tertentu berdasarkan ID'),
    update=extend_schema(summary='Perbarui detail tangkapan', description='Memperbarui detail tangkapan yang ada'),
    partial_update=extend_schema(summary='Perbarui sebagian detail tangkapan', description='Memperbarui sebagian detail tangkapan yang ada'),
    destroy=extend_schema(summary='Hapus detail tangkapan', description='Menghapus detail tangkapan')
)
class CatchDetailViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola detail tangkapan (spesies dan jumlah)
    """
    queryset = CatchDetail.objects.all()  # type: ignore
    serializer_class = CatchDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]