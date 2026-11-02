"""
Domain Layer for Regions (WPP - Wilayah Penangkapan Perikanan)
Business rules and entities for fishing zones/regions management.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


class RegionDomain:
    """Domain entity representing a Fishing Zone (WPP)."""
    
    def __init__(
        self,
        id: int = None,
        code: str = '',
        name: str = '',
        description: str = '',
        is_active: bool = True,
        created_at: str = None,
        updated_at: str = None
    ):
        self.id = id
        self.code = code.strip() if code else ''
        self.name = name.strip() if name else ''
        self.description = description.strip() if description else ''
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    def is_valid(self) -> bool:
        """Validate that required fields are present."""
        return bool(self.code and self.name)

    def get_display_name(self) -> str:
        """Get display name with code prefix."""
        return f"{self.code} - {self.name}" if self.code and self.name else self.name or self.code or ''


class RegionValidationResult:
    """Result of region validation with success flag and error messages."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []

    def add_error(self, message: str):
        """Add an error message to the result."""
        self.errors.append(message)
        self.is_valid = False


class RegionService:
    """
    Domain service for region business rules.
    Contains pure business logic without framework dependencies.
    """

    VALID_CODE_PATTERN = r'^[A-Z0-9]{3,}$'

    @classmethod
    def validate_region_data(cls, name: str, code: str, description: str = '') -> RegionValidationResult:
        """
        Validate region data according to business rules.
        
        Rules:
        - Name is required and must be at least 3 characters
        - Code is required, uppercase alphanumeric, min 3 chars
        - Description is optional
        """
        result = RegionValidationResult(is_valid=True)

        # Validate name
        if not name or not name.strip():
            result.add_error('Nama wilayah wajib diisi')
        elif len(name.strip()) < 3:
            result.add_error('Nama wilayah minimal 3 karakter')

        # Validate code
        if not code or not code.strip():
            result.add_error('Kode wilayah wajib diisi')
        elif not code.strip().isalnum():
            result.add_error('Kode wilayah hanya boleh berisi huruf dan angka')
        elif len(code.strip()) < 3:
            result.add_error('Kode wilayah minimal 3 karakter')
        elif code != code.upper():
            result.add_error('Kode wilayah harus huruf kapital')

        # Description is optional but if provided must be reasonable length
        if description and len(description) > 500:
            result.add_error('Deskripsi maksimal 500 karakter')

        return result

    @classmethod
    def format_region_data(cls, name: str, code: str, description: str = '') -> dict:
        """
        Format region data for consistent storage.
        """
        return {
            'name': name.strip(),
            'code': code.strip().upper(),
            'description': description.strip() if description else '',
        }

    @classmethod
    def generate_default_code(cls, name: str) -> str:
        """
        Generate a default code from name if not provided.
        Example: "Wilayah Perikanan 571" -> "WPP571"
        """
        import re
        # Extract numbers from name
        numbers = re.findall(r'\d+', name)
        if numbers:
            return f"WPP{numbers[0]}"
        # Fallback: use first letters
        words = name.split()
        code = ''.join(w[0].upper() for w in words[:3] if w)
        return code if code else 'WPP001'
