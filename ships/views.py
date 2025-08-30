from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.apps import apps
from io import StringIO
import csv
from .models import Ship
from .serializers import ShipSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.utils import OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

@extend_schema_view(
    list=extend_schema(summary='Daftar semua kapal', description='Mengambil daftar semua kapal penangkap ikan'),
    create=extend_schema(summary='Buat kapal', description='Membuat kapal penangkap ikan baru'),
    retrieve=extend_schema(summary='Ambil kapal', description='Mengambil kapal tertentu berdasarkan ID'),
    update=extend_schema(summary='Perbarui kapal', description='Memperbarui kapal yang ada'),
    partial_update=extend_schema(summary='Perbarui sebagian kapal', description='Memperbarui sebagian kapal yang ada'),
    destroy=extend_schema(summary='Hapus kapal', description='Menghapus kapal'),
    catch_reports=extend_schema(summary='Dapatkan laporan tangkapan kapal', description='Mengambil semua laporan tangkapan untuk kapal tertentu'),
    import_ships=extend_schema(
        summary='Impor kapal dari CSV',
        description='Mengimpor kapal dari data CSV yang dikirim dalam permintaan',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'csv_data': {
                        'type': 'string',
                        'description': 'Data CSV sebagai string dengan header: name,registration_number,owner_name,captain_name,length,width,gross_tonnage,year_built,home_port,active'
                    },
                    'clear_existing': {
                        'type': 'boolean',
                        'description': 'Jika true, hapus semua kapal yang ada sebelum mengimpor',
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
class ShipViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola kapal penangkap ikan
    """
    queryset = Ship.objects.select_related('owner', 'captain').prefetch_related('quotas').all()  # type: ignore
    serializer_class = ShipSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def catch_reports(self, request, pk=None):
        """Dapatkan semua laporan tangkapan untuk kapal tertentu"""
        ship = self.get_object()
        catches = ship.catch_reports.all()
        from catches.serializers import FishCatchSerializer
        serializer = FishCatchSerializer(catches, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def import_ships(self, request):
        """
        Import ships from CSV data provided in the request
        """
        csv_data = request.data.get('csv_data')
        clear_existing = request.data.get('clear_existing', False)
        
        if not csv_data:
            return Response(
                {'error': 'csv_data is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the Ship, Owner, and Captain models dynamically
        Ship = apps.get_model('ships', 'Ship')
        Owner = apps.get_model('owners', 'Owner')
        Captain = apps.get_model('owners', 'Captain')
        
        # Clear existing data if requested
        if clear_existing:
            Ship._default_manager.all().delete()  # type: ignore
        
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
                    registration_number = row.get('registration_number', '').strip()
                    owner_name = row.get('owner_name', '').strip()
                    captain_name = row.get('captain_name', '').strip() or None
                    length = row.get('length', '').strip()
                    width = row.get('width', '').strip()
                    gross_tonnage = row.get('gross_tonnage', '').strip()
                    year_built = row.get('year_built', '').strip()
                    home_port = row.get('home_port', '').strip() or None
                    active = row.get('active', 'true').strip().lower()
                    
                    # Validate required fields
                    if not name:
                        error_details.append(f'Row {row_num}: Missing name')
                        error_count += 1
                        continue
                    
                    if not registration_number:
                        error_details.append(f'Row {row_num}: Missing registration_number')
                        error_count += 1
                        continue
                        
                    if not owner_name:
                        error_details.append(f'Row {row_num}: Missing owner_name')
                        error_count += 1
                        continue
                    
                    # Find the owner
                    try:
                        owner = Owner._default_manager.get(name=owner_name)  # type: ignore
                    except Owner.DoesNotExist:  # type: ignore
                        error_details.append(f'Row {row_num}: Owner "{owner_name}" not found')
                        error_count += 1
                        continue
                    
                    # Find the captain if provided
                    captain = None
                    if captain_name:
                        try:
                            captain = Captain._default_manager.get(name=captain_name)  # type: ignore
                        except Captain.DoesNotExist:  # type: ignore
                            error_details.append(f'Row {row_num}: Captain "{captain_name}" not found')
                            error_count += 1
                            continue
                    
                    # Convert numeric values if provided
                    length_decimal = None
                    width_decimal = None
                    gross_tonnage_decimal = None
                    year_built_int = None
                    
                    if length:
                        try:
                            length_decimal = float(length)
                        except ValueError:
                            error_details.append(f'Row {row_num}: Invalid length value "{length}"')
                            error_count += 1
                            continue
                    
                    if width:
                        try:
                            width_decimal = float(width)
                        except ValueError:
                            error_details.append(f'Row {row_num}: Invalid width value "{width}"')
                            error_count += 1
                            continue
                    
                    if gross_tonnage:
                        try:
                            gross_tonnage_decimal = float(gross_tonnage)
                        except ValueError:
                            error_details.append(f'Row {row_num}: Invalid gross_tonnage value "{gross_tonnage}"')
                            error_count += 1
                            continue
                    
                    if year_built:
                        try:
                            year_built_int = int(year_built)
                        except ValueError:
                            error_details.append(f'Row {row_num}: Invalid year_built value "{year_built}"')
                            error_count += 1
                            continue
                    
                    # Convert active to boolean
                    active_bool = active in ['true', '1', 'yes', 'y']
                    
                    # Create or update the ship
                    ship, created = Ship._default_manager.get_or_create(  # type: ignore
                        registration_number=registration_number,
                        defaults={
                            'name': name,
                            'owner': owner,
                            'captain': captain,
                            'length': length_decimal,
                            'width': width_decimal,
                            'gross_tonnage': gross_tonnage_decimal,
                            'year_built': year_built_int,
                            'home_port': home_port,
                            'active': active_bool,
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        # Update existing record if there's new data
                        updated = False
                        if ship.name != name:
                            ship.name = name
                            updated = True
                        if ship.owner != owner:
                            ship.owner = owner
                            updated = True
                        if ship.captain != captain:
                            ship.captain = captain
                            updated = True
                        if ship.length != length_decimal:
                            ship.length = length_decimal
                            updated = True
                        if ship.width != width_decimal:
                            ship.width = width_decimal
                            updated = True
                        if ship.gross_tonnage != gross_tonnage_decimal:
                            ship.gross_tonnage = gross_tonnage_decimal
                            updated = True
                        if ship.year_built != year_built_int:
                            ship.year_built = year_built_int
                            updated = True
                        if ship.home_port != home_port:
                            ship.home_port = home_port
                            updated = True
                        if ship.active != active_bool:
                            ship.active = active_bool
                            updated = True
                        
                        if updated:
                            ship.save()
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


@extend_schema(
    summary='Periksa registrasi kapal',
    description='Memeriksa apakah nomor registrasi kapal terdaftar dalam sistem',
    parameters=[
        OpenApiParameter(
            name='registration_number', 
            description='Nomor registrasi kapal untuk diperiksa', 
            required=True, 
            type=str
        ),
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'exists': {'type': 'boolean'},
                'ship': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'registration_number': {'type': 'string'},
                        'owner': {'type': 'string'},
                        'captain': {'type': 'string', 'nullable': True},
                    }
                }
            }
        },
        404: {
            'type': 'object',
            'properties': {
                'exists': {'type': 'boolean', 'example': False},
                'message': {'type': 'string', 'example': 'Nomor registrasi tidak ditemukan'}
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def check_ship_registration(request):
    """
    Endpoint untuk memeriksa apakah nomor registrasi kapal terdaftar
    """
    registration_number = request.GET.get('registration_number')
    
    if not registration_number:
        return Response({
            'exists': False,
            'message': 'Parameter registration_number diperlukan'
        }, status=400)
    
    try:
        ship = Ship._default_manager.select_related('owner', 'captain').get(registration_number=registration_number)
        return Response({
            'exists': True,
            'ship': {
                'id': ship.id,
                'name': ship.name,
                'registration_number': ship.registration_number,
                'owner': str(ship.owner),
                'captain': str(ship.captain) if ship.captain else None,
            }
        })
    except ObjectDoesNotExist:
        return Response({
            'exists': False,
            'message': 'Nomor registrasi tidak ditemukan'
        }, status=404)