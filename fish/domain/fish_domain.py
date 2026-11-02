"""
Fish Domain Layer
Business logic and entities for fish species and fish management.
"""

from dataclasses import dataclass
from typing import Optional, List
from decimal import Decimal


@dataclass
class FishSpeciesDomain:
    """Domain entity representing a fish species."""
    
    id: Optional[int] = None
    name: str = ''
    scientific_name: str = ''
    description: str = ''

    def is_valid(self) -> bool:
        """Validate that required fields are present."""
        return bool(self.name.strip())

    def get_display_name(self) -> str:
        """Get display name with scientific name if available."""
        if self.scientific_name:
            return f"{self.name} ({self.scientific_name})"
        return self.name


@dataclass
class FishDomain:
    """Domain entity representing a fish catch record."""
    
    id: Optional[int] = None
    fish_species: str = ''
    weight_kg: float = 0.0
    location: str = ''
    caught_at: str = ''
    notes: str = ''
    ship_registration: str = ''

    def is_valid(self) -> bool:
        """Validate that required fields are present."""
        return bool(self.fish_species.strip()) and self.weight_kg > 0


class FishValidationResult:
    """Result of fish/domain validation."""

    def __init__(self, is_valid: bool, errors: list = None):
        self.is_valid = is_valid
        self.errors = errors or []

    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False


class FishSpeciesDomainService:
    """Domain service for fish species business rules."""

    @classmethod
    def validate_species_data(cls, name: str, scientific_name: str = '', description: str = '') -> FishValidationResult:
        """Validate species data."""
        result = FishValidationResult(is_valid=True)

        if not name or not name.strip():
            result.add_error('Nama ikan wajib diisi')
        elif len(name.strip()) < 2:
            result.add_error('Nama ikan minimal 2 karakter')

        if scientific_name and len(scientific_name.strip()) < 3:
            result.add_error('Nama ilmiah minimal 3 karakter')

        if description and len(description) > 500:
            result.add_error('Deskripsi maksimal 500 karakter')

        return result

    @classmethod
    def format_species_data(cls, name: str, scientific_name: str = '', description: str = '') -> dict:
        """Format species data for storage."""
        return {
            'name': name.strip(),
            'scientific_name': scientific_name.strip() if scientific_name else '',
            'description': description.strip() if description else '',
        }


class FishDomainService:
    """Domain service for fish catch records business rules."""

    MIN_WEIGHT = 0.01  # kg
    MAX_WEIGHT = 10000.0  # kg

    @classmethod
    def validate_fish_data(cls, fish_species: str, weight_kg: float, location: str = '',
                          notes: str = '') -> FishValidationResult:
        """Validate fish catch data."""
        result = FishValidationResult(is_valid=True)

        if not fish_species or not fish_species.strip():
            result.add_error('Spesies ikan wajib diisi')

        if not weight_kg or weight_kg <= 0:
            result.add_error('Berat ikan harus lebih dari 0 kg')
        elif weight_kg > cls.MAX_WEIGHT:
            result.add_error(f'Berat ikan maksimal {cls.MAX_WEIGHT} kg')

        if notes and len(notes) > 1000:
            result.add_error('Catatan maksimal 1000 karakter')

        return result

    @classmethod
    def format_fish_data(cls, fish_species: str, weight_kg: float, location: str = '',
                        notes: str = '') -> dict:
        """Format fish catch data for storage."""
        return {
            'fish_species': fish_species.strip(),
            'weight_kg': float(weight_kg),
            'location': location.strip() if location else '',
            'notes': notes.strip() if notes else '',
        }
