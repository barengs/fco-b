"""
Catch Views (Presentation Layer)
API Views untuk manajemen data tangkapan ikan dan PNBP predictions.
Facade yang menggunakan Application Layer untuk bisnis logic.
"""

import os
import json
import csv
import io
from datetime import datetime
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.http import HttpResponse
from django.db import transaction

from .models import FishCatch, CatchDetail
from .serializers import FishCatchSerializer, CatchDetailSerializer, FishCatchWithDetailsSerializer
from .presentation.permissions import IsCatchOwnerOrAdmin
from .presentation.views.pnbp_views import (
    predict_pnbp_future,
    get_pnbp_history,
    get_latest_pnbp_predictions,
    get_unified_chart_data,
)
from ships.models import Ship


@extend_schema_view(
    list=extend_schema(
        tags=['Catches'],
        summary='Daftar semua laporan tangkapan',
        description='Mengambil daftar semua laporan tangkapan ikan',
    ),
    create=extend_schema(
        tags=['Catches'],
        summary='Tambah laporan tangkapan baru',
    ),
    retrieve=extend_schema(
        tags=['Catches'],
        summary='Detail laporan tangkapan',
    ),
    update=extend_schema(
        tags=['Catches'],
        summary='Perbarui laporan tangkapan',
    ),
    partial_update=extend_schema(
        tags=['Catches'],
        summary='Perbarui sebagian laporan tangkapan',
    ),
    destroy=extend_schema(
        tags=['Catches'],
        summary='Hapus laporan tangkapan',
    ),
)
class FishCatchViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola laporan tangkapan ikan.
    """
    queryset = FishCatch._default_manager.all().order_by('-catch_date')
    serializer_class = FishCatchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCatchOwnerOrAdmin]

    def perform_create(self, serializer):
        serializer.save()


@extend_schema_view(
    list=extend_schema(
        tags=['Catch Details'],
        summary='Daftar semua detail tangkapan',
        description='Mengambil daftar semua detail tangkapan ikan',
    ),
    create=extend_schema(
        tags=['Catch Details'],
        summary='Tambah detail tangkapan baru',
    ),
    retrieve=extend_schema(
        tags=['Catch Details'],
        summary='Detail detail tangkapan',
    ),
    update=extend_schema(
        tags=['Catch Details'],
        summary='Perbarui detail tangkapan',
    ),
    partial_update=extend_schema(
        tags=['Catch Details'],
        summary='Perbarui sebagian detail tangkapan',
    ),
    destroy=extend_schema(
        tags=['Catch Details'],
        summary='Hapus detail tangkapan',
    ),
)
class CatchDetailViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola detail tangkapan ikan.
    """
    queryset = CatchDetail._default_manager.all()
    serializer_class = CatchDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsCatchOwnerOrAdmin]


@extend_schema_view(
    list=extend_schema(
        tags=['Catch Details'],
        summary='Daftar detail tangkapan lengkap dengan relasi',
        description='Mengambil daftar detail tangkapan ikan lengkap dengan informasi ikan, kapal, dan lokasi',
    ),
    retrieve=extend_schema(
        tags=['Catch Details'],
        summary='Detail lengkap tangkapan',
    ),
)
class FishCatchWithDetailsViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola detail tangkapan ikan dengan data lengkap (relasi).
    """
    queryset = CatchDetail._default_manager.all().select_related('fish_catch', 'fish_catch__ship')
    serializer_class = FishCatchWithDetailsSerializer
    permission_classes = [permissions.IsAuthenticated, IsCatchOwnerOrAdmin]

    @action(detail=False, methods=['post'], url_path='import_csv')
    def import_csv(self, request):
        """Import catch data from CSV content or file"""
        csv_data = request.data.get('csv_data')
        csv_file = request.FILES.get('csv_file')
        dry_run = request.data.get('dry_run', False)

        if isinstance(dry_run, str):
            dry_run = dry_run.lower() in ('true', '1', 'yes', 'on')

        if csv_data:
            if hasattr(csv_data, 'read'):
                try:
                    csv_data = csv_data.read().decode('utf-8')
                except UnicodeDecodeError:
                    return Response(
                        {'error': 'Format CSV harus UTF-8'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        if csv_file:
            MAX_UPLOAD_SIZE = 10 * 1024 * 1024
            if getattr(csv_file, 'size', 0) > MAX_UPLOAD_SIZE:
                return Response(
                    {'error': 'Ukuran file melebihi batas maksimal 10 MB'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                csv_data = csv_file.read().decode('utf-8')
            except UnicodeDecodeError:
                return Response(
                    {'error': 'Format CSV harus UTF-8'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not csv_data:
            return Response(
                {'error': 'Pilih atau unggah file CSV terlebih dahulu'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            csv_reader = csv.DictReader(io.StringIO(csv_data))
            catch_groups = {}

            for row_num, row in enumerate(csv_reader, start=2):
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

                detail = {
                    'fish_species_name': row.get('fish_species_name', '').strip(),
                    'quantity': row.get('quantity', '').strip(),
                    'unit': row.get('unit', 'kg').strip(),
                    'value': row.get('value', '').strip() or None,
                    'notes': row.get('notes', '').strip() or None,
                    'wpp_name': row.get('wpp_name', '').strip() or None
                }

                catch_groups[catch_key]['catch_details'].append(detail)

        except Exception as e:
            return Response(
                {'error': f'Error parsing CSV data: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        success_count = 0
        error_count = 0
        results = []

        for catch_key, catch_data in catch_groups.items():
            try:
                from ships.models import Ship, Quota
                from fish.models import FishSpecies
                from regions.models import FishingArea
                from owners.models import Owner, Captain

                with transaction.atomic():
                    ship = self._get_or_create_ship_api(catch_data, dry_run)

                    if not dry_run:
                        year = int(catch_data['catch_date'].split('-')[0])
                        self._get_or_create_quota_api(ship, year, catch_data.get('quota_amount'))

                    try:
                        validated_data = self._validate_catch_data_api(catch_data, ship, dry_run)
                    except Exception as ve:
                        results.append({
                            'status': 'error',
                            'message': f'Validation error: {str(ve)}'
                        })
                        error_count += 1
                        continue

                    if dry_run:
                        results.append({
                            'status': 'would_import',
                            'message': f'Would import: Ship {catch_data["ship_registration"]} - {catch_data["catch_date"]} - {len(catch_data["catch_details"])} species'
                        })
                    else:
                        serializer = FishCatchWithDetailsSerializer(data=validated_data)
                        if serializer.is_valid():
                            serializer.save()
                            success_count += 1
                            results.append({
                                'status': 'success',
                                'message': f'Imported: Ship {catch_data["ship_registration"]} - {catch_data["catch_date"]}'
                            })
                        else:
                            results.append({
                                'status': 'error',
                                'message': f'Validation error: {serializer.errors}'
                            })
                            error_count += 1

            except Exception as e:
                results.append({
                    'status': 'error',
                    'message': f'Error importing {catch_key}: {str(e)}'
                })
                error_count += 1

        response_data = {
            'total_processed': len(catch_groups),
            'success_count': success_count,
            'error_count': error_count,
            'dry_run': dry_run,
            'results': results
        }

        return Response(response_data)

    @action(detail=False, methods=['get'], url_path='download_template', permission_classes=[permissions.AllowAny])
    def download_template(self, request):
        """Download CSV template for catch data import"""
        template_data = [
            ['ship_registration', 'ship_name', 'owner_name', 'captain_name', 'captain_license', 'quota_amount', 'catch_date', 'catch_type', 'location_latitude', 'location_longitude', 'description', 'fish_species_name', 'quantity', 'unit', 'value', 'notes', 'wpp_name'],
            ['ABC123', 'Kapal Maju Jaya', 'Ahmad Surya', 'Nahkoda Rahman', 'LSN123456', '50000', '2024-01-15', 'pelagic', '-6.2088', '106.8456', 'Tangkapan pagi hari', 'Tuna Sirip Kuning', '150.50', 'kg', '750000', 'Catch bagus', 'WPP 711'],
            ['ABC123', 'Kapal Maju Jaya', 'Ahmad Surya', 'Nahkoda Rahman', 'LSN123456', '50000', '2024-01-15', 'pelagic', '-6.2088', '106.8456', 'Tangkapan pagi hari', 'Ikan Kakap', '75.25', 'kg', '375000', 'Catch sedang', 'WPP 711'],
            ['DEF456', 'Kapal Bahari', 'PT. Samudra Jaya', 'Kapten Budi', 'LSN789012', '75000', '2024-01-16', 'demersal', '-7.7956', '110.3695', 'Tangkapan sore', 'Ikan Kerapu', '45.00', 'kg', '225000', '', 'WPP 712']
        ]

        output = io.StringIO()
        writer = csv.writer(output)
        for row in template_data:
            writer.writerow(row)

        csv_content = output.getvalue()
        output.close()

        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="catch_data_import_template.csv"'

        return response

    def _get_or_create_ship_api(self, catch_data, dry_run=False):
        from ships.models import Ship
        from owners.models import Owner, Captain

        ship_registration = catch_data['ship_registration']

        try:
            ship = Ship.objects.get(registration_number=ship_registration)
            return ship
        except Ship.DoesNotExist:
            pass

        owner = self._get_or_create_owner_api(catch_data['owner_name'], dry_run)
        captain = self._get_or_create_captain_api(
            catch_data['captain_name'],
            catch_data['captain_license'],
            owner,
            dry_run
        )

        if not dry_run:
            ship = Ship.objects.create(
                name=catch_data['ship_name'],
                registration_number=ship_registration,
                owner=owner,
                captain=captain
            )
        else:
            ship = Ship(
                name=catch_data['ship_name'],
                registration_number=ship_registration,
                owner=owner,
                captain=captain
            )

        return ship

    def _get_or_create_owner_api(self, owner_name, dry_run=False):
        from owners.models import Owner

        try:
            owner = Owner.objects.get(full_name=owner_name)
            return owner
        except Owner.DoesNotExist:
            if not dry_run:
                owner = Owner.objects.create(
                    full_name=owner_name,
                    owner_type='individual'
                )
            else:
                owner = Owner(full_name=owner_name, owner_type='individual')
            return owner

    def _get_or_create_captain_api(self, captain_name, license_number, owner, dry_run=False):
        from owners.models import Captain

        try:
            captain = Captain.objects.get(license_number=license_number)
            return captain
        except Captain.DoesNotExist:
            if not dry_run:
                captain = Captain.objects.create(
                    full_name=captain_name,
                    license_number=license_number,
                    owner=owner
                )
            else:
                captain = Captain(full_name=captain_name, license_number=license_number, owner=owner)
            return captain

    def _get_or_create_quota_api(self, ship, year, quota_amount_str):
        from ships.models import Quota

        try:
            quota = Quota.objects.get(ship=ship, year=year, is_active=True)
            return quota
        except Quota.DoesNotExist:
            if quota_amount_str:
                try:
                    quota_amount = float(quota_amount_str)
                    quota = Quota.objects.create(
                        ship=ship,
                        year=year,
                        quota=quota_amount,
                        remaining_quota=quota_amount
                    )
                    return quota
                except ValueError:
                    pass

    def _validate_catch_data_api(self, catch_data, ship, dry_run=False):
        from fish.models import FishSpecies
        from regions.models import FishingArea

        validated_details = []
        for detail in catch_data['catch_details']:
            try:
                fish_species = FishSpecies.objects.get(name=detail['fish_species_name'])
            except FishSpecies.DoesNotExist:
                if not dry_run:
                    fish_species = FishSpecies.objects.create(
                        name=detail['fish_species_name'],
                        description=f"Auto-created from import: {detail['fish_species_name']}"
                    )
                else:
                    fish_species = FishSpecies(name=detail['fish_species_name'])

            wpp = None
            if detail['wpp_name']:
                try:
                    wpp = FishingArea.objects.get(nama=detail['wpp_name'])
                except FishingArea.DoesNotExist:
                    pass

            validated_details.append({
                'fish_species': fish_species,
                'quantity': float(detail['quantity'] or 0),
                'unit': detail.get('unit', 'kg'),
                'value': float(detail['value']) if detail.get('value') else None,
                'notes': detail.get('notes') or '',
                'wpp': wpp,
                'tarif_index': 0,
                'pnkp': 0,
                'pnbp': 0,
            })

        return {
            'ship': ship,
            'catch_date': catch_data['catch_date'],
            'catch_type': catch_data.get('catch_type', ''),
            'location_latitude': catch_data.get('location_latitude') or 0,
            'location_longitude': catch_data.get('location_longitude') or 0,
            'description': catch_data.get('description', ''),
            'catch_details': validated_details,
        }


__all__ = [
    'IsCatchOwnerOrAdmin',
    'FishCatchViewSet',
    'CatchDetailViewSet',
    'FishCatchWithDetailsViewSet',
    'predict_pnbp_future',
    'get_pnbp_history',
    'get_latest_pnbp_predictions',
    'get_unified_chart_data',
]
