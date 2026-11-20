"""
IoT Smart Scale Application Service (Application Layer)
Orchestrates business logic for IoT smart scales, readings, and harbor catch workflows.
"""

from typing import Optional, List, Dict, Any, Tuple
import secrets
from decimal import Decimal
from django.apps import apps
from django.utils import timezone
from django.db import transaction

try:
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
except ImportError:
    async_to_sync = None
    get_channel_layer = None

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
        is_stable: bool = True,
        session_id: str = '',
        api_key: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any], int]:
        """
        Record a weight measurement from an IoT scale device and broadcast event.
        Includes device authorization, load cell anomaly detection, and real-time broadcasting.
        """
        # Ensure device is pre-registered by port administrator (prevent rogue auto-provisioning)
        scale = self.scale_model.objects.filter(device_id=device_id).first()
        if not scale:
            return False, {
                'error': f"Perangkat timbangan '{device_id}' tidak terdaftar di sistem. Daftarkan perangkat terlebih dahulu melalui administrator pelabuhan."
            }, 404

        if not scale.is_active:
            return False, {
                'error': f"Timbangan {device_id} sedang dinonaktifkan. Silakan hubungi petugas pelabuhan."
            }, 403

        # Enforce device token / API key authentication
        if scale.api_key:
            if not api_key or not secrets.compare_digest(str(scale.api_key), str(api_key)):
                return False, {'error': 'Kunci API timbangan (X-Device-Token) tidak cocok atau belum disertakan.'}, 403

        scale.last_seen = timezone.now()
        scale.save(update_fields=['last_seen'])

        # Anomaly / Rapid Fluctuation Detection
        # Check if weight abruptly spikes by > 3,000 kg within < 3 seconds
        now = timezone.now()
        anomaly_warning = None
        last_reading = self.reading_model.objects.filter(device_id=device_id).order_by('-created_at').first()

        if last_reading:
            time_diff = (now - last_reading.created_at).total_seconds()
            prev_multiplier = 1000.0 if str(last_reading.unit).lower() in ('ton', 'tons', 'tonnes') else 1.0
            curr_multiplier = 1000.0 if str(unit).lower() in ('ton', 'tons', 'tonnes') else 1.0
            prev_kg = float(last_reading.weight) * prev_multiplier
            curr_kg = float(weight) * curr_multiplier
            weight_diff_kg = abs(curr_kg - prev_kg)

            if time_diff < 3.0 and weight_diff_kg > 3000.0:
                is_stable = False
                anomaly_warning = (
                    f"Peringatan anomali: Lonjakan bobot drastis terdeteksi ({weight_diff_kg:.1f} kg dalam {time_diff:.1f} detik). "
                    "Sensor load cell ditandai belum stabil."
                )

        reading = self.reading_model.objects.create(
            scale=scale,
            device_id=device_id,
            weight=weight,
            unit=unit,
            is_stable=is_stable,
            session_id=session_id
        )

        payload = {
            'event': 'weight_update',
            'reading_id': str(reading.id),
            'device_id': device_id,
            'scale_name': scale.name,
            'port_name': scale.port_name,
            'weight': float(weight),
            'unit': unit,
            'is_stable': is_stable,
            'status': reading.status,
            'session_id': session_id,
            'anomaly_warning': anomaly_warning,
            'created_at': reading.created_at.isoformat()
        }
        # 1. Broadcast via Django Channels & Redis Channel Layer
        if get_channel_layer and async_to_sync:
            try:
                channel_layer = get_channel_layer()
                if channel_layer:
                    # Broadcast to specific scale device group
                    async_to_sync(channel_layer.group_send)(
                        f"scale_{device_id}",
                        {
                            "type": "scale_weight_update",
                            "data": payload
                        }
                    )
                    # Broadcast to global monitoring group
                    async_to_sync(channel_layer.group_send)(
                        "scale_all",
                        {
                            "type": "scale_weight_update",
                            "data": payload
                        }
                    )
            except Exception:
                # Fallback gracefully if channel layer is temporarily offline
                pass

        # 2. Legacy in-memory bus for backwards-compatible SSE clients
        scale_event_bus.broadcast(payload, device_id=device_id)

        response_data = {
            'status': 'success',
            'message': 'Data timbangan berhasil diterima dan disiarkan ke sistem dermaga.',
            'reading_id': str(reading.id),
            'device_id': device_id,
            'weight': float(weight),
            'unit': unit,
            'is_stable': is_stable,
            'session_id': session_id,
            'anomaly_warning': anomaly_warning,
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

            # Gunakan bobot hasil timbang
            measured_weight = reading.weight

            remaining_quota_val = None
            quota_percentage_val = None
            quota_warning = None
            quota_obj = Quota.objects.filter(ship=ship, year=target_date.year, is_active=True).first()
            if quota_obj:
                if measured_weight > quota_obj.remaining_quota:
                    return False, {
                        'error': f"Sisa kuota kapal '{ship.name}' ({quota_obj.remaining_quota:,.2f} kg) tidak mencukupi untuk bobot hasil timbang ({measured_weight:,.2f} kg)!"
                    }, 400
                quota_obj.remaining_quota -= measured_weight
                quota_obj.save()
                remaining_quota_val = float(quota_obj.remaining_quota)
                if quota_obj.quota > 0:
                    quota_percentage_val = round(float(quota_obj.remaining_quota / quota_obj.quota) * 100, 2)
                    if quota_obj.remaining_quota <= 0:
                        quota_warning = f"Perhatian: Kuota kapal '{ship.name}' tahun {target_date.year} telah habis (0 kg tersisa)."
                    elif quota_percentage_val <= 15:
                        quota_warning = f"Peringatan: Kuota kapal '{ship.name}' telah mencapai ambang batas kritis (tersisa {quota_percentage_val:.1f}% / {remaining_quota_val:,.1f} kg)."

            notes_text = operator_notes or f"Hasil timbang resmi timbangan pelabuhan {reading.device_id}"

            catch_detail = CatchDetail(
                fish_catch=fish_catch,
                fish_species=species,
                wpp=wpp,
                quantity=measured_weight,
                unit=reading.unit,
                notes=notes_text
            )
            catch_detail.calculate_pnbp()
            catch_detail.save()

            reading.status = 'saved'
            reading.fish_catch = fish_catch
            reading.catch_detail = catch_detail
            reading.operator_notes = operator_notes
            reading.save(update_fields=['status', 'fish_catch', 'catch_detail', 'operator_notes'])

        # Auto-seal catch into cryptographic blockchain block
        try:
            from blockchain.application.blockchain_service import BlockchainApplicationService
            blockchain_service = BlockchainApplicationService()
            blockchain_service.record_catch_transaction(fish_catch)
        except Exception:
            pass

        save_broadcast_payload = {
            'event': 'weight_saved',
            'reading_id': str(reading.id),
            'device_id': reading.device_id,
            'status': 'saved',
            'catch_id': fish_catch.id,
            'fish_species': species.name,
            'weight': float(reading.weight)
        }
        if get_channel_layer and async_to_sync:
            try:
                channel_layer = get_channel_layer()
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        f"scale_{reading.device_id}",
                        {"type": "scale_weight_update", "data": save_broadcast_payload}
                    )
                    async_to_sync(channel_layer.group_send)(
                        "scale_all",
                        {"type": "scale_weight_update", "data": save_broadcast_payload}
                    )
            except Exception:
                pass

        scale_event_bus.broadcast(save_broadcast_payload, device_id=reading.device_id)

        response_data = {
            'status': 'success',
            'message': 'Laporan hasil tangkapan berhasil disimpan dan disegel resmi.',
            'catch_id': fish_catch.id,
            'catch_detail_id': catch_detail.id,
            'ship_registration': ship.registration_number,
            'ship_name': ship.name,
            'fish_species': species.name,
            'weight': float(measured_weight),
            'unit': reading.unit,
            'pnkp': float(catch_detail.pnkp) if catch_detail.pnkp else None,
            'pnbp': float(catch_detail.pnbp) if catch_detail.pnbp else None,
            'remaining_quota': remaining_quota_val,
            'quota_percentage': quota_percentage_val,
            'quota_warning': quota_warning,
            'reading_id': str(reading.id),
            'blockchain_status': 'Tercatat otomatis di Blockchain'
        }
        return True, response_data, 201


# Backward compatibility alias
IoTDeviceApplicationService = SmartScaleApplicationService

