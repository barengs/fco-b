from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from django.apps import apps
from io import StringIO
import csv
from .models import FishSpecies, Fish
from .serializers import FishSpeciesSerializer, FishSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

@extend_schema_view(
    list=extend_schema(summary='Daftar semua spesies ikan', description='Mengambil daftar semua spesies ikan'),
    create=extend_schema(summary='Buat spesies ikan', description='Membuat spesies ikan baru'),
    retrieve=extend_schema(summary='Ambil spesies ikan', description='Mengambil spesies ikan tertentu berdasarkan ID'),
    update=extend_schema(summary='Perbarui spesies ikan', description='Memperbarui spesies ikan yang ada'),
    partial_update=extend_schema(summary='Perbarui sebagian spesies ikan', description='Memperbarui sebagian spesies ikan yang ada'),
    destroy=extend_schema(summary='Hapus spesies ikan', description='Menghapus spesies ikan'),
    import_species=extend_schema(
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
                    scientific_name = row.get('scientific_name', '').strip() or None
                    description = row.get('description', '').strip() or None
                    
                    # Validate required fields
                    if not name:
                        error_details.append(f'Row {row_num}: Missing name')
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


@extend_schema_view(
    list=extend_schema(summary='Daftar semua ikan', description='Mengambil daftar semua ikan'),
    create=extend_schema(summary='Buat ikan', description='Membuat ikan baru'),
    retrieve=extend_schema(summary='Ambil ikan', description='Mengambil ikan tertentu berdasarkan ID'),
    update=extend_schema(summary='Perbarui ikan', description='Memperbarui ikan yang ada'),
    partial_update=extend_schema(summary='Perbarui sebagian ikan', description='Memperbarui sebagian ikan yang ada'),
    destroy=extend_schema(summary='Hapus ikan', description='Menghapus ikan'),
    import_fish=extend_schema(
        summary='Impor ikan dari CSV',
        description='Mengimpor ikan dari data CSV yang dikirim dalam permintaan',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'csv_data': {
                        'type': 'string',
                        'description': 'Data CSV sebagai string dengan header: species_name,name,length,weight,notes'
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
                    species_name = row.get('species_name', '').strip()
                    name = row.get('name', '').strip() or None
                    length = row.get('length', '').strip()
                    weight = row.get('weight', '').strip()
                    notes = row.get('notes', '').strip() or None
                    
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
                    
                    # Convert length and weight to Decimal if provided
                    length_decimal = None
                    weight_decimal = None
                    
                    if length:
                        try:
                            length_decimal = float(length)
                        except ValueError:
                            error_details.append(f'Row {row_num}: Invalid length value "{length}"')
                            error_count += 1
                            continue
                    
                    if weight:
                        try:
                            weight_decimal = float(weight)
                        except ValueError:
                            error_details.append(f'Row {row_num}: Invalid weight value "{weight}"')
                            error_count += 1
                            continue
                    
                    # Create fish instance
                    fish = Fish(
                        species=species,
                        name=name,
                        length=length_decimal,
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