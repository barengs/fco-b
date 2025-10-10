import csv
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import transaction
from django.apps import apps
from catches.serializers import FishCatchWithDetailsSerializer
from ships.models import Ship, Quota
from fish.models import FishSpecies
from regions.models import FishingArea
from owners.models import Owner, Captain

class Command(BaseCommand):
    help = 'Import catch data from CSV file with auto-creation of ships, owners, captains, and quotas'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing',
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        dry_run = options['dry_run']

        # Dictionary untuk mengelompokkan data berdasarkan tangkapan unik
        catch_groups = {}

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row_num, row in enumerate(reader, start=2):
                    # Buat key unik untuk setiap tangkapan
                    catch_key = (
                        row.get('ship_registration', '').strip(),
                        row.get('catch_date', '').strip(),
                        row.get('catch_type', '').strip(),
                        row.get('location_latitude', '').strip(),
                        row.get('location_longitude', '').strip(),
                        row.get('description', '').strip() or ''
                    )

                    if catch_key not in catch_groups:
                        catch_groups[catch_key] = {
                            'ship_registration': catch_key[0],
                            'ship_name': row.get('ship_name', '').strip(),
                            'owner_name': row.get('owner_name', '').strip(),
                            'captain_name': row.get('captain_name', '').strip(),
                            'captain_license': row.get('captain_license', '').strip(),
                            'quota_amount': row.get('quota_amount', '').strip(),
                            'catch_date': catch_key[1],
                            'catch_type': catch_key[2],
                            'location_latitude': catch_key[3],
                            'location_longitude': catch_key[4],
                            'description': catch_key[5],
                            'catch_details': []
                        }

                    # Tambahkan detail spesies ke tangkapan ini
                    detail = {
                        'fish_species_name': row.get('fish_species_name', '').strip(),
                        'quantity': row.get('quantity', '').strip(),
                        'unit': row.get('unit', 'kg').strip(),
                        'value': row.get('value', '').strip() or None,
                        'notes': row.get('notes', '').strip() or None,
                        'wpp_name': row.get('wpp_name', '').strip() or None
                    }

                    catch_groups[catch_key]['catch_details'].append(detail)

            # Proses setiap tangkapan
            success_count = 0
            error_count = 0

            for catch_key, catch_data in catch_groups.items():
                try:
                    with transaction.atomic():
                        # Auto-create ship, owner, captain, quota jika belum ada
                        ship = self._get_or_create_ship(catch_data, dry_run)

                        if not dry_run:
                            # Pastikan quota ada untuk tahun tangkapan
                            year = int(catch_data['catch_date'].split('-')[0])
                            self._get_or_create_quota(ship, year, catch_data.get('quota_amount'))

                        # Validasi dan konversi data
                        validated_data = self._validate_catch_data(catch_data, ship)

                        if dry_run:
                            self.stdout.write(
                                f'Would import: Ship {catch_data["ship_registration"]} - {catch_data["catch_date"]} - {len(catch_data["catch_details"])} species'
                            )
                        else:
                            # Gunakan serializer untuk create
                            serializer = FishCatchWithDetailsSerializer(data=validated_data)
                            if serializer.is_valid():
                                serializer.save()
                                success_count += 1
                                self.stdout.write(
                                    f'Imported: Ship {catch_data["ship_registration"]} - {catch_data["catch_date"]}'
                                )
                            else:
                                self.stdout.write(
                                    f'Validation error for {catch_key}: {serializer.errors}'
                                )
                                error_count += 1

                except Exception as e:
                    self.stdout.write(
                        f'Error importing {catch_key}: {str(e)}'
                    )
                    error_count += 1

            if dry_run:
                self.stdout.write(
                    f'Dry run completed. Would import {len(catch_groups)} catches'
                )
            else:
                self.stdout.write(
                    f'Import completed. Success: {success_count}, Errors: {error_count}'
                )

        except FileNotFoundError:
            self.stdout.write(f'File not found: {csv_file_path}')
        except Exception as e:
            self.stdout.write(f'Error reading CSV file: {e}')

    def _get_or_create_ship(self, catch_data, dry_run=False):
        """Mendapatkan atau membuat ship beserta owner dan captain"""
        ship_registration = catch_data['ship_registration']

        # Cek apakah ship sudah ada
        try:
            ship = Ship.objects.get(registration_number=ship_registration)
            if dry_run:
                self.stdout.write(f'Would use existing ship: {ship.name} ({ship_registration})')
            return ship
        except Ship.DoesNotExist:
            pass

        # Ship belum ada, buat owner dulu
        owner = self._get_or_create_owner(catch_data['owner_name'], dry_run)

        # Buat captain
        captain = self._get_or_create_captain(
            catch_data['captain_name'],
            catch_data['captain_license'],
            owner,
            dry_run
        )

        # Buat ship
        if dry_run:
            self.stdout.write(
                f'Would create ship: {catch_data["ship_name"]} ({ship_registration}) with owner {owner.full_name} and captain {captain.full_name}'
            )
            # Return dummy ship object untuk dry run
            ship = Ship(
                name=catch_data['ship_name'],
                registration_number=ship_registration,
                owner=owner,
                captain=captain
            )
            return ship
        else:
            ship = Ship.objects.create(
                name=catch_data['ship_name'],
                registration_number=ship_registration,
                owner=owner,
                captain=captain
            )
            self.stdout.write(f'Created ship: {ship.name} ({ship_registration})')
            return ship

    def _get_or_create_owner(self, owner_name, dry_run=False):
        """Mendapatkan atau membuat owner"""
        try:
            owner = Owner.objects.get(full_name=owner_name)
            if dry_run:
                self.stdout.write(f'Would use existing owner: {owner_name}')
            return owner
        except Owner.DoesNotExist:
            if dry_run:
                self.stdout.write(f'Would create owner: {owner_name}')
                # Return dummy owner untuk dry run
                owner = Owner(full_name=owner_name, owner_type='individual')
                return owner
            else:
                owner = Owner.objects.create(
                    full_name=owner_name,
                    owner_type='individual'  # Default sebagai perorangan
                )
                self.stdout.write(f'Created owner: {owner_name}')
                return owner

    def _get_or_create_captain(self, captain_name, license_number, owner, dry_run=False):
        """Mendapatkan atau membuat captain"""
        try:
            captain = Captain.objects.get(license_number=license_number)
            if dry_run:
                self.stdout.write(f'Would use existing captain: {captain_name} ({license_number})')
            return captain
        except Captain.DoesNotExist:
            if dry_run:
                self.stdout.write(f'Would create captain: {captain_name} ({license_number})')
                # Return dummy captain untuk dry run
                captain = Captain(full_name=captain_name, license_number=license_number, owner=owner)
                return captain
            else:
                captain = Captain.objects.create(
                    full_name=captain_name,
                    license_number=license_number,
                    owner=owner
                )
                self.stdout.write(f'Created captain: {captain_name} ({license_number})')
                return captain

    def _get_or_create_quota(self, ship, year, quota_amount_str):
        """Mendapatkan atau membuat quota untuk ship dan tahun tertentu"""
        try:
            quota = Quota.objects.get(ship=ship, year=year, is_active=True)
            self.stdout.write(f'Using existing quota for {ship.name} {year}: {quota.quota} kg')
            return quota
        except Quota.DoesNotExist:
            if quota_amount_str:
                try:
                    quota_amount = float(quota_amount_str)
                    quota = Quota.objects.create(
                        ship=ship,
                        year=year,
                        quota=quota_amount,
                        remaining_quota=quota_amount  # Awalnya remaining = total
                    )
                    self.stdout.write(f'Created quota for {ship.name} {year}: {quota_amount} kg')
                    return quota
                except ValueError:
                    self.stdout.write(f'Invalid quota amount: {quota_amount_str}, skipping quota creation')
            else:
                self.stdout.write(f'No quota amount provided for {ship.name} {year}, skipping quota creation')

    def _validate_catch_data(self, catch_data, ship):
        """Validasi dan konversi data sebelum import"""
        # Validasi catch_details
        validated_details = []
        for detail in catch_data['catch_details']:
            # Validasi fish_species - auto-create jika belum ada
            try:
                fish_species = FishSpecies.objects.get(name=detail['fish_species_name'])
            except FishSpecies.DoesNotExist:
                if not dry_run:
                    fish_species = FishSpecies.objects.create(
                        name=detail['fish_species_name'],
                        description=f"Auto-created from import: {detail['fish_species_name']}"
                    )
                    self.stdout.write(f'Created fish species: {detail["fish_species_name"]}')
                else:
                    # For dry run, create a mock object
                    fish_species = FishSpecies(name=detail['fish_species_name'])

            # Validasi WPP jika ada
            wpp = None
            if detail['wpp_name']:
                try:
                    wpp = FishingArea.objects.get(nama=detail['wpp_name'])
                except FishingArea.DoesNotExist:
                    self.stdout.write(
                        f"Warning: WPP '{detail['wpp_name']}' not found, skipping WPP assignment"
                    )

            # Konversi quantity dan value
            try:
                quantity = float(detail['quantity'])
            except ValueError:
                raise ValidationError(f"Invalid quantity: {detail['quantity']}")

            value = None
            if detail['value']:
                try:
                    value = float(detail['value'])
                except ValueError:
                    raise ValidationError(f"Invalid value: {detail['value']}")

            validated_details.append({
                'fish_species': fish_species.id,
                'quantity': quantity,
                'unit': detail['unit'],
                'value': value,
                'notes': detail['notes'],
                'wpp': wpp.id if wpp else None
            })

        return {
            'ship': ship.registration_number,  # Gunakan registration number untuk serializer
            'catch_date': catch_data['catch_date'],
            'catch_type': catch_data['catch_type'],
            'location_latitude': float(catch_data['location_latitude']),
            'location_longitude': float(catch_data['location_longitude']),
            'description': catch_data['description'],
            'catch_details': validated_details
        }