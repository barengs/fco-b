"""
Region Views (Presentation Layer)
API Views untuk manajemen wilayah penangkapan (WPP).
Menggunakan Application Layer untuk bisnis logic.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import FishingArea
from .serializers import FishingAreaSerializer
from .application.region_service import RegionApplicationService


@extend_schema_view(
    list=extend_schema(
        tags=['Fishing Areas'],
        summary='Daftar semua area penangkapan',
        description='Mengambil daftar semua area penangkapan'
    ),
    create=extend_schema(
        tags=['Fishing Areas'],
        summary='Buat area penangkapan',
        description='Membuat area penangkapan baru'
    ),
    retrieve=extend_schema(
        tags=['Fishing Areas'],
        summary='Ambil area penangkapan',
        description='Mengambil area penangkapan tertentu berdasarkan ID'
    ),
    update=extend_schema(
        tags=['Fishing Areas'],
        summary='Perbarui area penangkapan',
        description='Memperbarui area penangkapan yang ada'
    ),
    partial_update=extend_schema(
        tags=['Fishing Areas'],
        summary='Perbarui sebagian area penangkapan',
        description='Memperbarui sebagian area penangkapan yang ada'
    ),
    destroy=extend_schema(
        tags=['Fishing Areas'],
        summary='Hapus area penangkapan',
        description='Menghapus area penangkapan'
    ),
    download_template=extend_schema(
        tags=['Fishing Areas'],
        summary='Download template CSV/Excel area penangkapan',
        description='Download template CSV/Excel dengan header dan sample data untuk import area penangkapan',
    ),
    import_areas=extend_schema(
        tags=['Fishing Areas'],
        summary='Impor area penangkapan dari CSV/Excel',
        description='Mengimpor area penangkapan dari data CSV/Excel yang dikirim dalam permintaan',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'csv_file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'File CSV/Excel upload dengan header: nama,code,deskripsi'
                    },
                    'csv_data': {
                        'type': 'string',
                        'description': 'Data CSV sebagai string dengan header: nama,code,deskripsi'
                    },
                    'clear_existing': {
                        'type': 'boolean',
                        'description': 'Jika true, hapus semua area penangkapan yang ada sebelum mengimpor',
                        'default': False
                    }
                }
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'created': {'type': 'integer'},
                    'updated': {'type': 'integer'},
                    'errors': {'type': 'integer'},
                    'error_details': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                }
            }
        }
    )
)
class FishingAreaViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola area penangkapan (WPP).
    Delegates business logic to RegionApplicationService.
    """
    queryset = FishingArea.objects.all().order_by('code')
    serializer_class = FishingAreaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.region_service = RegionApplicationService()

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def download_template(self, request):
        """
        Download CSV/Excel template untuk import area penangkapan.
        Accepts query parameter 'format' with values 'csv' or 'excel'. Defaults to 'csv'.
        """
        import csv
        from io import StringIO, BytesIO
        from django.http import HttpResponse
        import xlsxwriter

        format_type = (
            request.GET.get('type') or request.GET.get('format', 'csv')
        ).lower()

        headers = ['nama', 'code', 'deskripsi']
        sample_data = [
            ['WPPNRI 571', '571', 'Perairan Selat Malaka dan Laut Andaman'],
            ['WPPNRI 572', '572', 'Perairan Samudera Hindia sebelah Barat Sumatera dan Selat Sunda'],
            ['WPPNRI 573', '573', 'Perairan Samudera Hindia sebelah Selatan Jawa hingga sebelah Selatan Nusa Tenggara'],
            ['WPPNRI 711', '711', 'Perairan Selat Karimata, Laut Natuna, dan Laut Natuna Utara'],
            ['WPPNRI 712', '712', 'Perairan Laut Jawa'],
            ['WPPNRI 713', '713', 'Perairan Selat Makassar, Teluk Bone, Laut Flores, dan Laut Bali']
        ]

        if format_type == 'excel':
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Fishing Areas')

            for col, header in enumerate(headers):
                worksheet.write(0, col, header)

            for row, data_row in enumerate(sample_data, start=1):
                for col, cell_data in enumerate(data_row):
                    worksheet.write(row, col, cell_data)

            workbook.close()
            output.seek(0)

            response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="fishingarea_import_template.xlsx"'
            return response
        else:
            output = StringIO()
            writer = csv.writer(output)

            writer.writerow(headers)

            for row in sample_data:
                writer.writerow(row)

            output.seek(0)
            response = HttpResponse(output.getvalue().encode('utf-8'), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="fishingarea_import_template.csv"'

            return response

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def import_areas(self, request):
        """
        Import fishing areas from CSV/Excel data provided in the request
        """
        csv_data = request.data.get('csv_data')
        csv_file_upload = request.FILES.get('csv_file')
        clear_existing = request.data.get('clear_existing', False)

        if not csv_data and not csv_file_upload:
            return Response(
                {'error': 'Pilih atau unggah file CSV terlebih dahulu'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = self.region_service.import_regions_from_csv(
            csv_data=csv_data,
            clear_existing=clear_existing
        )

        return Response(result)
