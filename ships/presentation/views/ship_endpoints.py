"""
Ship Dedicated Endpoints (Presentation Layer)
Standalone API views for registration verification and AI ship recommendations.
"""

from datetime import datetime, timedelta
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Count, Avg
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

from ...models import Ship
from ...serializers import AIRecommendationResponseSerializer

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
    time_period = int(request.query_params.get('time_period', 180))
    fish_species_id = request.query_params.get('fish_species', None)
    top_n = int(request.query_params.get('top_n', 5))

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=time_period)

    FishCatch = apps.get_model('catches', 'FishCatch')
    CatchDetail = apps.get_model('catches', 'CatchDetail')

    ships_with_catches = Ship._default_manager.filter(
        active=True,
        catch_reports__catch_date__gte=start_date,
        catch_reports__catch_date__lte=end_date
    ).distinct()

    if not ships_with_catches.exists():
        return Response({
            'error': f'Tidak ada data tangkapan yang ditemukan dalam {time_period} hari terakhir'
        }, status=status.HTTP_404_NOT_FOUND)

    recommendations = []

    for ship in ships_with_catches:
        catch_reports = FishCatch.objects.filter(
            ship=ship,
            catch_date__gte=start_date,
            catch_date__lte=end_date
        )

        catch_details = CatchDetail.objects.filter(
            fish_catch__in=catch_reports
        )

        if fish_species_id:
            catch_details = catch_details.filter(fish_species_id=fish_species_id)

        stats = catch_details.aggregate(
            total_weight=Sum('quantity'),
            total_value=Sum('value'),
            avg_weight_per_trip=Avg('quantity')
        )

        total_weight = float(stats['total_weight'] or 0)
        total_value = float(stats['total_value'] or 0)
        avg_weight = float(stats['avg_weight_per_trip'] or 0)
        trip_count = catch_reports.count()

        if total_weight > 0:
            gt = float(getattr(ship, 'gross_tonnage', 0) or 50.0)
            score = (total_weight / (gt or 1)) * 0.6 + (trip_count * 10) * 0.4

            recommendations.append({
                'ship_id': ship.id,
                'ship_name': ship.name,
                'registration_number': ship.registration_number,
                'gross_tonnage': gt,
                'owner': str(ship.owner),
                'total_weight_kg': total_weight,
                'total_value_idr': total_value,
                'trip_count': trip_count,
                'score': round(score, 2),
            })

    recommendations.sort(key=lambda x: x['score'], reverse=True)
    top_recommendations = recommendations[:top_n]

    return Response({
        'time_period_days': time_period,
        'count': len(top_recommendations),
        'results': top_recommendations
    })
