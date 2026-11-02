"""
IoT Domain Model (Domain Layer)
Domain entities and business rules for Smart Scales and Readings.
"""

from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass
class SmartScaleDomain:
    """Domain entity representing an IoT Smart Scale."""
    id: Optional[int] = None
    device_id: str = ''
    name: str = ''
    port_name: str = ''
    api_key: Optional[str] = None
    is_active: bool = True
    last_seen: Optional[str] = None

    def is_valid(self) -> bool:
        return bool(self.device_id.strip()) and bool(self.name.strip())


@dataclass
class ScaleReadingDomain:
    """Domain entity representing a weight reading from a smart scale."""
    id: Optional[str] = None
    device_id: str = ''
    weight: Decimal = Decimal('0.0')
    unit: str = 'kg'
    tare: Decimal = Decimal('0.0')
    is_stable: bool = True
    status: str = 'pending'

    @property
    def net_weight(self) -> Decimal:
        return max(Decimal('0.0'), self.weight - self.tare)


# Backward compatibility alias
IoTDeviceDomain = SmartScaleDomain


class IoTDeviceDomainService:
    """Domain service for IoT device validation rules."""

    @classmethod
    def validate_device_data(cls, device_id: str, name: str, port_name: str = '') -> dict:
        errors = []
        if not device_id or not device_id.strip():
            errors.append('Device ID wajib diisi')
        elif len(device_id.strip()) < 3:
            errors.append('Device ID minimal 3 karakter')

        if not name or not name.strip():
            errors.append('Nama timbangan wajib diisi')
        elif len(name.strip()) < 3:
            errors.append('Nama timbangan minimal 3 karakter')

        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }

    @classmethod
    def format_device_data(cls, device_id: str, name: str, port_name: str = '') -> dict:
        return {
            'device_id': device_id.strip().upper(),
            'name': name.strip(),
            'port_name': port_name.strip() if port_name else 'Pelabuhan Utama',
        }


