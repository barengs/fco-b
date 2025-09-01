from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import FishCatch, CatchDetail
from .serializers import FishCatchSerializer, CatchDetailSerializer, FishCatchWithDetailsSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(
        tags=['Fish Catches'],
        summary='Daftar semua laporan tangkapan ikan',
        description='''Mengambil daftar semua laporan tangkapan ikan dengan opsi filter.
        
Fitur:
- Pembuatan laporan tangkapan ikan
- Detail tangkapan berdasarkan spesies
- Manajemen data tangkapan
- Filter berdasarkan kapal dan rentang tanggal

Filter yang Tersedia:
- ship_id: Memfilter berdasarkan ID kapal
- start_date: Memfilter berdasarkan tanggal awal tangkapan (format: YYYY-MM-DD)
- end_date: Memfilter berdasarkan tanggal akhir tangkapan (format: YYYY-MM-DD)
        '''
    ),
    create=extend_schema(
        tags=['Fish Catches'],
        summary='Buat laporan tangkapan ikan',
        description='Membuat laporan tangkapan ikan baru dengan detail spesies dan jumlah.'
    ),
    retrieve=extend_schema(
        tags=['Fish Catches'],
        summary='Ambil laporan tangkapan ikan',
        description='Mengambil laporan tangkapan ikan tertentu berdasarkan ID.'
    ),
    update=extend_schema(
        tags=['Fish Catches'],
        summary='Perbarui laporan tangkapan ikan',
        description='Memperbarui laporan tangkapan ikan yang ada.'
    ),
    partial_update=extend_schema(
        tags=['Fish Catches'],
        summary='Perbarui sebagian laporan tangkapan ikan',
        description='Memperbarui sebagian informasi laporan tangkapan ikan yang ada.'
    ),
    destroy=extend_schema(
        tags=['Fish Catches'],
        summary='Hapus laporan tangkapan ikan',
        description='Menghapus laporan tangkapan ikan dari sistem.'
    )
)
class FishCatchViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola laporan tangkapan ikan.
    
    Fitur:
    - Manajemen laporan tangkapan ikan (CRUD)
    - Filter berdasarkan kapal dan rentang tanggal
    - Relasi dengan detail tangkapan (spesies dan jumlah)
    - Integrasi dengan data kapal dan area penangkapan
    
    Hak Akses:
    - Pengguna yang diautentikasi dapat membuat, memperbarui, dan menghapus
    - Pengguna anonim hanya dapat melihat data
    """
    queryset = FishCatch._default_manager.all()  # type: ignore
    serializer_class = FishCatchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Secara opsional membatasi tangkapan yang dikembalikan berdasarkan kapal atau rentang tanggal tertentu"""
        queryset = FishCatch._default_manager.all()  # type: ignore
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
    create=extend_schema(
        tags=['Fish Catches'],
        summary='Buat laporan tangkapan ikan dengan detail',
        description='Membuat laporan tangkapan ikan baru dengan detail spesies dan jumlah dalam satu permintaan.'
    ),
    update=extend_schema(
        tags=['Fish Catches'],
        summary='Perbarui laporan tangkapan ikan dengan detail',
        description='Memperbarui laporan tangkapan ikan yang ada beserta detail spesies dan jumlah dalam satu permintaan.'
    )
)
class FishCatchWithDetailsViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola laporan tangkapan ikan dengan detail dalam satu endpoint.
    
    Fitur:
    - Membuat laporan tangkapan ikan dengan detail dalam satu permintaan
    - Memperbarui laporan tangkapan ikan beserta detail dalam satu permintaan
    - Mengambil laporan tangkapan ikan dengan detail terkait
    """
    queryset = FishCatch._default_manager.all()  # type: ignore
    serializer_class = FishCatchWithDetailsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Secara opsional membatasi tangkapan yang dikembalikan berdasarkan kapal atau rentang tanggal tertentu"""
        queryset = FishCatch._default_manager.all()  # type: ignore
        ship_id = self.request.query_params.get('ship_id', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if ship_id is not None:
            queryset = queryset.filter(ship_id=ship_id)
        
        if start_date is not None:
            queryset = queryset.filter(catch_date__gte=start_date)
            
        if end_date is not None:
            queryset = queryset.filter(catch_date__lte=end_date)
            
        return queryset.prefetch_related('catch_details', 'catch_details__fish_species', 'ship')

@extend_schema_view(
    list=extend_schema(
        tags=['Fish Catches'],
        summary='Daftar semua detail tangkapan',
        description='''Mengambil daftar semua detail tangkapan (spesies dan jumlah).
        
Fitur:
- Detail tangkapan berdasarkan spesies
- Informasi kuantitas dan berat tangkapan
- Catatan tambahan untuk setiap detail tangkapan'''
    ),
    create=extend_schema(
        tags=['Fish Catches'],
        summary='Buat detail tangkapan',
        description='Membuat detail tangkapan baru dengan spesies ikan dan jumlah.'
    ),
    retrieve=extend_schema(
        tags=['Fish Catches'],
        summary='Ambil detail tangkapan',
        description='Mengambil detail tangkapan tertentu berdasarkan ID.'
    ),
    update=extend_schema(
        tags=['Fish Catches'],
        summary='Perbarui detail tangkapan',
        description='Memperbarui detail tangkapan yang ada.'
    ),
    partial_update=extend_schema(
        tags=['Fish Catches'],
        summary='Perbarui sebagian detail tangkapan',
        description='Memperbarui sebagian informasi detail tangkapan yang ada.'
    ),
    destroy=extend_schema(
        tags=['Fish Catches'],
        summary='Hapus detail tangkapan',
        description='Menghapus detail tangkapan dari sistem.'
    )
)
class CatchDetailViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola detail tangkapan (spesies dan jumlah).
    
    Fitur:
    - Manajemen detail tangkapan (CRUD)
    - Relasi dengan laporan tangkapan utama
    - Relasi dengan data spesies ikan
    - Informasi kuantitas dan catatan tambahan
    
    Hak Akses:
    - Pengguna yang diautentikasi dapat membuat, memperbarui, dan menghapus
    - Pengguna anonim hanya dapat melihat data
    """
    queryset = CatchDetail._default_manager.all()  # type: ignore
    serializer_class = CatchDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]