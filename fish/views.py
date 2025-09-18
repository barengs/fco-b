from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from django.apps import apps
from django.http import HttpResponse
from io import StringIO
import csv
from decimal import Decimal
from .models import FishSpecies, Fish
from .serializers import FishSpeciesSerializer, FishSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

@extend_schema_view(
    list=extend_schema(
        tags=['Fish Species'],
        summary='Daftar semua spesies ikan', 
        description='Mengambil daftar semua spesies ikan'
    ),
    create=extend_schema(
        tags=['Fish Species'],
        summary='Buat spesies ikan', 
        description='Membuat spesies ikan baru'
    ),
    retrieve=extend_schema(
        tags=['Fish Species'],
        summary='Ambil spesies ikan', 
        description='Mengambil spesies ikan tertentu berdasarkan ID'
    ),
    update=extend_schema(
        tags=['Fish Species'],
        summary='Perbarui spesies ikan', 
        description='Memperbarui spesies ikan yang ada'
    ),
    partial_update=extend_schema(
        tags=['Fish Species'],
        summary='Perbarui sebagian spesies ikan', 
        description='Memperbarui sebagian spesies ikan yang ada'
    ),
    destroy=extend_schema(
        tags=['Fish Species'],
        summary='Hapus spesies ikan', 
        description='Menghapus spesies ikan'
    ),
    download_template=extend_schema(
        tags=['Fish Species'],
        summary='Download template CSV untuk import spesies ikan',
        description='Download template CSV untuk import spesies ikan dengan header: name, scientific_name, description',
        responses={200: OpenApiTypes.BINARY}
    ),
    download_fish_template=extend_schema(
        tags=['Fish Species'],
        summary='Download template CSV untuk import ikan',
        description='Download template CSV untuk import ikan dengan header: nama_jenis, nama_ikan, berat_kg, catatan',
        responses={200: OpenApiTypes.BINARY}
    ),
    import_species=extend_schema(
        tags=['Fish Species'],
        summary='Impor spesies ikan dari CSV',
        description='Mengimpor spesies ikan dari data CSV yang dikirim dalam permintaan',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'csv_data': {
                        'type': 'string',
                        'description': 'Data CSV sebagai string dengan header: name,scientific_name,description'
                    },
                    'clear_existing': {
                        'type': 'boolean',
                        'description': 'Jika true, hapus semua spesies ikan yang ada sebelum mengimpor',
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

class FishSpeciesViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola spesies ikan
    """
    queryset = FishSpecies.objects.all()  # type: ignore
    serializer_class = FishSpeciesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def import_species(self, request):
        """
        Import fish species from CSV data provided in the request
        """
        csv_data = request.data.get('csv_data')
        clear_existing = request.data.get('clear_existing', False)
        
        if not csv_data:
            return Response(
                {'error': 'csv_data is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the FishSpecies model dynamically
        FishSpecies = apps.get_model('fish', 'FishSpecies')
        
        # Clear existing data if requested
        if clear_existing:
            FishSpecies._default_manager.all().delete()  # type: ignore
        
        # Process CSV data
        try:
            # Handle different types of csv_data
            if hasattr(csv_data, 'read'):  # File-like object (e.g., InMemoryUploadedFile)
                csv_string = csv_data.read().decode('utf-8')
            elif isinstance(csv_data, bytes):
                csv_string = csv_data.decode('utf-8')
            else:
                csv_string = str(csv_data)
            # Use StringIO to treat string as file-like object
            csv_file = StringIO(csv_string)
            reader = csv.DictReader(csv_file)
            
            created_count = 0
            updated_count = 0
            error_count = 0
            error_details = []
            
            for row_num, row in enumerate(reader, start=1):
                try:
                    # Extract data from CSV row
                    name = row.get('name', '').strip()
                    scientific_name = row.get('scientific_name', '').strip() or None
                    description = row.get('description', '').strip() or None
                    
                    # Validate required fields
                    if not name:
                        error_details.append(f'Row {row_num}: Nama Ikan tidak boleh kosong')
                        error_count += 1
                        continue
                    
                    # Create or update the fish species
                    fish_species, created = FishSpecies._default_manager.get_or_create(  # type: ignore
                        name=name,
                        defaults={
                            'scientific_name': scientific_name,
                            'description': description,
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        # Update existing record if there's new data
                        updated = False
                        if scientific_name and fish_species.scientific_name != scientific_name:
                            fish_species.scientific_name = scientific_name
                            updated = True
                        if description and fish_species.description != description:
                            fish_species.description = description
                            updated = True
                        
                        if updated:
                            fish_species.save()
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

    @action(detail=False, methods=['get'], permission_classes=[])
    def download_template(self, request):
        """
        Download CSV template for importing fish species
        """
        import csv
        from django.http import HttpResponse

        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="fish_species_import_template.csv"'

        # Create CSV writer
        writer = csv.writer(response)

        # Write header row
        writer.writerow(['name', 'scientific_name', 'description'])

        # Write example row
        writer.writerow(['Ikan Lele', 'Clarias batrachus', 'Ikan air tawar yang populer di Indonesia'])

        return response

    @action(detail=False, methods=['get'], permission_classes=[])
    def download_fish_template(self, request):
        """
        Download CSV template for importing fish
        """
        import csv
        from django.http import HttpResponse

        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="fish_import_template.csv"'

        # Create CSV writer
        writer = csv.writer(response)

        # Write header row matching the import fields
        writer.writerow(['nama_jenis', 'nama_ikan', 'berat_kg', 'catatan'])

        # Write example row
        writer.writerow(['Ikan Lele', 'Lele Super', '1.2', 'Ikan berkualitas tinggi'])

        return response


@extend_schema_view(
    list=extend_schema(
        tags=['Fish Species'],
        summary='Daftar semua ikan', 
        description='Mengambil daftar semua ikan'
    ),
    create=extend_schema(
        tags=['Fish Species'],
        summary='Buat ikan', 
        description='Membuat ikan baru'
    ),
    retrieve=extend_schema(
        tags=['Fish Species'],
        summary='Ambil ikan', 
        description='Mengambil ikan tertentu berdasarkan ID'
    ),
    update=extend_schema(
        tags=['Fish Species'],
        summary='Perbarui ikan', 
        description='Memperbarui ikan yang ada'
    ),
    partial_update=extend_schema(
        tags=['Fish Species'],
        summary='Perbarui sebagian ikan', 
        description='Memperbarui sebagian ikan yang ada'
    ),
    destroy=extend_schema(
        tags=['Fish Species'],
        summary='Hapus ikan', 
        description='Menghapus ikan'
    ),
    download_template=extend_schema(
        tags=['Fish Species'],
        summary='Unduh template CSV ikan',
        description='Mengunduh template CSV untuk mengimpor ikan',
        responses={
            (200, 'text/csv'): OpenApiTypes.BINARY
        }
    ),
    import_fish=extend_schema(
        tags=['Fish Species'],
        summary='Impor ikan dari CSV',
        description='Mengimpor ikan dari data CSV yang dikirim dalam permintaan',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'csv_data': {
                        'type': 'string',
                        'description': 'Data CSV sebagai string dengan header: nama_jenis,nama_ikan,berat_kg,catatan'
                    },
                    'clear_existing': {
                        'type': 'boolean',
                        'description': 'Jika true, hapus semua ikan yang ada sebelum mengimpor',
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
class FishViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola ikan individual
    """
    queryset = Fish.objects.all()  # type: ignore
    serializer_class = FishSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Secara opsional membatasi ikan yang dikembalikan berdasarkan spesies tertentu"""
        queryset = Fish.objects.all()  # type: ignore
        species_id = self.request.query_params.get('species_id', None)
        
        if species_id is not None:
            queryset = queryset.filter(species_id=species_id)
            
        return queryset
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def import_fish(self, request):
        """
        Import fish from CSV data provided in the request
        """
        csv_data = request.data.get('csv_data')
        clear_existing = request.data.get('clear_existing', False)
        
        if not csv_data:
            return Response(
                {'error': 'csv_data is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the Fish and FishSpecies models dynamically
        Fish = apps.get_model('fish', 'Fish')
        FishSpecies = apps.get_model('fish', 'FishSpecies')
        
        # Clear existing data if requested
        if clear_existing:
            Fish._default_manager.all().delete()  # type: ignore
        
        # Process CSV data
        try:
            # Handle different types of csv_data
            if hasattr(csv_data, 'read'):  # File-like object (e.g., InMemoryUploadedFile)
                csv_string = csv_data.read().decode('utf-8')
            elif isinstance(csv_data, bytes):
                csv_string = csv_data.decode('utf-8')
            else:
                csv_string = str(csv_data)
            # Use StringIO to treat string as file-like object
            csv_file = StringIO(csv_string)
            reader = csv.DictReader(csv_file)
            
            created_count = 0
            updated_count = 0
            error_count = 0
            error_details = []
            
            for row_num, row in enumerate(reader, start=1):
                try:
                    # Extract data from CSV row
                    species_name = row.get('nama_jenis', '').strip()
                    name = row.get('nama_ikan', '').strip() or None
                    weight = row.get('berat_kg', '').strip()
                    notes = row.get('catatan', '').strip() or None
                    
                    # Validate required fields
                    if not species_name:
                        error_details.append(f'Row {row_num}: Missing species_name')
                        error_count += 1
                        continue
                    
                    # Find the fish species
                    try:
                        species = FishSpecies._default_manager.get(name=species_name)  # type: ignore
                    except FishSpecies.DoesNotExist:  # type: ignore
                        error_details.append(f'Row {row_num}: Fish species "{species_name}" not found')
                        error_count += 1
                        continue
                    
                    # Convert weight to Decimal if provided
                    weight_decimal = None

                    if weight:
                        try:
                            weight_decimal = Decimal(weight)
                        except (ValueError, decimal.InvalidOperation):
                            error_details.append(f'Row {row_num}: Invalid weight value "{weight}"')
                            error_count += 1
                            continue
                    
                    # Create fish instance
                    fish = Fish(
                        species=species,
                        name=name,
                        weight=weight_decimal,
                        notes=notes
                    )
                    
                    try:
                        fish.full_clean()  # Validate model fields
                        fish.save()
                        created_count += 1
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

