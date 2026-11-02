"""
IoT Domain Model (Domain Layer)
Domain logic for IoT scale devices.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class IoTDeviceDomain:
    """Domain entity representing a IoT scale device."""
    
    id: Optional[int] = None
    device_id: str = ''
    name: str = ''
    location: str = ''
    is_active: bool = True
    last_seen: str = ''

    def is_valid(self) -> bool:
        """Validate that required fields are present."""
        return bool(self.device_id.strip()) and bool(self.name.strip())

    def get_display_name(self) -> str:
        """Get display name."""
        return self.name


class IoTDeviceDomainService:
    """Domain service for IoT device business rules."""

    @classmethod
    def validate_device_data(cls, device_id: str, name: str,
                            location: str = '') -> dict:
        """Validate IoT device data."""
        errors = []

        if not device_id or not device_id.strip():
            errors.append('Device ID wajib diisi')
        elif len(device_id.strip()) < 3:
            errors.append('Device ID minimal 3 karakter')

        if not name or not name.strip():
            errors.append('Nama perangkat wajib diisi')
        elif len(name.strip()) < 3:
            errors.append('Nama perangkat minimal 3 karakter')

        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }

    @classmethod
    def format_device_data(cls, device_id: str, name: str,
                          location: str = '') -> dict:
        """Format device data for storage."""
        return {
            'device_id': device_id.strip().upper(),
            'name': name.strip(),
            'location': location.strip() if location else '',
        }

