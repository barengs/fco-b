from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.apps import apps
from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField, Avg, Q
from django.db.models.functions import TruncMonth
from io import StringIO, BytesIO
import csv
from datetime import datetime, timedelta
import json
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from .models import Ship
from .serializers import ShipSerializer, AIRecommendationResponseSerializer

@extend_schema_view(
    list=extend_schema(
        tags=['Ships'],
        summary='Daftar semua kapal', 
        description='Mengambil daftar semua kapal penangkap ikan'
    ),
    create=extend_schema(
        tags=['Ships'],
        summary='Buat kapal', 
        description='Membuat kapal penangkap ikan baru'
    ),
    retrieve=extend_schema(
        tags=['Ships'],
        summary='Ambil kapal', 
        description='Mengambil kapal tertentu berdasarkan ID'
    ),
    update=extend_schema(
        tags=['Ships'],
        summary='Perbarui kapal', 
        description='Memperbarui kapal yang ada'
    ),
    partial_update=extend_schema(
        tags=['Ships'],
        summary='Perbarui sebagian kapal', 
        description='Memperbarui sebagian kapal yang ada'
    ),
    destroy=extend_schema(
        tags=['Ships'],
        summary='Hapus kapal', 
        description='Menghapus kapal'
    ),
    catch_reports=extend_schema(
        tags=['Ships'],
        summary='Dapatkan laporan tangkapan kapal', 
        description='Mengambil semua laporan tangkapan untuk kapal tertentu'
    ),
    download_template=extend_schema(
        tags=['Ships'],
        summary='Download template CSV kapal',
        description='Download template CSV dengan header yang sesuai untuk import kapal',
        responses={
            200: {
                'content': {
                    'text/csv': {
                        'schema': {
                            'type': 'string',
                            'description': 'File CSV template untuk import kapal'
                        }
                    }
                }
            }
        }
    ),
    import_ships=extend_schema(
        tags=['Ships'],
        summary='Impor kapal dari CSV',
        description='Mengimpor kapal dari data CSV yang dikirim dalam permintaan',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'csv_file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'File CSV upload dengan header dalam bahasa Inggris atau Indonesia'
                    },
                    'csv_data': {
                        'type': 'string',
                        'description': 'Data CSV sebagai string dengan header dalam bahasa Inggris atau Indonesia. Header Inggris: name,registration_number,length,width,gross_tonnage,year_built,home_port. Header Indonesia: nama_kapal,no_buku_kapal,panjang,lebar,tonase_kotor,tahun_dibuat,pelabuhan_asal.'
                    },
                    'clear_existing': {
                        'type': 'boolean',
                        'description': 'Jika true, hapus semua kapal yang ada sebelum mengimpor',
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
    ),
    download_template=extend_schema(
        tags=['Ships'],
        summary='Unduh template CSV untuk impor kapal',
        description='Mengunduh template CSV yang dapat digunakan untuk mengimpor data kapal',
        responses={
            (200, 'text/csv'): OpenApiParameter(
                name='Content-Disposition',
                type=str,
                location=OpenApiParameter.HEADER,
                description='attachment; filename="ship_import_template.csv"'
            )
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
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def download_template(self, request):
        """
        Download CSV template for ship import
        """
        import csv
        from django.http import HttpResponse
        
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ship_import_template.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow([
            'name',
            'registration_number', 
            'owner_name',
            'captain_name',
            'length',
            'width',
            'gross_tonnage',
            'year_built',
            'home_port',
            'active'
        ])
        
        # Write example row
        writer.writerow([
            'Nama Kapal',
            'REG001',
            'Nama Pemilik',
            'Nama Nahkoda',
            '20.5',
            '5.2',
            '100.5',
            '2020',
            'Pelabuhan Asal',
            'true'
        ])
        
        return response
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def import_ships(self, request):
        """
        Import ships from CSV data provided in the request
        """
        csv_data = request.data.get('csv_data')
        csv_file_upload = request.FILES.get('csv_file')
        csv_data_file = request.FILES.get('csv_data')  # Handle case where csv_data is sent as file
        clear_existing = request.data.get('clear_existing', False)

        print(f"Request data keys: {list(request.data.keys())}")
        print(f"Request FILES keys: {list(request.FILES.keys())}")
        print(f"csv_data type: {type(csv_data)}")
        print(f"csv_file_upload type: {type(csv_file_upload)}")
        print(f"csv_data_file type: {type(csv_data_file)}")

        # Handle the case where csv_data is sent as a file (InMemoryUploadedFile)
        if csv_data_file and isinstance(csv_data_file, type(csv_file_upload)):
            print("Detected csv_data as file upload, switching to file processing mode")
            csv_file_upload = csv_data_file
            csv_data = None
        elif csv_data and hasattr(csv_data, 'read'):  # Check if csv_data is a file-like object
            print("Detected csv_data as file-like object, switching to file processing mode")
            csv_file_upload = csv_data
            csv_data = None

        if not csv_data and not csv_file_upload:
            return Response(
                {'error': 'csv_data (string) or csv_file (upload) is required'},
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
            
            created_count = 0
            updated_count = 0
            error_count = 0
            error_details = []

            print(f"Starting CSV import process...")
            print(f"Headers detected: {reader.fieldnames}")

            for row_num, row in enumerate(reader, start=1):
                print(f"Processing row {row_num}: {row}")
                try:
                    # Extract data from CSV row - support both English and Indonesian headers
                    name = row.get('name', row.get('nama_kapal', '')).strip()
                    registration_number = row.get('registration_number', row.get('no_buku_kapal', '')).strip()
                    owner_name = row.get('owner_name', row.get('nama_pemilik', '')).strip()
                    captain_name = row.get('captain_name', row.get('nama_nahkoda', '')).strip() or None
                    length = row.get('length', row.get('panjang', '')).strip()
                    width = row.get('width', row.get('lebar', '')).strip()
                    gross_tonnage = row.get('gross_tonnage', row.get('tonase_kotor', '')).strip()
                    year_built = row.get('year_built', row.get('tahun_dibuat', '')).strip()
                    home_port = row.get('home_port', row.get('pelabuhan_asal', '')).strip() or None
                    active = row.get('active', row.get('aktif', 'true')).strip().lower()
                    # Default to True if not provided
                    active_bool = active in ['true', '1', 'yes', 'y'] if active else True

                    print(f"  Extracted data: name='{name}', reg_num='{registration_number}', owner='{owner_name}', length='{length}', active={active_bool}")
                    
                    # Validate required fields
                    if not name:
                        error_details.append(f'Row {row_num}: Missing name/nama_kapal')
                        error_count += 1
                        continue

                    if not registration_number:
                        error_details.append(f'Row {row_num}: Missing registration_number/no_buku_kapal')
                        error_count += 1
                        continue

                    # Handle owner - create default if not provided
                    if not owner_name:
                        owner_name = 'Default Owner'

                    try:
                        owner = Owner._default_manager.get_or_create(
                            full_name=owner_name,
                            defaults={'owner_type': 'individual'}  # Set default owner type
                        )[0]  # type: ignore
                    except Exception as e:
                        error_details.append(f'Row {row_num}: Could not create/find owner "{owner_name}" - {str(e)}')
                        error_count += 1
                        continue
                    
                    # Find the captain if provided (optional)
                    captain = None
                    if captain_name:
                        try:
                            captain = Captain._default_manager.get(full_name=captain_name)  # type: ignore
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
                    
                    # active_bool is already set above
                    
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
                        print(f"  ✓ Created new ship: {ship.name} ({ship.registration_number})")
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
                            print(f"  ✓ Updated existing ship: {ship.name} ({ship.registration_number})")
                        else:
                            print(f"  - No changes needed for ship: {ship.name} ({ship.registration_number})")
            
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
            return Response(
                {'error': f'Error processing CSV data: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema(
    tags=['Ships'],
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


@extend_schema(
    tags=['Ships'],
    summary='Rekomendasi Kapal AI',
    description='''Mendapatkan rekomendasi kapal berdasarkan data historis penangkapan ikan.
    
Fitur:
- Analisis data penangkapan ikan historis
- Peringkat kapal berdasarkan tangkapan total dan jenis ikan
- Rekomendasi kapal terbaik berdasarkan lokasi dan musim
- Analisis tren penangkapan ikan''',
    parameters=[
        OpenApiParameter(
            name='time_period', 
            description='Periode waktu untuk analisis (dalam hari, default: 180)', 
            required=False, 
            type=int
        ),
        OpenApiParameter(
            name='fish_species', 
            description='ID spesies ikan (opsional, untuk rekomendasi spesifik berdasarkan jenis ikan)', 
            required=False, 
            type=int
        ),
        OpenApiParameter(
            name='top_n', 
            description='Jumlah kapal teratas untuk direkomendasikan (default: 5)', 
            required=False, 
            type=int
        ),
    ],
    responses={
        200: AIRecommendationResponseSerializer,
        400: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string', 'description': 'Pesan kesalahan'}
            }
        },
        404: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string', 'description': 'Pesan kesalahan'}
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_ship_recommendations(request):
    """
    Endpoint AI untuk memberikan rekomendasi kapal berdasarkan data historis penangkapan ikan
    """
    # Get query parameters with defaults
    time_period = int(request.query_params.get('time_period', 180))  # Default to 180 days
    fish_species_id = request.query_params.get('fish_species', None)
    top_n = int(request.query_params.get('top_n', 5))  # Default to top 5 ships
    
    # Calculate date range for analysis
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=time_period)
    
    # Get FishCatch and CatchDetail models dynamically
    FishCatch = apps.get_model('catches', 'FishCatch')
    CatchDetail = apps.get_model('catches', 'CatchDetail')
    
    # Query to get all active ships with catch data in the period
    ships_with_catches = Ship._default_manager.filter(
        active=True,
        catch_reports__catch_date__gte=start_date,
        catch_reports__catch_date__lte=end_date
    ).distinct()
    
    # If no ships found with catches in the period
    if not ships_with_catches.exists():
        return Response({
            'error': f'Tidak ada data tangkapan yang ditemukan dalam {time_period} hari terakhir'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # List to store ship recommendations
    recommendations = []
    
    # Process each ship
    for ship in ships_with_catches:
        # Get all catch reports for this ship in the period
        catch_reports = FishCatch.objects.filter(
            ship=ship,
            catch_date__gte=start_date,
            catch_date__lte=end_date
        )
        
        # Filter catch details by fish species if specified
        catch_details_query = Q(fish_catch__in=catch_reports)
        if fish_species_id:
            catch_details_query &= Q(fish_species_id=fish_species_id)
        
        catch_details = CatchDetail.objects.filter(catch_details_query)
        
        # Skip if no catch details match the criteria
        if not catch_details.exists():
            continue
        
        # Calculate total catch
        total_catch = catch_details.aggregate(
            total=Sum(ExpressionWrapper(F('quantity'), output_field=FloatField()))
        )['total'] or 0
        
        # Calculate average catch per report
        num_reports = catch_reports.count()
        average_catch = total_catch / num_reports if num_reports > 0 else 0
        
        # Determine best fishing location (simplified)
        best_location_catch = catch_reports.order_by('-catch_details__quantity').first()
        best_location = {
            'latitude': float(best_location_catch.location_latitude) if best_location_catch else None,
            'longitude': float(best_location_catch.location_longitude) if best_location_catch else None
        }
        
        # Calculate monthly trends (simplified)
        monthly_data = catch_reports.annotate(
            month=TruncMonth('catch_date')
        ).values('month').annotate(
            total=Sum('catch_details__quantity')
        ).order_by('month')
        
        # Determine trend direction
        trend = "stabil"  # Default
        if len(monthly_data) >= 2:
            first_month = monthly_data[0]['total'] if monthly_data[0]['total'] else 0
            last_month = monthly_data[len(monthly_data)-1]['total'] if monthly_data[len(monthly_data)-1]['total'] else 0
            
            if last_month > first_month * 1.1:  # 10% increase
                trend = "naik"
            elif last_month < first_month * 0.9:  # 10% decrease
                trend = "turun"
        
        # Determine best fishing months
        best_months = []
        if monthly_data:
            avg_monthly_catch = sum(item['total'] for item in monthly_data) / len(monthly_data)
            best_months = [
                item['month'].strftime('%B') for item in monthly_data 
                if item['total'] and item['total'] > avg_monthly_catch * 1.1  # 10% above average
            ]
        
        # Calculate efficiency score (simplified)
        efficiency_score = average_catch * (0.8 if trend == "naik" else 0.6 if trend == "stabil" else 0.4)
        
        # Build recommendation object
        ship_data = {
            'id': ship.id,
            'name': ship.name,
            'registration_number': ship.registration_number,
            'owner': str(ship.owner),
            'captain': str(ship.captain) if ship.captain else None,
            'total_catch': round(total_catch, 2),
            'average_catch': round(average_catch, 2),
            'catch_trend': trend,
            'catch_efficiency': round(efficiency_score, 2),
            'best_fishing_location': best_location,
            'best_fishing_months': best_months
        }
        
        recommendations.append(ship_data)
    
    # Sort by efficiency score and get top N
    recommendations.sort(key=lambda x: x['catch_efficiency'], reverse=True)
    top_recommendations = recommendations[:top_n]
    
    # Prepare response
    response_data = {
        'top_ships': top_recommendations,
        'analysis_period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        'recommendation_factors': "Total tangkapan, rata-rata tangkapan per laporan, tren tangkapan, dan lokasi terbaik",
        'total_ships_analyzed': len(recommendations)
    }
    
    return Response(response_data)
