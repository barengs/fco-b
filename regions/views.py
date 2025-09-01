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
    download_template=extend_schema(
        tags=['Fishing Areas'],
        summary='Download template CSV area penangkapan',
        description='Download template CSV dengan header dan sample data untuk import area penangkapan',
        responses={
            200: {
                'content': {
                    'text/csv': {
                        'schema': {
                            'type': 'string',
                            'description': 'File CSV template untuk import area penangkapan'
                        }
                    }
                }
            }
        }
    ),
    import_areas=extend_schema(
        tags=['Fishing Areas'],
        summary='Impor area penangkapan dari CSV',
        description='Mengimpor area penangkapan dari data CSV yang dikirim dalam permintaan',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'csv_file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'File CSV upload dengan header: nama,code,deskripsi'
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
        csv_data = request.data.get('csv_data')
        csv_file_upload = request.FILES.get('csv_file')
        clear_existing = request.data.get('clear_existing', False)

        print(f"Starting fishing area CSV import...")
        print(f"Request data keys: {list(request.data.keys())}")
        print(f"Request FILES keys: {list(request.FILES.keys())}")

        # Handle the case where csv_data is sent as a file (InMemoryUploadedFile)
        if hasattr(csv_data, 'read'):  # Check if csv_data is a file-like object
            print("Detected csv_data as file-like object, switching to file processing mode")
            csv_file_upload = csv_data
            csv_data = None

        if not csv_data and not csv_file_upload:
            return Response(
                {'error': 'csv_data (string) or csv_file (upload) is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the FishingArea model dynamically
        FishingArea = apps.get_model('regions', 'FishingArea')
        
        # Clear existing data if requested
        if clear_existing:
            FishingArea._default_manager.all().delete()  # type: ignore
        
        # Process CSV data
        try:
            if csv_file_upload:
                # Handle file upload
                print(f"✓ Processing as file upload: {getattr(csv_file_upload, 'name', 'unnamed')}, size: {getattr(csv_file_upload, 'size', 'unknown')}")
                file_content = csv_file_upload.read().decode('utf-8')
                print(f"File content length: {len(file_content)}")
                print(f"File content preview: {file_content[:100]}...")
                csv_file = StringIO(file_content)
                reader = csv.DictReader(csv_file)
            else:
                # Handle string data
                print(f"✓ Processing as string data, length: {len(csv_data) if csv_data else 0}")
                print(f"String content preview: {csv_data[:100] if csv_data else 'None'}...")
                csv_file = StringIO(csv_data)
                reader = csv.DictReader(csv_file)

            print(f"Headers detected: {reader.fieldnames}")

            created_count = 0
            updated_count = 0
            error_count = 0
            error_details = []
            
            for row_num, row in enumerate(reader, start=1):
                print(f"Processing row {row_num}: {row}")
                try:
                    # Extract data from CSV row
                    nama = row.get('nama', '').strip()
                    code = row.get('code', '').strip()
                    deskripsi = row.get('deskripsi', '').strip() or None
                    print(f"  Extracted data: nama='{nama}', code='{code}', deskripsi='{deskripsi}'")

                    # Validate required fields
                    if not nama:
                        print(f"  ✗ Row {row_num}: Missing nama")
                        error_details.append(f'Row {row_num}: Missing nama')
                        error_count += 1
                        continue

                    if not code:
                        print(f"  ✗ Row {row_num}: Missing code")
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
                        print(f"  ✓ Created new fishing area: {fishing_area.nama} ({fishing_area.code})")
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
                            print(f"  ✓ Updated existing fishing area: {fishing_area.nama} ({fishing_area.code})")
                        else:
                            print(f"  - No changes needed for fishing area: {fishing_area.nama} ({fishing_area.code})")
            
                except ValidationError as e:
                    print(f"  ✗ Row {row_num}: Validation error - {str(e)}")
                    error_details.append(f'Row {row_num}: Validation error - {str(e)}')
                    error_count += 1
                except Exception as e:
                    print(f"  ✗ Row {row_num}: Unexpected error - {str(e)}")
                    error_details.append(f'Row {row_num}: Unexpected error - {str(e)}')
                    error_count += 1

            print(f"\nImport Summary:")
            print(f"  Total rows processed: {row_num}")
            print(f"  Created: {created_count}")
            print(f"  Updated: {updated_count}")
            print(f"  Errors: {error_count}")
            if error_details:
                print(f"  Error details: {error_details}")

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
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def download_template(self, request):
        """
        Download CSV template untuk import Fishing Area dengan sample data
        """
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)

        # Write headers
        headers = [
            'nama',
            'code',
            'deskripsi'
        ]
        writer.writerow(headers)

        # Write sample data
        sample_data = [
            'Area Penangkapan Utara',
            'APU-001',
            'Wilayah penangkapan ikan di bagian utara perairan Indonesia'
        ]
        writer.writerow(sample_data)

        # Additional sample rows
        sample_data2 = [
            'Area Penangkapan Selatan',
            'APS-002',
            'Wilayah penangkapan ikan di bagian selatan perairan Indonesia'
        ]
        writer.writerow(sample_data2)

        sample_data3 = [
            'Area Penangkapan Timur',
            'APT-003',
            'Wilayah penangkapan ikan di bagian timur perairan Indonesia'
        ]
        writer.writerow(sample_data3)

        # Prepare response
        output.seek(0)
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="fishingarea_import_template.csv"'

        return response


