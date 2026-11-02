"""
Fish Application Service (Application Layer)
Orchestrates business logic for fish species and catch records.
"""

from typing import Optional, List, Dict, Any
from django.apps import apps

from ..domain.fish_domain import (
    FishSpeciesDomain, FishDomain,
    FishSpeciesDomainService, FishDomainService,
    FishValidationResult
)


class FishSpeciesApplicationService:
    """
    Application service for fish species management.
    """

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = self._get_model('fish', 'FishSpecies')
        return self._model

    def _get_model(self, app_label: str, model_name: str):
        return apps.get_model(app_label, model_name)

    def get_all_species(self) -> List[dict]:
        """Get all fish species."""
        species = self.model.objects.all().order_by('name')
        return [self._to_dict(s) for s in species]

    def get_species_by_id(self, species_id: int) -> Optional[dict]:
        """Get a fish species by ID."""
        try:
            species = self.model.objects.get(id=species_id)
            return self._to_dict(species)
        except self.model.DoesNotExist:
            return None

    def create_species(self, name: str, scientific_name: str = '',
                      description: str = '') -> dict:
        """
        Create a new fish species with validation.
        """
        # Validate using domain service
        validation = FishSpeciesDomainService.validate_species_data(
            name=name,
            scientific_name=scientific_name,
            description=description
        )

        if not validation.is_valid:
            return {
                'success': False,
                'errors': validation.errors
            }

        # Format data
        formatted = FishSpeciesDomainService.format_species_data(
            name=name,
            scientific_name=scientific_name,
            description=description
        )

        # Check if name already exists
        if self.model.objects.filter(name=formatted['name']).exists():
            return {
                'success': False,
                'errors': [f"Spesies ikan '{formatted['name']}' sudah terdaftar"]
            }

        try:
            species = self.model.objects.create(
                name=formatted['name'],
                scientific_name=formatted['scientific_name'],
                description=formatted['description']
            )
            return {
                'success': True,
                'data': self._to_dict(species)
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }

    def update_species(self, species_id: int, name: str = None,
                      scientific_name: str = None,
                      description: str = None) -> dict:
        """
        Update an existing fish species.
        """
        try:
            species = self.model.objects.get(id=species_id)
        except self.model.DoesNotExist:
            return {
                'success': False,
                'errors': ['Spesies ikan tidak ditemukan']
            }

        # Use current values if not provided
        new_name = name if name is not None else species.name
        new_scientific = scientific_name if scientific_name is not None else species.scientific_name
        new_description = description if description is not None else species.description

        # Validate
        validation = FishSpeciesDomainService.validate_species_data(
            name=new_name,
            scientific_name=new_scientific,
            description=new_description
        )

        if not validation.is_valid:
            return {
                'success': False,
                'errors': validation.errors
            }

        # Format
        formatted = FishSpeciesDomainService.format_species_data(
            name=new_name,
            scientific_name=new_scientific,
            description=new_description
        )

        # Check name uniqueness (excluding self)
        if self.model.objects.filter(name=formatted['name']).exclude(id=species_id).exists():
            return {
                'success': False,
                'errors': [f"Nama ikan '{formatted['name']}' sudah digunakan"]
            }

        try:
            species.name = formatted['name']
            species.scientific_name = formatted['scientific_name']
            species.description = formatted['description']
            species.save()
            return {
                'success': True,
                'data': self._to_dict(species)
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }

    def delete_species(self, species_id: int) -> dict:
        """Delete a fish species by ID."""
        try:
            species = self.model.objects.get(id=species_id)
            species_name = species.name
            species.delete()
            return {
                'success': True,
                'message': f'Spesies ikan "{species_name}" berhasil dihapus'
            }
        except self.model.DoesNotExist:
            return {
                'success': False,
                'errors': ['Spesies ikan tidak ditemukan']
            }

    def import_species_from_csv(self, csv_data, clear_existing: bool = False, user=None) -> dict:
        """Import fish species from CSV string or file content."""
        import csv
        from io import StringIO
        from django.core.exceptions import ValidationError

        if clear_existing:
            self.model.objects.all().delete()

        try:
            if hasattr(csv_data, 'read'):
                csv_string = csv_data.read().decode('utf-8')
            elif isinstance(csv_data, bytes):
                csv_string = csv_data.decode('utf-8')
            else:
                csv_string = str(csv_data)

            reader = csv.DictReader(StringIO(csv_string))
            created_count = 0
            updated_count = 0
            error_count = 0
            error_details = []

            for row_num, row in enumerate(reader, start=1):
                try:
                    name = row.get('name', '').strip()
                    scientific_name = row.get('scientific_name', '').strip() or None
                    description = row.get('description', '').strip() or None

                    if not name:
                        error_details.append(f'Row {row_num}: Nama Ikan tidak boleh kosong')
                        error_count += 1
                        continue

                    species, created = self.model.objects.get_or_create(
                        name=name,
                        defaults={
                            'scientific_name': scientific_name,
                            'description': description,
                        }
                    )

                    if created:
                        created_count += 1
                    else:
                        updated = False
                        if scientific_name and species.scientific_name != scientific_name:
                            species.scientific_name = scientific_name
                            updated = True
                        if description and species.description != description:
                            species.description = description
                            updated = True
                        if updated:
                            species.save()
                            updated_count += 1

                except ValidationError as e:
                    error_details.append(f'Row {row_num}: Validation error - {str(e)}')
                    error_count += 1
                except Exception as e:
                    error_details.append(f'Row {row_num}: Unexpected error - {str(e)}')
                    error_count += 1

            return {
                'message': 'Data spesies berhasil diimpor',
                'created': created_count,
                'updated': updated_count,
                'errors': error_count,
                'error_details': error_details if error_details else None
            }
        except Exception as e:
            return {'error': f'Gagal mengimpor CSV: {str(e)}'}

    def get_template_csv(self) -> str:
        """Generate CSV template for fish species."""
        import csv
        from io import StringIO
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['name', 'scientific_name', 'description'])
        writer.writerow(['Ikan Lele', 'Clarias batrachus', 'Ikan air tawar yang populer di Indonesia'])
        return output.getvalue()

    def get_fish_template_csv(self) -> str:
        """Generate CSV template for individual fish."""
        import csv
        from io import StringIO
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['nama_jenis', 'nama_ikan', 'berat_kg', 'catatan'])
        writer.writerow(['Ikan Lele', 'Lele Super', '1.2', 'Ikan berkualitas tinggi'])
        return output.getvalue()

    def _to_dict(self, species) -> dict:
        """Convert model instance to dictionary."""
        return {
            'id': species.id,
            'name': species.name,
            'scientific_name': species.scientific_name,
            'description': species.description,
        }


class FishApplicationService:
    """
    Application service for fish catch records.
    """

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = self._get_model('fish', 'Fish')
        return self._model

    def _get_model(self, app_label: str, model_name: str):
        return apps.get_model(app_label, model_name)

    def get_all_catches(self) -> List[dict]:
        """Get all fish catch records."""
        catches = self.model.objects.all().order_by('-catch_date')
        return [self._to_dict(c) for c in catches]

    def get_catch_by_id(self, catch_id: int) -> Optional[dict]:
        """Get a catch record by ID."""
        try:
            catch = self.model.objects.get(id=catch_id)
            return self._to_dict(catch)
        except self.model.DoesNotExist:
            return None

    def create_catch(self, fish_species: str, weight_kg: float,
                    location: str = '', notes: str = '',
                    ship_registration: str = '') -> dict:
        """
        Create a new catch record with validation.
        """
        # Validate using domain service
        validation = FishDomainService.validate_fish_data(
            fish_species=fish_species,
            weight_kg=weight_kg,
            location=location,
            notes=notes
        )

        if not validation.is_valid:
            return {
                'success': False,
                'errors': validation.errors
            }

        # Format data
        formatted = FishDomainService.format_fish_data(
            fish_species=fish_species,
            weight_kg=weight_kg,
            location=location,
            notes=notes
        )

        try:
            catch = self.model.objects.create(
                fish_species=formatted['fish_species'],
                weight_kg=formatted['weight_kg'],
                location=formatted['location'],
                notes=formatted['notes'],
                ship_registration=ship_registration
            )
            return {
                'success': True,
                'data': self._to_dict(catch)
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }

    def update_catch(self, catch_id: int,
                     fish_species: str = None,
                     weight_kg: float = None,
                     location: str = None,
                     notes: str = None) -> dict:
        """
        Update an existing catch record.
        """
        try:
            catch = self.model.objects.get(id=catch_id)
        except self.model.DoesNotExist:
            return {
                'success': False,
                'errors': ['Laporan tangkapan tidak ditemukan']
            }

        # Use current values if not provided
        new_species = fish_species if fish_species is not None else catch.fish_species
        new_weight = weight_kg if weight_kg is not None else catch.weight_kg
        new_location = location if location is not None else catch.location
        new_notes = notes if notes is not None else catch.notes

        # Validate
        validation = FishDomainService.validate_fish_data(
            fish_species=new_species,
            weight_kg=new_weight,
            location=new_location,
            notes=new_notes
        )

        if not validation.is_valid:
            return {
                'success': False,
                'errors': validation.errors
            }

        try:
            catch.fish_species = new_species
            catch.weight_kg = new_weight
            catch.location = new_location
            catch.notes = new_notes
            catch.save()
            return {
                'success': True,
                'data': self._to_dict(catch)
            }
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }

    def delete_catch(self, catch_id: int) -> dict:
        """Delete a catch record by ID."""
        try:
            catch = self.model.objects.get(id=catch_id)
            species = catch.fish_species
            weight = catch.weight_kg
            catch.delete()
            return {
                'success': True,
                'message': f'Laporan tangkapan {species} ({weight} kg) berhasil dihapus'
            }
        except self.model.DoesNotExist:
            return {
                'success': False,
                'errors': ['Laporan tangkapan tidak ditemukan']
            }

    def import_catches_from_csv(self, csv_data, clear_existing: bool = False, user=None) -> dict:
        """Import individual fish catches from CSV string or file content."""
        import csv
        from io import StringIO
        from decimal import Decimal, InvalidOperation
        from django.core.exceptions import ValidationError

        FishSpecies = self._get_model('fish', 'FishSpecies')

        if clear_existing:
            self.model.objects.all().delete()

        try:
            if hasattr(csv_data, 'read'):
                csv_string = csv_data.read().decode('utf-8')
            elif isinstance(csv_data, bytes):
                csv_string = csv_data.decode('utf-8')
            else:
                csv_string = str(csv_data)

            reader = csv.DictReader(StringIO(csv_string))
            created_count = 0
            updated_count = 0
            error_count = 0
            error_details = []

            for row_num, row in enumerate(reader, start=1):
                try:
                    species_name = row.get('nama_jenis', '').strip()
                    name = row.get('nama_ikan', '').strip() or None
                    weight = row.get('berat_kg', '').strip()
                    notes = row.get('catatan', '').strip() or None

                    if not species_name:
                        error_details.append(f'Row {row_num}: Missing species_name')
                        error_count += 1
                        continue

                    try:
                        species = FishSpecies.objects.get(name=species_name)
                    except FishSpecies.DoesNotExist:
                        error_details.append(f'Row {row_num}: Fish species "{species_name}" not found')
                        error_count += 1
                        continue

                    weight_decimal = None
                    if weight:
                        try:
                            weight_decimal = Decimal(weight)
                        except (ValueError, InvalidOperation):
                            error_details.append(f'Row {row_num}: Invalid weight value "{weight}"')
                            error_count += 1
                            continue

                    fish = self.model(
                        species=species,
                        name=name,
                        weight=weight_decimal,
                        notes=notes
                    )
                    fish.full_clean()
                    fish.save()
                    created_count += 1

                except ValidationError as e:
                    error_details.append(f'Row {row_num}: Validation error - {str(e)}')
                    error_count += 1
                except Exception as e:
                    error_details.append(f'Row {row_num}: Unexpected error - {str(e)}')
                    error_count += 1

            return {
                'message': 'Data sampel ikan berhasil diimpor',
                'created': created_count,
                'updated': updated_count,
                'errors': error_count,
                'error_details': error_details if error_details else None
            }
        except Exception as e:
            return {'error': f'Gagal mengimpor CSV: {str(e)}'}

    def _to_dict(self, catch) -> dict:
        """Convert model instance to dictionary."""
        return {
            'id': catch.id,
            'fish_species': catch.fish_species,
            'weight_kg': catch.weight_kg,
            'location': catch.location,
            'notes': catch.notes,
            'ship_registration': catch.ship_registration,
            'catch_date': catch.catch_date.isoformat() if catch.catch_date else None,
        }
