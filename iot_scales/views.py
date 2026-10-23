import json
import time
import queue
import threading
from decimal import Decimal
from datetime import datetime

from django.http import StreamingHttpResponse
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import SmartScale, ScaleReading
from .serializers import (
    SmartScaleSerializer,
    IoTWeightInputSerializer,
    ScaleReadingSerializer,
    HarborWeighingCatchSaveSerializer
)
from catches.models import FishCatch, CatchDetail
from ships.models import Ship, Quota
from fish.models import FishSpecies
from regions.models import FishingArea


# Thread-safe in-memory event bus for SSE (Server-Sent Events)
class ScaleEventBus:
    def __init__(self):
        self._subscribers = []
        self._lock = threading.Lock()

    def subscribe(self, device_id=None):
        q = queue.Queue(maxsize=100)
        with self._lock:
            self._subscribers.append((q, device_id))
        return q

    def unsubscribe(self, q):
        with self._lock:
            self._subscribers = [sub for sub in self._subscribers if sub[0] != q]

    def broadcast(self, payload, device_id):
        with self._lock:
            dead_subscribers = []
            for q, subscribed_device in self._subscribers:
                if subscribed_device is None or subscribed_device == device_id:
                    try:
                        q.put_nowait(payload)
                    except queue.Full:
                        dead_subscribers.append((q, subscribed_device))
            for dead in dead_subscribers:
                if dead in self._subscribers:
                    self._subscribers.remove(dead)


scale_event_bus = ScaleEventBus()


class SmartScaleViewSet(viewsets.ModelViewSet):
    """
    CRUD management for IoT smart scales deployed at ports.
    """
    queryset = SmartScale.objects.all().order_by('-created_at')
    serializer_class = SmartScaleSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(
    tags=['IoT Smart Scale'],
    summary='Terima Data Berat dari Timbangan Pintar IoT',
    description='''Endpoint yang dipanggil oleh perangkat timbangan pintar (IoT) di pelabuhan 
    saat ikan diletakkan di timbangan. Data berat langsung dicatat dan disiarkan secara real-time 
    ke frontend pelabuhan via Server-Sent Events (SSE).''',
    request=IoTWeightInputSerializer,
    responses={
        201: {
            'type': 'object',
            'properties': {
                'status': {'type': 'string'},
                'message': {'type': 'string'},
                'reading_id': {'type': 'string', 'format': 'uuid'},
                'device_id': {'type': 'string'},
                'weight': {'type': 'number'},
                'unit': {'type': 'string'},
                'is_stable': {'type': 'boolean'},
                'created_at': {'type': 'string', 'format': 'date-time'}
            }
        },
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        403: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def receive_iot_weight(request):
    """
    Endpoint for IoT scale devices to post weight measurements.
    """
    serializer = IoTWeightInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Format data tidak valid', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    data = serializer.validated_data
    device_id = data['device_id']
    weight = data['weight']
    unit = data.get('unit', 'kg')
    api_key = request.headers.get('X-Device-Token') or data.get('api_key', '')

    # Check or auto-register SmartScale
    scale, _ = SmartScale.objects.get_or_create(
        device_id=device_id,
        defaults={
            'name': f'Timbangan {device_id}',
            'port_name': 'Pelabuhan Utama',
            'is_active': True
        }
    )

    # Validate API key if scale has one configured
    if scale.api_key:
        if not api_key or scale.api_key != api_key:
            return Response(
                {'error': 'Kunci API timbangan tidak valid atau belum disertakan'},
                status=status.HTTP_403_FORBIDDEN
            )

    # Update last seen timestamp
    scale.last_seen = timezone.now()
    scale.save(update_fields=['last_seen'])

    # Create ScaleReading record (default to stable state, tare 0.0 since no tare field is transmitted)
    reading = ScaleReading.objects.create(
        scale=scale,
        device_id=device_id,
        weight=weight,
        unit=unit,
        is_stable=True
    )

    # Prepare payload for real-time broadcast to frontend
    payload = {
        'event': 'weight_update',
        'reading_id': str(reading.id),
        'device_id': device_id,
        'scale_name': scale.name,
        'port_name': scale.port_name,
        'weight': float(weight),
        'unit': unit,
        'tare': 0.0,
        'is_stable': True,
        'status': reading.status,
        'created_at': reading.created_at.isoformat()
    }

    # Broadcast to all connected frontend clients
    scale_event_bus.broadcast(payload, device_id=device_id)

    return Response(
        {
            'status': 'success',
            'message': 'Data berat berhasil diterima dan disiarkan ke frontend',
            'reading_id': str(reading.id),
            'device_id': device_id,
            'weight': float(weight),
            'unit': unit,
            'is_stable': True,
            'created_at': reading.created_at.isoformat()
        },
        status=status.HTTP_201_CREATED
    )


@extend_schema(
    tags=['IoT Smart Scale'],
    summary='Ambil Pembacaan Timbangan Terakhir',
    description='''Endpoint REST untuk mengambil data timbangan terbaru. 
    Dapat digunakan frontend untuk polling atau fetch pertama kali saat membuka halaman timbang.''',
    parameters=[
        OpenApiParameter('device_id', OpenApiTypes.STR, description='Filter berdasarkan ID Perangkat Timbangan', required=False),
        OpenApiParameter('status', OpenApiTypes.STR, description='Filter status (pending, saved, discarded)', required=False),
    ],
    responses={200: ScaleReadingSerializer}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_latest_scale_reading(request):
    """
    Get latest weight reading for a given scale device or harbor.
    """
    device_id = request.query_params.get('device_id')
    status_filter = request.query_params.get('status', 'pending')

    queryset = ScaleReading.objects.all()
    if device_id:
        queryset = queryset.filter(device_id=device_id)
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    latest = queryset.first()
    if not latest:
        # Fallback to any latest reading if no pending ones
        fallback = ScaleReading.objects.filter(device_id=device_id).first() if device_id else ScaleReading.objects.first()
        if not fallback:
            return Response({'message': 'Belum ada data timbangan yang tercatat'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ScaleReadingSerializer(fallback)
        return Response(serializer.data)

    serializer = ScaleReadingSerializer(latest)
    return Response(serializer.data)


@extend_schema(
    tags=['IoT Smart Scale'],
    summary='Daftar Riwayat Pembacaan Timbangan',
    description='Mendapatkan riwayat pembacaan timbangan di pelabuhan dengan filter.',
    parameters=[
        OpenApiParameter('device_id', OpenApiTypes.STR, description='ID Perangkat', required=False),
        OpenApiParameter('status', OpenApiTypes.STR, description='Status (pending/saved/discarded)', required=False),
        OpenApiParameter('limit', OpenApiTypes.INT, description='Jumlah maksimal baris (default: 20)', required=False),
    ],
    responses={200: ScaleReadingSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def list_scale_readings(request):
    """
    List historical weight readings from IoT scales.
    """
    device_id = request.query_params.get('device_id')
    status_filter = request.query_params.get('status')
    limit = int(request.query_params.get('limit', 20))

    queryset = ScaleReading.objects.all()
    if device_id:
        queryset = queryset.filter(device_id=device_id)
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    readings = queryset[:limit]
    serializer = ScaleReadingSerializer(readings, many=True)
    return Response(serializer.data)


def stream_scale_events(request):
    """
    Server-Sent Events (SSE) streaming generator.
    Frontend connects with:
        const eventSource = new EventSource('/api/iot/scales/stream/?device_id=SCALE-01');
        eventSource.onmessage = (e) => { const data = JSON.parse(e.data); console.log(data.weight); };
    """
    device_id = request.GET.get('device_id')
    event_queue = scale_event_bus.subscribe(device_id=device_id)

    def event_generator():
        try:
            # Send initial connected message & latest reading if available
            welcome_msg = {
                'event': 'connected',
                'device_id': device_id or 'all',
                'timestamp': timezone.now().isoformat(),
                'message': 'Terhubung ke siaran data timbangan pintar'
            }
            yield f"data: {json.dumps(welcome_msg)}\n\n"

            # Check if there is already a recent pending reading
            recent_query = ScaleReading.objects.filter(status='pending')
            if device_id:
                recent_query = recent_query.filter(device_id=device_id)
            initial_reading = recent_query.first()
            if initial_reading:
                initial_payload = {
                    'event': 'initial_state',
                    'reading_id': str(initial_reading.id),
                    'device_id': initial_reading.device_id,
                    'weight': float(initial_reading.weight),
                    'unit': initial_reading.unit,
                    'tare': float(initial_reading.tare),
                    'is_stable': initial_reading.is_stable,
                    'status': initial_reading.status,
                    'created_at': initial_reading.created_at.isoformat()
                }
                yield f"data: {json.dumps(initial_payload)}\n\n"

            # Listen for new events
            while True:
                try:
                    payload = event_queue.get(timeout=25.0)
                    yield f"data: {json.dumps(payload)}\n\n"
                except queue.Empty:
                    # Send heartbeat ping every 25 seconds to keep connection alive
                    ping = {'event': 'ping', 'timestamp': timezone.now().isoformat()}
                    yield f": keep-alive\n\n"
        finally:
            scale_event_bus.unsubscribe(event_queue)

    response = StreamingHttpResponse(
        event_generator(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


@extend_schema(
    tags=['IoT Smart Scale'],
    summary='Simpan Data Tangkapan dari Hasil Timbangan IoT',
    description='''Endpoint yang dipanggil oleh frontend pelabuhan ketika operator telah memilih 
    jenis ikan dan menekan tombol simpan.
    
    Alur yang dijalankan sistem:
    1. Mengambil data berat dari ID pembacaan timbangan IoT (ScaleReading).
    2. Membuat/mengaitkan laporan tangkapan (FishCatch) dan detail tangkapan (CatchDetail).
    3. Menghitung otomatis tarif PNBP dan PNKP berdasarkan GT kapal dan referensi harga ikan.
    4. Mengurangi sisa kuota kapal jika kuota aktif terdaftar.
    5. Merekam transaksi secara otomatis ke rantai Blockchain.
    6. Mengubah status pembacaan timbangan menjadi 'saved'.''',
    request=HarborWeighingCatchSaveSerializer,
    responses={
        201: {
            'type': 'object',
            'properties': {
                'status': {'type': 'string'},
                'message': {'type': 'string'},
                'catch_id': {'type': 'integer'},
                'catch_detail_id': {'type': 'integer'},
                'ship_name': {'type': 'string'},
                'fish_species': {'type': 'string'},
                'weight': {'type': 'number'},
                'pnbp': {'type': 'number'},
                'remaining_quota': {'type': 'number'},
                'blockchain_recorded': {'type': 'boolean'}
            }
        },
        400: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def harbor_save_catch_from_scale(request):
    """
    Save catch report at harbor by combining IoT scale weight reading
    with user-selected fish species, ship, and region data.
    """
    serializer = HarborWeighingCatchSaveSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Data input tidak valid', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    validated = serializer.validated_data
    reading = validated['reading_id']
    ship = validated['ship_registration_number']
    species = validated['fish_species_id']
    wpp = validated.get('wpp_id')
    catch_type = validated.get('catch_type', 'pelagic')
    catch_date = validated.get('catch_date', timezone.now().date())
    latitude = validated.get('location_latitude', Decimal('-8.7483'))
    longitude = validated.get('location_longitude', Decimal('115.1672'))
    operator_notes = validated.get('operator_notes', '')

    with transaction.atomic():
        # 1. Create or get FishCatch record
        fish_catch, created = FishCatch.objects.get_or_create(
            ship=ship,
            catch_date=catch_date,
            defaults={
                'catch_type': catch_type,
                'location_latitude': latitude,
                'location_longitude': longitude,
                'description': f"Ditimbang di pelabuhan via IoT ({reading.device_id})"
            }
        )

        # 2. Check and deduct ship quota
        remaining_quota_val = None
        quota_obj = Quota.objects.filter(ship=ship, year=catch_date.year, is_active=True).first()
        if quota_obj:
            if reading.weight > quota_obj.remaining_quota:
                return Response(
                    {
                        'error': f"Kuota kapal '{ship.name}' tidak mencukupi! Sisa kuota: {quota_obj.remaining_quota} kg, berat ditimbang: {reading.weight} kg"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            quota_obj.remaining_quota -= reading.weight
            quota_obj.save()
            remaining_quota_val = float(quota_obj.remaining_quota)

        # 3. Create CatchDetail (automatically computes PNBP via save())
        catch_detail = CatchDetail(
            fish_catch=fish_catch,
            fish_species=species,
            wpp=wpp,
            quantity=reading.weight,
            unit=reading.unit,
            notes=operator_notes or f"Hasil timbang IoT {reading.device_id}"
        )
        # Calling calculate_pnbp() and save()
        catch_detail.calculate_pnbp()
        catch_detail.save()

        # 4. Update reading status
        reading.status = 'saved'
        reading.fish_catch = fish_catch
        reading.catch_detail = catch_detail
        reading.operator_notes = operator_notes
        reading.save(update_fields=['status', 'fish_catch', 'catch_detail', 'operator_notes'])

    # Broadcast event that this reading has been saved so other frontend tabs update
    save_broadcast_payload = {
        'event': 'weight_saved',
        'reading_id': str(reading.id),
        'device_id': reading.device_id,
        'status': 'saved',
        'catch_id': fish_catch.id,
        'fish_species': species.name,
        'weight': float(reading.weight)
    }
    scale_event_bus.broadcast(save_broadcast_payload, device_id=reading.device_id)

    return Response(
        {
            'status': 'success',
            'message': 'Laporan tangkapan dari timbangan IoT berhasil disimpan ke database!',
            'catch_id': fish_catch.id,
            'catch_detail_id': catch_detail.id,
            'ship_registration': ship.registration_number,
            'ship_name': ship.name,
            'fish_species': species.name,
            'weight': float(reading.weight),
            'unit': reading.unit,
            'pnkp': float(catch_detail.pnkp) if catch_detail.pnkp else None,
            'pnbp': float(catch_detail.pnbp) if catch_detail.pnbp else None,
            'remaining_quota': remaining_quota_val,
            'reading_id': str(reading.id),
            'blockchain_status': 'Tercatat otomatis di Blockchain'
        },
        status=status.HTTP_201_CREATED
    )
