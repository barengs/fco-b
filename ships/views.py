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
from decimal import Decimal

class IsShipOwnerOrAdmin(permissions.BasePermission):
    """
    Anti-IDOR: Hanya pemilik sah kapal, admin, atau regulator yang dapat mengubah/menghapus kapal.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, 'role', '') in ('admin', 'superadmin', 'regulator') or user.is_staff or user.is_superuser:
            return True
        user_owner = getattr(user, 'owner', None)
        return user_owner is not None and obj.owner_id == user_owner.id

@extend_schema_view(
    list=extend_schema(
        tags=['Ships'],
        summary='Daftar semua kapal',
        description='Mengambil daftar semua kapal penangkap ikan dengan informasi kuota tahun berjalan',
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'count': {'type': 'integer'},
                    'next': {'type': 'string', 'nullable': True},
                    'previous': {'type': 'string', 'nullable': True},
                    'results': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'name': {'type': 'string'},
                                'registration_number': {'type': 'string'},
                                'owner': {'type': 'integer', 'nullable': True},
                                'owner_name': {'type': 'string'},
                                'captain': {'type': 'integer', 'nullable': True},
                                'captain_name': {'type': 'string'},
                                'length': {'type': 'number', 'nullable': True},
                                'width': {'type': 'number', 'nullable': True},
                                'gross_tonnage': {'type': 'number', 'nullable': True},
                                'year_built': {'type': 'integer', 'nullable': True},
                                'home_port': {'type': 'string', 'nullable': True},
                                'active': {'type': 'boolean'},
                                'current_year_quota': {
                                    'type': 'object',
                                    'nullable': True,
                                    'properties': {
                                        'year': {'type': 'integer'},
                                        'total_quota': {'type': 'number'},
                                        'remaining_quota': {'type': 'number'},
                                        'used_quota': {'type': 'number'},
                                        'quota_percentage': {'type': 'number'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    ),
    create=extend_schema(
        tags=['Ships'],
        summary='Buat kapal',
        description='Membuat kapal penangkap ikan baru'
    ),
    retrieve=extend_schema(
        tags=['Ships'],
        summary='Ambil kapal',
        description='Mengambil kapal tertentu berdasarkan ID dengan informasi kuota tahun berjalan',
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'registration_number': {'type': 'string'},
                    'owner': {'type': 'integer', 'nullable': True},
                    'owner_name': {'type': 'string'},
                    'captain': {'type': 'integer', 'nullable': True},
                    'captain_name': {'type': 'string'},
                    'length': {'type': 'number', 'nullable': True},
                    'width': {'type': 'number', 'nullable': True},
                    'gross_tonnage': {'type': 'number', 'nullable': True},
                    'year_built': {'type': 'integer', 'nullable': True},
                    'home_port': {'type': 'string', 'nullable': True},
                    'active': {'type': 'boolean'},
                    'current_year_quota': {
                        'type': 'object',
                        'nullable': True,
                        'properties': {
                            'year': {'type': 'integer'},
                            'total_quota': {'type': 'number'},
                            'remaining_quota': {'type': 'number'},
                            'used_quota': {'type': 'number'},
                            'quota_percentage': {'type': 'number'}
                        }
                    }
                }
            }
        }
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
    by_owner=extend_schema(
        methods=['GET'],
        tags=['Ships'],
        summary='Dapatkan kapal berdasarkan ID pemilik', 
        description='Mengambil semua kapal yang dimiliki oleh pemilik dengan ID tertentu',
        parameters=[
            OpenApiParameter(
                name='owner_id', 
                description='ID pemilik kapal', 
                required=True, 
                type=int
            ),
        ]
    ),
    by_captain=extend_schema(
        methods=['GET'],
        tags=['Ships'],
        summary='Dapatkan kapal berdasarkan ID nahkoda', 
        description='Mengambil semua kapal yang dikemudi oleh nahkoda dengan ID tertentu',
        parameters=[
            OpenApiParameter(
                name='captain_id', 
                description='ID nahkoda kapal', 
                required=True, 
                type=int
            ),
        ]
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
    )
)
class ShipViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola kapal penangkap ikan
    """
    queryset = Ship.objects.select_related('owner', 'captain').prefetch_related('quotas').all()  # type: ignore
    serializer_class = ShipSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsShipOwnerOrAdmin]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def by_owner(self, request):
        """Dapatkan semua kapal berdasarkan ID pemilik atau pemilik akun login"""
        owner_id = request.GET.get('owner_id')
        user = request.user
        
        # Jika owner_id tidak diberikan dan pengguna terautentikasi memiliki profil owner
        if not owner_id and user and user.is_authenticated and hasattr(user, 'owner') and user.owner:
            owner_id = user.owner.id
        
        if not owner_id:
            return Response({
                'error': 'Parameter owner_id diperlukan'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Cari kapal berdasarkan owner_id atau user_id dari pemilik
            ships = self.queryset.filter(
                models.Q(owner_id=owner_id) | models.Q(owner__user_id=owner_id)
            ).distinct()
            serializer = self.get_serializer(ships, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': f'Error retrieving ships: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def by_captain(self, request):
        """Dapatkan semua kapal berdasarkan ID nahkoda"""
        captain_id = request.GET.get('captain_id')
        
        if not captain_id:
            return Response({
                'error': 'Parameter captain_id diperlukan'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            ships = self.queryset.filter(captain_id=captain_id)
            serializer = self.get_serializer(ships, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({
                'error': f'Error retrieving ships: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
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
        Download CSV template for ship import (delegated to application layer service)
        """
        from .application.ship_csv_service import ShipCsvService
        return ShipCsvService.generate_template()

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def import_ships(self, request):
        """
        Import ships from CSV data provided in the request (delegated to application layer service)
        """
        csv_data = request.data.get('csv_data')
        csv_file_upload = request.FILES.get('csv_file') or request.FILES.get('csv_data')
        clear_existing = request.data.get('clear_existing', False)

        if not csv_data and not csv_file_upload:
            return Response(
                {'error': 'Pilih atau unggah file CSV terlebih dahulu'},
                status=status.HTTP_400_BAD_REQUEST
            )

        MAX_UPLOAD_SIZE = 10 * 1024 * 1024
        if csv_file_upload and getattr(csv_file_upload, 'size', 0) > MAX_UPLOAD_SIZE:
            return Response(
                {'error': 'Ukuran file melebihi batas maksimal 10 MB'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if clear_existing:
            user = request.user
            is_admin = user and (user.is_superuser or getattr(user, 'role', '') in ('admin', 'superadmin') or user.is_staff)
            if not is_admin:
                return Response(
                    {'error': 'Hanya administrator yang diizinkan menggunakan opsi hapus seluruh data (clear_existing)'},
                    status=status.HTTP_403_FORBIDDEN
                )
            Ship._default_manager.all().delete()

        try:
            from .application.ship_csv_service import ShipCsvService
            result = ShipCsvService.parse_and_import(csv_file_upload=csv_file_upload, csv_data=csv_data)
            return Response({
                'message': 'Data kapal berhasil diimpor',
                **result
            })
        except Exception as e:
            return Response(
                {'error': f'Gagal mengimpor CSV: {str(e)}'},
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
                if item['total'] and item['total'] > avg_monthly_catch *  Decimal('1.1')# 10% above average
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
