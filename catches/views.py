from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
import csv
import io
import json
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
from platypus import NSGAIII, Problem, Real
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

from .models import FishCatch, CatchDetail
from .serializers import FishCatchSerializer, CatchDetailSerializer, FishCatchWithDetailsSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(
        tags=['Fish Catches'],
        summary='Daftar semua laporan tangkapan ikan',
        description='''Mengambil daftar semua laporan tangkapan ikan dengan opsi filter.
        
Fitur:
- Pembuatan laporan tangkapan ikan
- Detail tangkapan berdasarkan spesies
- Manajemen data tangkapan
- Filter berdasarkan kapal dan rentang tanggal

Filter yang Tersedia:
- ship_id: Memfilter berdasarkan ID kapal
- start_date: Memfilter berdasarkan tanggal awal tangkapan (format: YYYY-MM-DD)
- end_date: Memfilter berdasarkan tanggal akhir tangkapan (format: YYYY-MM-DD)
        '''
    ),
    create=extend_schema(
        tags=['Fish Catches'],
        summary='Buat laporan tangkapan ikan',
        description='Membuat laporan tangkapan ikan baru dengan detail spesies dan jumlah.'
    ),
    retrieve=extend_schema(
        tags=['Fish Catches'],
        summary='Ambil laporan tangkapan ikan',
        description='Mengambil laporan tangkapan ikan tertentu berdasarkan ID.'
    ),
    update=extend_schema(
        tags=['Fish Catches'],
        summary='Perbarui laporan tangkapan ikan',
        description='Memperbarui laporan tangkapan ikan yang ada.'
    ),
    partial_update=extend_schema(
        tags=['Fish Catches'],
        summary='Perbarui sebagian laporan tangkapan ikan',
        description='Memperbarui sebagian informasi laporan tangkapan ikan yang ada.'
    ),
    destroy=extend_schema(
        tags=['Fish Catches'],
        summary='Hapus laporan tangkapan ikan',
        description='Menghapus laporan tangkapan ikan dari sistem.'
    )
)
class FishCatchViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola laporan tangkapan ikan.
    
    Fitur:
    - Manajemen laporan tangkapan ikan (CRUD)
    - Filter berdasarkan kapal dan rentang tanggal
    - Relasi dengan detail tangkapan (spesies dan jumlah)
    - Integrasi dengan data kapal dan area penangkapan
    
    Hak Akses:
    - Pengguna yang diautentikasi dapat membuat, memperbarui, dan menghapus
    - Pengguna anonim hanya dapat melihat data
    """
    queryset = FishCatch._default_manager.all()  # type: ignore
    serializer_class = FishCatchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Secara opsional membatasi tangkapan yang dikembalikan berdasarkan kapal atau rentang tanggal tertentu"""
        queryset = FishCatch._default_manager.all()  # type: ignore
        ship_id = self.request.query_params.get('ship_id', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if ship_id is not None:
            queryset = queryset.filter(ship_id=ship_id)
        
        if start_date is not None:
            queryset = queryset.filter(catch_date__gte=start_date)
            
        if end_date is not None:
            queryset = queryset.filter(catch_date__lte=end_date)
            
        return queryset

@extend_schema_view(
    create=extend_schema(
        tags=['Fish Catches'],
        summary='Buat laporan tangkapan ikan dengan detail',
        description='Membuat laporan tangkapan ikan baru dengan detail spesies dan jumlah dalam satu permintaan.'
    ),
    update=extend_schema(
        tags=['Fish Catches'],
        summary='Perbarui laporan tangkapan ikan dengan detail',
        description='Memperbarui laporan tangkapan ikan yang ada beserta detail spesies dan jumlah dalam satu permintaan.'
    )
)
class FishCatchWithDetailsViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola laporan tangkapan ikan dengan detail dalam satu endpoint.
    
    Fitur:
    - Membuat laporan tangkapan ikan dengan detail dalam satu permintaan
    - Memperbarui laporan tangkapan ikan beserta detail dalam satu permintaan
    - Mengambil laporan tangkapan ikan dengan detail terkait
    """
    queryset = FishCatch._default_manager.all()  # type: ignore
    serializer_class = FishCatchWithDetailsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Secara opsional membatasi tangkapan yang dikembalikan berdasarkan kapal atau rentang tanggal tertentu"""
        queryset = FishCatch._default_manager.all()  # type: ignore
        ship_id = self.request.query_params.get('ship_id', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if ship_id is not None:
            queryset = queryset.filter(ship_id=ship_id)
        
        if start_date is not None:
            queryset = queryset.filter(catch_date__gte=start_date)
            
        if end_date is not None:
            queryset = queryset.filter(catch_date__lte=end_date)
            
        return queryset.prefetch_related('catch_details', 'catch_details__fish_species', 'ship')

    @action(detail=False, methods=['post'], url_path='import_csv')
    def import_csv(self, request):
        """Import catch data from CSV content or file"""
        csv_data = request.data.get('csv_data')
        csv_file = request.FILES.get('csv_file')
        dry_run = request.data.get('dry_run', False)

        # Convert dry_run to boolean if it's a string
        if isinstance(dry_run, str):
            dry_run = dry_run.lower() in ('true', '1', 'yes', 'on')

        # Handle csv_data - could be string or InMemoryUploadedFile
        if csv_data:
            if hasattr(csv_data, 'read'):  # It's an InMemoryUploadedFile
                try:
                    csv_data = csv_data.read().decode('utf-8')
                except UnicodeDecodeError:
                    return Response(
                        {'error': 'CSV data must be encoded in UTF-8'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            # else it's already a string

        # Handle file upload
        if csv_file:
            try:
                csv_data = csv_file.read().decode('utf-8')
            except UnicodeDecodeError:
                return Response(
                    {'error': 'CSV file must be encoded in UTF-8'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not csv_data:
            return Response(
                {'error': 'Either csv_data field or csv_file upload is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parse CSV data
        try:
            csv_reader = csv.DictReader(io.StringIO(csv_data))
            catch_groups = {}

            for row_num, row in enumerate(csv_reader, start=2):
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

        except Exception as e:
            return Response(
                {'error': f'Error parsing CSV data: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Process imports
        success_count = 0
        error_count = 0
        results = []

        for catch_key, catch_data in catch_groups.items():
            try:
                from django.db import transaction
                from ships.models import Ship, Quota
                from fish.models import FishSpecies
                from regions.models import FishingArea
                from owners.models import Owner, Captain

                with transaction.atomic():
                    # Auto-create ship, owner, captain, quota jika belum ada
                    ship = self._get_or_create_ship_api(catch_data, dry_run)

                    if not dry_run:
                        # Pastikan quota ada untuk tahun tangkapan
                        year = int(catch_data['catch_date'].split('-')[0])
                        self._get_or_create_quota_api(ship, year, catch_data.get('quota_amount'))

                    # Validasi dan konversi data
                    try:
                        validated_data = self._validate_catch_data_api(catch_data, ship, dry_run)
                    except ValidationError as ve:
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
                        # Gunakan serializer untuk create
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

    @action(detail=False, methods=['get'], url_path='download_template')
    def download_template(self, request):
        """Download CSV template for catch data import"""
        # Create CSV template content
        template_data = [
            ['ship_registration', 'ship_name', 'owner_name', 'captain_name', 'captain_license', 'quota_amount', 'catch_date', 'catch_type', 'location_latitude', 'location_longitude', 'description', 'fish_species_name', 'quantity', 'unit', 'value', 'notes', 'wpp_name'],
            ['ABC123', 'Kapal Maju Jaya', 'Ahmad Surya', 'Nahkoda Rahman', 'LSN123456', '50000', '2024-01-15', 'pelagic', '-6.2088', '106.8456', 'Tangkapan pagi hari', 'Tuna Sirip Kuning', '150.50', 'kg', '750000', 'Catch bagus', 'WPP 711'],
            ['ABC123', 'Kapal Maju Jaya', 'Ahmad Surya', 'Nahkoda Rahman', 'LSN123456', '50000', '2024-01-15', 'pelagic', '-6.2088', '106.8456', 'Tangkapan pagi hari', 'Ikan Kakap', '75.25', 'kg', '375000', 'Catch sedang', 'WPP 711'],
            ['DEF456', 'Kapal Bahari', 'PT. Samudra Jaya', 'Kapten Budi', 'LSN789012', '75000', '2024-01-16', 'demersal', '-7.7956', '110.3695', 'Tangkapan sore', 'Ikan Kerapu', '45.00', 'kg', '225000', '', 'WPP 712']
        ]

        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        for row in template_data:
            writer.writerow(row)

        csv_content = output.getvalue()
        output.close()

        # Create HTTP response
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="catch_data_import_template.csv"'

        return response

    def _get_or_create_ship_api(self, catch_data, dry_run=False):
        """Mendapatkan atau membuat ship beserta owner dan captain"""
        from ships.models import Ship
        from owners.models import Owner, Captain

        ship_registration = catch_data['ship_registration']

        # Cek apakah ship sudah ada
        try:
            ship = Ship.objects.get(registration_number=ship_registration)
            return ship
        except Ship.DoesNotExist:
            pass

        # Ship belum ada, buat owner dulu
        owner = self._get_or_create_owner_api(catch_data['owner_name'], dry_run)

        # Buat captain
        captain = self._get_or_create_captain_api(
            catch_data['captain_name'],
            catch_data['captain_license'],
            owner,
            dry_run
        )

        # Buat ship
        if not dry_run:
            ship = Ship.objects.create(
                name=catch_data['ship_name'],
                registration_number=ship_registration,
                owner=owner,
                captain=captain
            )
        else:
            # For dry run, create a mock ship object
            ship = Ship(
                name=catch_data['ship_name'],
                registration_number=ship_registration,
                owner=owner,
                captain=captain
            )

        return ship

    def _get_or_create_owner_api(self, owner_name, dry_run=False):
        """Mendapatkan atau membuat owner"""
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
        """Mendapatkan atau membuat captain"""
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
        """Mendapatkan atau membuat quota untuk ship dan tahun tertentu"""
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
        """Validasi dan konversi data sebelum import"""
        from fish.models import FishSpecies
        from regions.models import FishingArea

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
                else:
                    # For dry run, create a mock object
                    fish_species = FishSpecies(name=detail['fish_species_name'])

            # Validasi WPP jika ada
            wpp = None
            if detail['wpp_name']:
                try:
                    wpp = FishingArea.objects.get(nama=detail['wpp_name'])
                except FishingArea.DoesNotExist:
                    pass  # Skip WPP assignment if not found

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
            'ship': ship.registration_number,
            'catch_date': catch_data['catch_date'],
            'catch_type': catch_data['catch_type'],
            'location_latitude': float(catch_data['location_latitude']),
            'location_longitude': float(catch_data['location_longitude']),
            'description': catch_data['description'],
            'catch_details': validated_details
        }

@extend_schema_view(
    list=extend_schema(
        tags=['Fish Catches'],
        summary='Daftar semua detail tangkapan',
        description='''Mengambil daftar semua detail tangkapan (spesies dan jumlah).
        
Fitur:
- Detail tangkapan berdasarkan spesies
- Informasi kuantitas dan berat tangkapan
- Catatan tambahan untuk setiap detail tangkapan'''
    ),
    create=extend_schema(
        tags=['Fish Catches'],
        summary='Buat detail tangkapan',
        description='Membuat detail tangkapan baru dengan spesies ikan dan jumlah.'
    ),
    retrieve=extend_schema(
        tags=['Fish Catches'],
        summary='Ambil detail tangkapan',
        description='Mengambil detail tangkapan tertentu berdasarkan ID.'
    ),
    update=extend_schema(
        tags=['Fish Catches'],
        summary='Perbarui detail tangkapan',
        description='Memperbarui detail tangkapan yang ada.'
    ),
    partial_update=extend_schema(
        tags=['Fish Catches'],
        summary='Perbarui sebagian detail tangkapan',
        description='Memperbarui sebagian informasi detail tangkapan yang ada.'
    ),
    destroy=extend_schema(
        tags=['Fish Catches'],
        summary='Hapus detail tangkapan',
        description='Menghapus detail tangkapan dari sistem.'
    )
)
class CatchDetailViewSet(viewsets.ModelViewSet):
    """
    ViewSet untuk mengelola detail tangkapan (spesies dan jumlah).

    Fitur:
    - Manajemen detail tangkapan (CRUD)
    - Relasi dengan laporan tangkapan utama
    - Relasi dengan data spesies ikan
    - Informasi kuantitas dan catatan tambahan

    Hak Akses:
    - Pengguna yang diautentikasi dapat membuat, memperbarui, dan menghapus
    - Pengguna anonim hanya dapat melihat data
    """
    queryset = CatchDetail._default_manager.all()  # type: ignore
    serializer_class = CatchDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# -----------------------------------------------------------------------------------
# PNBP Prediction Classes
# -----------------------------------------------------------------------------------

class PNBPRegressionPredictor:
    """Prediktor PNBP menggunakan Analisis Regresi"""

    @staticmethod
    def predict(historical_data):
        """
        Analisis Regresi untuk memprediksi PNBP berdasarkan hubungan antara
        variabel produksi, harga ikan, biaya operasional, dan kapasitas kapal.
        """
        if len(historical_data) < 3:
            return PNBPRegressionPredictor._fallback_prediction(historical_data)

        # Prepare features: volume, GT (simulated), operational costs (simulated)
        features = []
        targets = []

        for item in historical_data:
            volume = item.get('total_volume', 100)
            gt = item.get('gt_kapal', 60)  # Default GT
            operational_cost = volume * 0.1  # Simulated operational cost
            features.append([volume, gt, operational_cost])
            targets.append(item.get('total_pnbp', 0))

        try:
            # Train regression model
            model = LinearRegression()
            model.fit(features, targets)

            # Predict for next period (assume average values)
            avg_volume = np.mean([f[0] for f in features])
            avg_gt = np.mean([f[1] for f in features])
            avg_cost = np.mean([f[2] for f in features])

            prediction = model.predict([[avg_volume, avg_gt, avg_cost]])[0]
            return max(0, prediction)
        except Exception as e:
            print(f"Regression prediction error: {e}")
            return PNBPRegressionPredictor._fallback_prediction(historical_data)

    @staticmethod
    def _fallback_prediction(historical_data):
        """Fallback prediction using simple average"""
        if not historical_data:
            return 0
        return np.mean([item.get('total_pnbp', 0) for item in historical_data])


class PNBPNeuralNetworkPredictor:
    """Prediktor PNBP menggunakan Jaringan Saraf"""

    @staticmethod
    def predict(historical_data):
        """
        Jaringan Saraf untuk mendeteksi pola non-linear dan tren jangka panjang pada data historis PNBP.
        """
        if len(historical_data) < 5:
            return PNBPNeuralNetworkPredictor._fallback_prediction(historical_data)

        # Prepare time series data
        pnbp_values = [item.get('total_pnbp', 0) for item in historical_data]

        # Create features: lagged values
        X = []
        y = []
        for i in range(3, len(pnbp_values)):
            X.append(pnbp_values[i-3:i])
            y.append(pnbp_values[i])

        if len(X) < 2:
            return PNBPNeuralNetworkPredictor._fallback_prediction(historical_data)

        try:
            # Train neural network
            model = MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=1000, random_state=42)
            model.fit(X, y)

            # Predict next value
            last_sequence = pnbp_values[-3:]
            prediction = model.predict([last_sequence])[0]
            return max(0, prediction)
        except Exception as e:
            print(f"Neural network prediction error: {e}")
            return PNBPNeuralNetworkPredictor._fallback_prediction(historical_data)

    @staticmethod
    def _fallback_prediction(historical_data):
        """Fallback prediction using simple average"""
        if not historical_data:
            return 0
        return np.mean([item.get('total_pnbp', 0) for item in historical_data])


class PNBPOptimizationPredictor:
    """Prediktor PNBP menggunakan Optimasi Multi-Objektif NSGA-III"""

    @staticmethod
    def predict(historical_data, ships_data=None):
        """
        Optimasi Multi-Objektif untuk mencari kombinasi variabel optimal
        yang memaksimalkan potensi pendapatan dengan tetap menjaga keberlanjutan.
        """
        if not ships_data or len(ships_data) == 0:
            return PNBPOptimizationPredictor._fallback_prediction(historical_data)

        num_ships = len(ships_data)

        def pnbp_objective_function(vars):
            # vars represent efficiency factors for each ship
            efficiencies = np.array(vars)

            # Calculate potential PNBP based on efficiency and historical data
            avg_historical_pnbp = np.mean([item.get('total_pnbp', 0) for item in historical_data])
            base_pnbp = avg_historical_pnbp * 0.8  # Conservative base

            # Efficiency-weighted PNBP
            efficiency_bonus = np.sum(efficiencies) * avg_historical_pnbp * 0.2

            total_pnbp = base_pnbp + efficiency_bonus

            # Objectives: maximize PNBP, minimize resource usage variance, minimize environmental impact
            resource_variance = np.var(efficiencies)
            environmental_impact = np.sum(efficiencies > 1.2) * 100  # Penalty for over-efficiency

            return [-total_pnbp, resource_variance, environmental_impact]

        try:
            problem = Problem(num_ships, 3)
            problem.types[:] = Real(0.5, 1.5)
            problem.function = pnbp_objective_function

            algorithm = NSGAIII(problem, divisions_outer=12, divisions_inner=2)
            algorithm.run(100)

            if not algorithm.result:
                return PNBPOptimizationPredictor._fallback_prediction(historical_data)

            # Use the best solution
            best_solution = algorithm.result[0]
            predicted_pnbp = -best_solution.objectives[0]  # Negate because we maximized negative

            return max(0, predicted_pnbp)
        except Exception as e:
            print(f"Optimization prediction error: {e}")
            return PNBPOptimizationPredictor._fallback_prediction(historical_data)

    @staticmethod
    def _fallback_prediction(historical_data):
        """Fallback prediction using simple average"""
        if not historical_data:
            return 0
        return np.mean([item.get('total_pnbp', 0) for item in historical_data])


class PNBPTimeSeriesPredictor:
    """Prediktor PNBP menggunakan Peramalan Deret Waktu"""

    @staticmethod
    def predict(historical_data):
        """
        Peramalan Deret Waktu untuk memprediksi nilai PNBP di periode mendatang
        berdasarkan pola musiman dan fluktuasi tahunan.
        """
        if len(historical_data) < 5:
            return PNBPTimeSeriesPredictor._fallback_prediction(historical_data)

        # Extract PNBP time series
        pnbp_values = [item.get('total_pnbp', 0) for item in historical_data]

        try:
            # Fit ARIMA model (p=1, d=1, q=1) - common starting point
            model = ARIMA(pnbp_values, order=(1, 1, 1))
            model_fit = model.fit()

            # Forecast next value
            forecast = model_fit.forecast(steps=1)[0]
            return max(0, forecast)
        except Exception as e:
            print(f"Time series prediction error: {e}")
            return PNBPTimeSeriesPredictor._fallback_prediction(historical_data)

    @staticmethod
    def _fallback_prediction(historical_data):
        """Fallback prediction using exponential smoothing"""
        if not historical_data:
            return 0

        pnbp_values = [item.get('total_pnbp', 0) for item in historical_data]
        if len(pnbp_values) >= 2:
            alpha = 0.3
            smoothed = pnbp_values[0]
            for value in pnbp_values[1:]:
                smoothed = alpha * value + (1 - alpha) * smoothed
            return max(0, smoothed)
        else:
            return np.mean(pnbp_values)


class PNBPDataManager:
    """Manajer data untuk PNBP predictions"""

    @staticmethod
    def load_historical_data(filepath="pnbp_history.json"):
        """Load historical PNBP data from JSON file"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            print(f"Error loading historical data: {e}")
            return []

    @staticmethod
    def save_predictions_to_json(predictions_data, filename="pnbp_predictions.json"):
        """Menyimpan hasil prediksi PNBP ke file JSON"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        data_to_save = {
            'timestamp': timestamp,
            'predictions': predictions_data
        }

        try:
            with open(filename, 'w') as f:
                json.dump(data_to_save, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving predictions: {e}")
            return False

    @staticmethod
    def get_django_historical_data():
        """Get historical PNBP data from Django models"""
        try:
            # Get data from CatchDetail model
            catch_details = CatchDetail.objects.all().order_by('fish_catch__catch_date')
            historical_data = []

            for detail in catch_details:
                if detail.pnbp and detail.pnbp > 0:
                    historical_data.append({
                        'date': detail.fish_catch.catch_date.isoformat(),
                        'total_volume': float(detail.quantity),
                        'total_pnbp': float(detail.pnbp),
                        'gt_kapal': float(detail.fish_catch.ship.gross_tonnage) if detail.fish_catch.ship.gross_tonnage else 60
                    })

            return historical_data
        except Exception as e:
            print(f"Error getting Django historical data: {e}")
            return []


class PNBPredictor:
    """Main class untuk menjalankan prediksi PNBP"""

    def __init__(self):
        self.regression_predictor = PNBPRegressionPredictor()
        self.neural_predictor = PNBPNeuralNetworkPredictor()
        self.optimization_predictor = PNBPOptimizationPredictor()
        self.time_series_predictor = PNBPTimeSeriesPredictor()
        self.data_manager = PNBPDataManager()

    def run_prediction_pipeline(self, historical_data=None, ships_data=None):
        """
        Menjalankan pipeline prediksi PNBP lengkap dengan 4 metode.
        """
        if historical_data is None:
            historical_data = self.data_manager.load_historical_data()

        predictions = {}

        # 1. Regression Analysis
        predictions['regression'] = self.regression_predictor.predict(historical_data)

        # 2. Neural Network
        predictions['neural_network'] = self.neural_predictor.predict(historical_data)

        # 3. NSGA-III Optimization
        predictions['nsga3_optimization'] = self.optimization_predictor.predict(historical_data, ships_data)

        # 4. Time Series Forecasting
        predictions['time_series'] = self.time_series_predictor.predict(historical_data)

        # 5. Normalize results
        normalized_predictions = self._normalize_predictions(predictions)

        # 6. Calculate weighted average
        final_prediction = self._calculate_weighted_average(normalized_predictions)

        return {
            'individual_predictions': predictions,
            'normalized_predictions': normalized_predictions,
            'final_prediction': final_prediction,
            'timestamp': datetime.now().isoformat(),
            'methods_used': ['regression', 'neural_network', 'nsga3_optimization', 'time_series']
        }

    def _normalize_predictions(self, predictions):
        """Normalisasi hasil prediksi menggunakan MinMaxScaler"""
        if not predictions:
            return {}

        values = list(predictions.values())
        scaler = MinMaxScaler()
        normalized_values = scaler.fit_transform(np.array(values).reshape(-1, 1)).flatten()

        return dict(zip(predictions.keys(), normalized_values))

    def _calculate_weighted_average(self, normalized_predictions):
        """Menghitung rata-rata tertimbang dari prediksi ternormalisasi"""
        weights = {
            'regression': 0.25,
            'neural_network': 0.35,
            'nsga3_optimization': 0.25,
            'time_series': 0.15
        }

        weighted_sum = 0
        total_weight = 0

        for method, prediction in normalized_predictions.items():
            if method in weights:
                weighted_sum += prediction * weights[method]
                total_weight += weights[method]

        if total_weight == 0:
            return 0

        return weighted_sum / total_weight

    def save_results(self, predictions_data, filename="pnbp_predictions.json"):
        """Menyimpan hasil prediksi ke file JSON"""
        return self.data_manager.save_predictions_to_json(predictions_data, filename)

    def get_historical_data_from_django(self):
        """Mendapatkan data historis dari model Django"""
        return self.data_manager.get_django_historical_data()


# -----------------------------------------------------------------------------------
# PNBP Prediction API Views
# -----------------------------------------------------------------------------------

@extend_schema(
    tags=['PNBP Predictions'],
    summary='Prediksi PNBP masa depan menggunakan 4 metode',
    description='''
    Melakukan prediksi PNBP (Penerimaan Negara Bukan Pajak) sektor perikanan menggunakan 4 metode:

    1. **Analisis Regresi** - Menganalisis hubungan antara variabel produksi, harga ikan, biaya operasional, dan kapasitas kapal
    2. **Jaringan Saraf (Neural Network)** - Mendeteksi pola non-linear dan tren jangka panjang pada data historis
    3. **Optimasi Multi-Objektif (NSGA-III)** - Mencari kombinasi optimal yang memaksimalkan pendapatan dengan menjaga keberlanjutan
    4. **Peramalan Deret Waktu** - Memprediksi berdasarkan pola musiman dan fluktuasi tahunan

    Hasil akhir adalah rata-rata tertimbang dengan bobot: Regresi 25%, Neural Network 35%, NSGA-III 25%, Time Series 15%.
    '''
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def predict_pnbp_future(request):
    """
    API endpoint untuk prediksi PNBP masa depan menggunakan 4 metode analisis.
    """
    try:
        # Initialize predictor
        predictor = PNBPredictor()

        # Get historical data from database if requested
        use_db_data = request.data.get('use_database_data', True)

        if use_db_data:
            historical_data = predictor.get_historical_data_from_django()
        else:
            # Use provided data or load from file
            historical_data = request.data.get('historical_data')
            if not historical_data:
                historical_data = predictor.data_manager.load_historical_data()

        # Get ships data if provided
        ships_data = request.data.get('ships_data')

        # Run prediction pipeline
        predictions = predictor.run_prediction_pipeline(historical_data, ships_data)

        # Optionally save results
        if request.data.get('save_results', False):
            predictor.save_results(predictions)

        return Response({
            'status': 'success',
            'predictions': predictions,
            'message': 'PNBP prediction completed successfully'
        })

    except Exception as e:
        return Response(
            {'error': f'Prediction failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['PNBP Predictions'],
    summary='Dapatkan data historis PNBP',
    description='Mengambil data historis PNBP dari database Django atau file JSON.'
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_pnbp_history(request):
    """
    API endpoint untuk mendapatkan data historis PNBP.
    """
    try:
        predictor = PNBPredictor()

        # Get data source preference
        source = request.query_params.get('source', 'database')

        if source == 'database':
            historical_data = predictor.get_historical_data_from_django()
        else:
            historical_data = predictor.data_manager.load_historical_data()

        return Response({
            'status': 'success',
            'source': source,
            'data_count': len(historical_data),
            'historical_data': historical_data
        })

    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve historical data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    tags=['PNBP Predictions'],
    summary='Dapatkan hasil prediksi PNBP terakhir',
    description='Mengambil hasil prediksi PNBP yang tersimpan dari file JSON.'
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_latest_pnbp_predictions(request):
    """
    API endpoint untuk mendapatkan hasil prediksi PNBP terakhir.
    """
    try:
        filename = "pnbp_predictions.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                predictions_data = json.load(f)

            return Response({
                'status': 'success',
                'predictions': predictions_data
            })
        else:
            return Response({
                'status': 'not_found',
                'message': 'No saved predictions found'
            }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve predictions: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )