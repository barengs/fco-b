from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from django.apps import apps
from io import StringIO, BytesIO
import csv
from .models import FishingArea
from .serializers import FishingAreaSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.http import HttpResponse
import pandas as pd
import xlsxwriter
import numpy as np
from typing import List, Any

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
        responses={
            200: {
                'content': {
                    'text/csv': {
                        'schema': {
                            'type': 'string',
                            'description': 'File CSV template untuk import area penangkapan'
                        }
                    },
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': {
                        'schema': {
                            'type': 'string',
                            'format': 'binary',
                            'description': 'File Excel template untuk import area penangkapan'
                        }
                    }
                }
            }
        }
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
    ViewSet untuk mengelola area penangkapan
    """
    queryset = FishingArea.objects.all()  # type: ignore
    serializer_class = FishingAreaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def import_areas(self, request):
        """
        Import fishing areas from CSV/Excel data provided in the request
        """
        csv_data = request.data.get('csv_data')
        csv_file_upload = request.FILES.get('csv_file')
        clear_existing = request.data.get('clear_existing', False)

        print(f"Starting fishing area CSV/Excel import...")
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
        
        # Process CSV/Excel data
        try:
            if csv_file_upload:
                # Handle file upload
                print(f"✓ Processing as file upload: {getattr(csv_file_upload, 'name', 'unnamed')}, size: {getattr(csv_file_upload, 'size', 'unknown')}")
                
                # Check file extension to determine processing method
                file_name = getattr(csv_file_upload, 'name', '')
                if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                    # Process Excel file
                    print("Processing as Excel file")
                    df = pd.read_excel(csv_file_upload)
                    reader = df.to_dict('records')
                else:
                    # Process CSV file
                    print("Processing as CSV file")
                    file_content = csv_file_upload.read().decode('utf-8')
                    print(f"File content length: {len(file_content)}")
                    print(f"File content preview: {file_content[:100]}...")
                    csv_file = StringIO(file_content)
                    reader = csv.DictReader(csv_file)
            else:
                # Handle string data (CSV only)
                print(f"✓ Processing as string data, length: {len(csv_data) if csv_data else 0}")
                print(f"String content preview: {csv_data[:100] if csv_data else 'None'}...")
                csv_file = StringIO(csv_data)
                reader = csv.DictReader(csv_file)

            print(f"Headers detected: {getattr(reader, 'fieldnames', 'Excel data')}")

            created_count = 0
            updated_count = 0
            error_count = 0
            error_details = []
            
            # Handle both CSV DictReader and Excel dict records
            rows = reader if isinstance(reader, list) else list(reader)
            
            # Initialize row_num to avoid unbound variable error
            row_num = 0
            
            for row_num, row in enumerate(rows, start=1):
                print(f"Processing row {row_num}: {row}")
                try:
                    # Extract data from CSV/Excel row
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
            print(f"DEBUG: Exception in CSV/Excel processing: {str(e)}")
            return Response(
                {'error': f'Error processing CSV/Excel data: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def download_template(self, request):
        """
        Download CSV/Excel template untuk import Fishing Area dengan sample data
        Accepts query parameter 'format' with values 'csv' or 'excel'. Defaults to 'csv'.
        """
        format_type = request.GET.get('format', 'csv').lower()
        
        headers: List[str] = ['nama', 'code', 'deskripsi']
        sample_data: List[List[str]] = [
            ['Area Penangkapan Utara', 'APU-001', 'Wilayah penangkapan ikan di bagian utara perairan Indonesia'],
            ['Area Penangkapan Selatan', 'APS-002', 'Wilayah penangkapan ikan di bagian selatan perairan Indonesia'],
            ['Area Penangkapan Timur', 'APT-003', 'Wilayah penangkapan ikan di bagian timur perairan Indonesia']
        ]
        
        if format_type == 'excel':
            # Create Excel template using xlsxwriter
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Fishing Areas')
            
            # Write headers
            for col, header in enumerate(headers):
                worksheet.write(0, col, header)
            
            # Write sample data
            for row, data_row in enumerate(sample_data, start=1):
                for col, cell_data in enumerate(data_row):
                    worksheet.write(row, col, cell_data)
            
            workbook.close()
            output.seek(0)
            
            # Create response
            response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="fishingarea_import_template.xlsx"'
            
            return response
        else:
            # Create CSV template (default)
            output = StringIO()
            writer = csv.writer(output)

            # Write headers
            writer.writerow(headers)

            # Write sample data
            for row in sample_data:
                writer.writerow(row)

            # Prepare response
            output.seek(0)
            response = HttpResponse(output.getvalue().encode('utf-8'), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="fishingarea_import_template.csv"'

            return response