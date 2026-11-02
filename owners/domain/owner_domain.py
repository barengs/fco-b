"""
Owner Domain Model (Domain Layer)
Domain logic for vessel owners (Pemilik Kapal).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class OwnerDomain:
    """Domain entity representing a vessel owner."""
    
    id: Optional[int] = None
    full_name: str = ''
    email: str = ''
    phone: str = ''
    address: str = ''
    owner_type: str = 'individual'
    is_active: bool = True

    def is_valid(self) -> bool:
        """Validate that required fields are present."""
        return bool(self.full_name.strip()) and bool(self.email.strip())

    def get_display_name(self) -> str:
        """Get display name."""
        return self.full_name


class OwnerDomainService:
    """Domain service for owner business rules."""

    @classmethod
    def validate_owner_data(cls, full_name: str, email: str,
                           phone: str = '', address: str = '',
                           owner_type: str = 'individual') -> dict:
        """Validate owner data."""
        errors = []

        if not full_name or not full_name.strip():
            errors.append('Nama pemilik wajib diisi')
        elif len(full_name.strip()) < 3:
            errors.append('Nama pemilik minimal 3 karakter')

        if not email or not email.strip():
            errors.append('Email wajib diisi')
        elif '@' not in email.strip():
            errors.append('Format email tidak valid')

        if owner_type not in ('individual', 'company'):
            errors.append('Tipe pemilik tidak valid')

        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }

    @classmethod
    def format_owner_data(cls, full_name: str, email: str,
                         phone: str = '', address: str = '',
                         owner_type: str = 'individual') -> dict:
        """Format owner data for storage."""
        return {
            'full_name': full_name.strip(),
            'email': email.strip().lower(),
            'phone': phone.strip() if phone else '',
            'address': address.strip() if address else '',
            'owner_type': owner_type,
        }
