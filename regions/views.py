from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from django.apps import apps
from io import StringIO
import csv
from .models import FishingArea
from .serializers import FishingAreaSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.http import HttpResponse

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
    import_areas=extend_schema(
        tags=['Fishing Areas'],
        summary='Impor area penangkapan dari CSV',
        description='Mengimpor area penangkapan dari data CSV yang dikirim dalam permintaan',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'csv_data': {
                        'type': 'string',
                        'description': 'Data CSV sebagai string dengan header: nama,code,deskripsi'
                    },
                    'clear_existing': {
                        'type': 'boolean',
                        'deskripsi': 'Jika true, hapus semua area penangkapan yang ada sebelum mengimpor',
                        'default': False
                    }
                },
                'required': ['csv_data']
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
    ViewSet untuk mengelola area penangkapan
    """
    queryset = FishingArea.objects.all()  # type: ignore
    serializer_class = FishingAreaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def import_areas(self, request):
        """
        Import fishing areas from CSV data provided in the request
        """
        print(f"DEBUG: Request data keys: {list(request.data.keys())}")
        csv_data = request.data.get('csv_data')
        clear_existing = request.data.get('clear_existing', False)
        print(f"DEBUG: csv_data type: {type(csv_data)}, length: {len(csv_data) if csv_data else 0}")
        print(f"DEBUG: clear_existing: {clear_existing}")

        if not csv_data:
            print("DEBUG: csv_data is missing or empty")
            return Response(
                {'error': 'csv_data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the FishingArea model dynamically
        FishingArea = apps.get_model('regions', 'FishingArea')
        
        # Clear existing data if requested
        if clear_existing:
            FishingArea._default_manager.all().delete()  # type: ignore
        
        # Process CSV data
        print(f"DEBUG: About to process csv_data, type: {type(csv_data)}")
        try:
            print("DEBUG: Processing CSV data")
            # Handle different types of csv_data
            if hasattr(csv_data, 'read'):  # File-like object (e.g., InMemoryUploadedFile)
                print("DEBUG: csv_data has read method")
                csv_string = csv_data.read().decode('utf-8')
                print("DEBUG: Read csv_data from file-like object")
            elif isinstance(csv_data, bytes):
                csv_string = csv_data.decode('utf-8')
                print("DEBUG: Decoded csv_data from bytes to string")
            else:
                csv_string = str(csv_data)
                print("DEBUG: Converted csv_data to string")
            print(f"DEBUG: csv_string type: {type(csv_string)}")
            # Use StringIO to treat string as file-like object
            print(f"DEBUG: Raw csv_string: {repr(csv_string)}")
            csv_file = StringIO(csv_string)
            reader = csv.DictReader(csv_file)
            print(f"DEBUG: CSV fieldnames: {reader.fieldnames}")

            created_count = 0
            updated_count = 0
            error_count = 0
            error_details = []
            
            for row_num, row in enumerate(reader, start=1):
                print(f"DEBUG: Processing row {row_num}: {row}")
                try:
                    # Extract data from CSV row
                    nama = row.get('nama', '').strip()
                    code = row.get('code', '').strip()
                    deskripsi = row.get('deskripsi', '').strip() or None
                    print(f"DEBUG: Extracted - nama: '{nama}', code: '{code}', deskripsi: '{deskripsi}'")

                    # Validate required fields
                    if not nama:
                        print(f"DEBUG: Row {row_num}: Missing nama")
                        error_details.append(f'Row {row_num}: Missing nama')
                        error_count += 1
                        continue

                    if not code:
                        print(f"DEBUG: Row {row_num}: Missing code")
                        error_details.append(f'Row {row_num}: Missing code')
                        error_count += 1
                        continue
                    
                    # Create or update the fishing area
                    fishing_area, created = FishingArea._default_manager.get_or_create(  # type: ignore
                        code=code,
                        defaults={
                            'nama': nama,
                            'deskripsi': deskripsi,
                    
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        # Update existing record if there's new data
                        updated = False
                        if fishing_area.nama != nama:
                            fishing_area.nama = nama
                            updated = True
                        if fishing_area.deskripsi != deskripsi:
                            fishing_area.deskripsi = deskripsi
                            updated = True
                        
                        if updated:
                            fishing_area.save()
                            updated_count += 1
            
                except ValidationError as e:
                    print(f"DEBUG: Row {row_num}: Validation error - {str(e)}")
                    error_details.append(f'Row {row_num}: Validation error - {str(e)}')
                    error_count += 1
                except Exception as e:
                    print(f"DEBUG: Row {row_num}: Unexpected error - {str(e)}")
                    error_details.append(f'Row {row_num}: Unexpected error - {str(e)}')
                    error_count += 1
            
            print(f"DEBUG: Import completed - created: {created_count}, updated: {updated_count}, errors: {error_count}")
            return Response({
                'message': 'Import completed',
                'created': created_count,
                'updated': updated_count,
                'errors': error_count,
                'error_details': error_details if error_details else None
            })

        except Exception as e:
            print(f"DEBUG: Exception in CSV processing: {str(e)}")
            return Response(
                {'error': f'Error processing CSV data: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def download_template(self, request):
        """
        Download CSV template untuk import Fishing Area
        """
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="fishingarea_template.csv"'

        writer = csv.writer(response)
        # Tulis header sesuai kebutuhan import
        writer.writerow(["nama", "code", "deskripsi"])

        return response


