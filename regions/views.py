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
                        'description': 'Data CSV sebagai string dengan header: name,code,description,boundary_coordinates'
                    },
                    'clear_existing': {
                        'type': 'boolean',
                        'description': 'Jika true, hapus semua area penangkapan yang ada sebelum mengimpor',
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
        csv_data = request.data.get('csv_data')
        clear_existing = request.data.get('clear_existing', False)
        
        if not csv_data:
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
        try:
            # Use StringIO to treat string as file-like object
            csv_file = StringIO(csv_data)
            reader = csv.DictReader(csv_file)
            
            created_count = 0
            updated_count = 0
            error_count = 0
            error_details = []
            
            for row_num, row in enumerate(reader, start=1):
                try:
                    # Extract data from CSV row
                    name = row.get('name', '').strip()
                    code = row.get('code', '').strip()
                    description = row.get('description', '').strip() or None
                    boundary_coordinates = row.get('boundary_coordinates', '').strip() or None
                    
                    # Validate required fields
                    if not name:
                        error_details.append(f'Row {row_num}: Missing name')
                        error_count += 1
                        continue
                    
                    if not code:
                        error_details.append(f'Row {row_num}: Missing code')
                        error_count += 1
                        continue
                    
                    # Create or update the fishing area
                    fishing_area, created = FishingArea._default_manager.get_or_create(  # type: ignore
                        code=code,
                        defaults={
                            'name': name,
                            'description': description,
                            'boundary_coordinates': boundary_coordinates,
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        # Update existing record if there's new data
                        updated = False
                        if fishing_area.name != name:
                            fishing_area.name = name
                            updated = True
                        if fishing_area.description != description:
                            fishing_area.description = description
                            updated = True
                        if fishing_area.boundary_coordinates != boundary_coordinates:
                            fishing_area.boundary_coordinates = boundary_coordinates
                            updated = True
                        
                        if updated:
                            fishing_area.save()
                            updated_count += 1
            
                except ValidationError as e:
                    error_details.append(f'Row {row_num}: Validation error - {str(e)}')
                    error_count += 1
                except Exception as e:
                    error_details.append(f'Row {row_num}: Unexpected error - {str(e)}')
                    error_count += 1
            
            return Response({
                'message': 'Import completed',
                'created': created_count,
                'updated': updated_count,
                'errors': error_count,
                'error_details': error_details if error_details else None
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error processing CSV data: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )