"""
Application Layer for Regions (Application Layer)
Orchestrates business logic between domain and infrastructure.
"""

from typing import Optional, List, Dict, Any
from django.apps import apps

from ..domain.region_domain import RegionDomain, RegionValidationResult, RegionService


class RegionApplicationService:
    """
    Application service for managing fishing zones (WPP).
    Coordinates between domain logic and infrastructure/data access.
    """

    def __init__(self):
        self._region_model = None

    @property
    def region_model(self):
        if self._region_model is None:
            self._region_model = self._get_model('regions', 'FishingArea')
        return self._region_model

    def _get_model(self, app_label: str, model_name: str):
        return apps.get_model(app_label, model_name)

    def get_all_regions(self) -> List[dict]:
        """Get all fishing zones."""
        regions = self.region_model.objects.all().order_by('code')
        return [self._to_dict(region) for region in regions]

    def get_region_by_id(self, region_id: int) -> Optional[dict]:
        """Get a single fishing zone by ID."""
        try:
            region = self.region_model.objects.get(id=region_id)
            return self._to_dict(region)
        except self.region_model.DoesNotExist:
            return None

    def get_region_by_code(self, code: str) -> Optional[dict]:
        """Get a fishing zone by code."""
        try:
            region = self.region_model.objects.get(code=code.strip().upper())
            return self._to_dict(region)
        except self.region_model.DoesNotExist:
            return None

    def create_region(self, name: str, code: str, description: str = '') -> dict:
        """
        Create a new fishing zone with validation.
        Returns dict with 'success' bool and either 'data' or 'errors'.
        """
        # Validate input using domain service
        validation_result = RegionService.validate_region_data(
            name=name,
            code=code,
            description=description
        )

        if not validation_result.is_valid:
            return {
                'success': False,
                'errors': validation_result.errors
            }

        # Format data using domain service
        formatted = RegionService.format_region_data(
            name=name,
            code=code,
            description=description
        )

        # Check if code already exists
        if self.region_model.objects.filter(code=formatted['code']).exists():
            return {
                'success': False,
                'errors': [f"Kode wilayah '{formatted['code']}' sudah digunakan"]
            }

        # Create the region
        try:
            region = self.region_model.objects.create(
                name=formatted['name'],
                code=formatted['code'],
                description=formatted['description']
            )
            return {
                'success': True,
                'data': self._to_dict(region)
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }

    def update_region(self, region_id: int, name: str = None, code: str = None,
                     description: str = None) -> dict:
        """
        Update an existing fishing zone with validation.
        """
        try:
            region = self.region_model.objects.get(id=region_id)
        except self.region_model.DoesNotExist:
            return {
                'success': False,
                'errors': ['Wilayah penangkapan tidak ditemukan']
            }

        # Get current values for fields not being updated
        current_name = region.name
        current_code = region.code
        current_description = region.description

        # Use provided values or keep current
        new_name = name if name is not None else current_name
        new_code = code if code is not None else current_code
        new_description = description if description is not None else current_description

        # Validate
        validation_result = RegionService.validate_region_data(
            name=new_name,
            code=new_code,
            description=new_description
        )

        if not validation_result.is_valid:
            return {
                'success': False,
                'errors': validation_result.errors
            }

        # Format
        formatted = RegionService.format_region_data(
            name=new_name,
            code=new_code,
            description=new_description
        )

        # Check if code conflicts with another region (excluding self)
        if self.region_model.objects.filter(code=formatted['code']).exclude(id=region_id).exists():
            return {
                'success': False,
                'errors': [f"Kode wilayah '{formatted['code']}' sudah digunakan oleh wilayah lain"]
            }

        # Update
        try:
            region.name = formatted['name']
            region.code = formatted['code']
            region.description = formatted['description']
            region.save()

            return {
                'success': True,
                'data': self._to_dict(region)
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }

    def delete_region(self, region_id: int) -> dict:
        """Delete a fishing zone by ID."""
        try:
            region = self.region_model.objects.get(id=region_id)
            region_name = region.name
            region.delete()
            return {
                'success': True,
                'message': f'Wilayah "{region_name}" berhasil dihapus'
            }
        except self.region_model.DoesNotExist:
            return {
                'success': False,
                'errors': ['Wilayah penangkapan tidak ditemukan']
            }

    def import_regions_from_csv(self, csv_data: str, clear_existing: bool = False) -> dict:
        """
        Import fishing zones from CSV data.
        Returns dict with created, updated, errors counts.
        """
        import csv
        from io import StringIO

        if clear_existing:
            self.region_model._default_manager.all().delete()

        csv_file = StringIO(csv_data)
        reader = csv.DictReader(csv_file)

        if not reader.fieldnames or 'nama' not in reader.fieldnames or 'code' not in reader.fieldnames:
            return {
                'success': False,
                'errors': ['Format CSV tidak valid. Header harus berisi: nama, code, deskripsi']
            }

        created_count = 0
        updated_count = 0
        error_count = 0
        error_details = []

        for row_num, row in enumerate(reader, start=2):  # Start at 2 because header is row 1
            nama = (row.get('nama') or '').strip()
            code = (row.get('code') or '').strip()
            deskripsi = (row.get('deskripsi') or '').strip()

            if not nama:
                error_details.append(f'Baris {row_num}: Nama wajib diisi')
                error_count += 1
                continue

            if not code:
                error_details.append(f'Baris {row_num}: Kode wajib diisi')
                error_count += 1
                continue

            # Validate
            validation_result = RegionService.validate_region_data(
                name=nama,
                code=code,
                description=deskripsi
            )

            if not validation_result.is_valid:
                error_details.append(f'Baris {row_num}: {"; ".join(validation_result.errors)}')
                error_count += 1
                continue

            # Format
            formatted = RegionService.format_region_data(
                name=nama,
                code=code,
                description=deskripsi
            )

            # Check if code exists
            existing = self.region_model.objects.filter(code=formatted['code']).first()
            if existing:
                if existing.name != formatted['name'] or existing.description != formatted['description']:
                    # Update existing
                    existing.name = formatted['name']
                    existing.description = formatted['description']
                    existing.save()
                    updated_count += 1
                continue

            # Create new
            try:
                self.region_model.objects.create(
                    name=formatted['name'],
                    code=formatted['code'],
                    description=formatted['description']
                )
                created_count += 1
            except Exception as e:
                error_details.append(f'Baris {row_num}: {str(e)}')
                error_count += 1

        return {
            'success': True if error_count == 0 else False,
            'created': created_count,
            'updated': updated_count,
            'errors': error_count,
            'error_details': error_details if error_details else None
        }

    def _to_dict(self, region) -> dict:
        """Convert model instance to dictionary."""
        return {
            'id': region.id,
            'code': region.code,
            'name': region.name,
            'description': region.description,
            'is_active': region.is_active,
            'created_at': region.created_at.isoformat() if region.created_at else None,
            'updated_at': region.updated_at.isoformat() if region.updated_at else None,
        }
