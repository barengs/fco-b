"""
IoT Smart Scale Application Service (Application Layer)
Orchestrates business logic for IoT smart scales, readings, and harbor catch workflows.
"""

from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
from django.apps import apps
from django.utils import timezone
from django.db import transaction

from ..infrastructure.event_bus import scale_event_bus


class SmartScaleApplicationService:
    """
    Application service for Smart Scales and Readings.
    """

    def __init__(self):
        self._scale_model = None
        self._reading_model = None

    @property
    def scale_model(self):
        if self._scale_model is None:
            self._scale_model = apps.get_model('iot_scales', 'SmartScale')
        return self._scale_model

    @property
    def reading_model(self):
        if self._reading_model is None:
            self._reading_model = apps.get_model('iot_scales', 'ScaleReading')
        return self._reading_model

    def record_weight(
        self,
        device_id: str,
        weight: Decimal,
        unit: str = 'kg',
        api_key: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any], int]:
        """
        Record a weight measurement from an IoT scale device and broadcast event.
        """
        scale, _ = self.scale_model.objects.get_or_create(
            device_id=device_id,
            defaults={
                'name': f'Timbangan {device_id}',
                'port_name': 'Pelabuhan Utama',
                'is_active': True
            }
        )

        if scale.api_key:
            if not api_key or scale.api_key != api_key:
                return False, {'error': 'Kunci API timbangan tidak valid atau belum disertakan'}, 403

        scale.last_seen = timezone.now()
        scale.save(update_fields=['last_seen'])

        reading = self.reading_model.objects.create(
            scale=scale,
            device_id=device_id,
            weight=weight,
            unit=unit,
            is_stable=True
        )

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
        scale_event_bus.broadcast(payload, device_id=device_id)

        response_data = {
            'status': 'success',
            'message': 'Data berat berhasil diterima dan disiarkan ke frontend',
            'reading_id': str(reading.id),
            'device_id': device_id,
            'weight': float(weight),
            'unit': unit,
            'is_stable': True,
            'created_at': reading.created_at.isoformat()
        }
        return True, response_data, 201

    def get_latest_reading(self, device_id: Optional[str] = None, status_filter: Optional[str] = None):
        """Get latest reading optionally filtered by device_id and status."""
        qs = self.reading_model.objects.select_related('scale', 'fish_catch', 'catch_detail')
        if device_id:
            qs = qs.filter(device_id=device_id)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs.order_by('-created_at').first()

    def list_readings(self, device_id: Optional[str] = None, status_filter: Optional[str] = None, limit: int = 50):
        """List readings with optional filters."""
        qs = self.reading_model.objects.select_related('scale', 'fish_catch', 'catch_detail')
        if device_id:
            qs = qs.filter(device_id=device_id)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs.order_by('-created_at')[:limit]

    def save_catch_from_scale(
        self,
        reading,
        ship,
        species,
        wpp=None,
        catch_type='pelagic',
        catch_date=None,
        latitude=Decimal('-8.7483'),
        longitude=Decimal('115.1672'),
        operator_notes=''
    ) -> Tuple[bool, Dict[str, Any], int]:
        """
        Save catch report at harbor by combining IoT scale reading with ship and catch details.
        """
        FishCatch = apps.get_model('catches', 'FishCatch')
        CatchDetail = apps.get_model('catches', 'CatchDetail')
        Quota = apps.get_model('ships', 'Quota')

        target_date = catch_date or timezone.now().date()

        with transaction.atomic():
            fish_catch, _ = FishCatch.objects.get_or_create(
                ship=ship,
                catch_date=target_date,
                defaults={
                    'catch_type': catch_type,
                    'location_latitude': latitude,
                    'location_longitude': longitude,
                    'description': f"Ditimbang di pelabuhan via IoT ({reading.device_id})"
                }
            )

            remaining_quota_val = None
            quota_obj = Quota.objects.filter(ship=ship, year=target_date.year, is_active=True).first()
            if quota_obj:
                if reading.weight > quota_obj.remaining_quota:
                    return False, {
                        'error': f"Kuota kapal '{ship.name}' tidak mencukupi! Sisa kuota: {quota_obj.remaining_quota} kg, berat ditimbang: {reading.weight} kg"
                    }, 400
                quota_obj.remaining_quota -= reading.weight
                quota_obj.save()
                remaining_quota_val = float(quota_obj.remaining_quota)

            catch_detail = CatchDetail(
                fish_catch=fish_catch,
                fish_species=species,
                wpp=wpp,
                quantity=reading.weight,
                unit=reading.unit,
                notes=operator_notes or f"Hasil timbang IoT {reading.device_id}"
            )
            catch_detail.calculate_pnbp()
            catch_detail.save()

            reading.status = 'saved'
            reading.fish_catch = fish_catch
            reading.catch_detail = catch_detail
            reading.operator_notes = operator_notes
            reading.save(update_fields=['status', 'fish_catch', 'catch_detail', 'operator_notes'])

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

        response_data = {
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
        }
        return True, response_data, 201


# Backward compatibility alias
IoTDeviceApplicationService = SmartScaleApplicationService

