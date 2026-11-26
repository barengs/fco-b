"""
Quota Application Service (Application Layer / Use Case)
Orchestrates vessel quota predictions and manual quota assignments.
Coordinates between domain policies, machine learning infrastructure, and persistence.
"""

import logging
from typing import Dict, Any
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist

from ..domain.quota_policy import QuotaPolicy
from ..infrastructure.ml import predict_and_optimize_quota

logger = logging.getLogger(__name__)


class QuotaApplicationService:
    """
    Application service orchestrating fishing quota use cases.
    Encapsulates business operations away from presentation views.
    """

    def __init__(self):
        self._ship_model = None
        self._quota_model = None

    @property
    def ship_model(self):
        if self._ship_model is None:
            self._ship_model = apps.get_model('ships', 'Ship')
        return self._ship_model

    @property
    def quota_model(self):
        if self._quota_model is None:
            self._quota_model = apps.get_model('ships', 'Quota')
        return self._quota_model

    def predict_quota_for_ship(
        self,
        ship_registration_number: str,
        prediction_months: int = 12,
        epoch_level: int = 5,
    ) -> Dict[str, Any]:
        """
        Execute AI quota forecasting (LSTM + NSGA-III) for a registered vessel.
        """
        try:
            ship = self.ship_model._default_manager.get(registration_number=ship_registration_number)
        except ObjectDoesNotExist:
            return {
                'error': f'Kapal dengan nomor registrasi {ship_registration_number} tidak ditemukan.',
                'status_code': 404,
            }

        try:
            optimized_results = predict_and_optimize_quota(
                ship_registration_number, prediction_months, epoch_level
            )
        except Exception:
            logger.exception("Gagal menghitung prediksi kuota untuk kapal %s", ship_registration_number)
            return {
                'error': 'Gagal menghitung prediksi kuota kapal.',
                'status_code': 500,
            }

        if isinstance(optimized_results, dict) and "error" in optimized_results:
            return {
                'error': optimized_results["error"],
                'status_code': 400,
            }

        response_data = optimized_results.copy()
        response_data['ship_registration_number'] = response_data.pop(
            'ship_registration', ship_registration_number
        )
        response_data['ship_name'] = ship.name

        return {'data': response_data, 'status_code': 200}

    def assign_manual_quota(
        self,
        ship_registration_number: str,
        year: int,
        quota_amount: float,
    ) -> Dict[str, Any]:
        """
        Assign or update vessel quota as determined by regulators.
        """
        try:
            ship = self.ship_model._default_manager.get(registration_number=ship_registration_number)
        except ObjectDoesNotExist:
            return {
                'error': f'Kapal dengan nomor registrasi {ship_registration_number} tidak ditemukan.',
                'status_code': 404,
            }

        quota, created = self.quota_model.objects.update_or_create(
            ship=ship,
            year=year,
            defaults={
                'quota': quota_amount,
                'remaining_quota': quota_amount,
                'is_active': True,
            },
        )

        action = "ditetapkan" if created else "diperbarui"
        response_data = {
            'ship_registration_number': ship.registration_number,
            'ship_name': ship.name,
            'year': year,
            'quota_amount': quota.quota,
            'remaining_quota': quota.remaining_quota,
            'message': f'Kuota kapal {ship.name} tahun {year} berhasil {action} ({quota.quota} kg).',
        }

        return {'data': response_data, 'status_code': 200}
