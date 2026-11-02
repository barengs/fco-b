"""
Catch Application Service (Application Layer)
Orchestrates business logic for catch reports and PNBP predictions.
Delegates to domain rules and infrastructure providers.
"""

from typing import Optional, Dict, Any, List
from django.apps import apps

from ..domain.pnbp_rules import PnbpRules
from ..infrastructure.pnbp_predictor import PNBPredictor


class CatchApplicationService:
    """
    Application service for managing fish catch reports.
    Orchestrates domain rules and infrastructure providers.
    """

    def __init__(self):
        self._catch_detail_model = None
        self._fish_catch_model = None

    @property
    def catch_detail_model(self):
        if self._catch_detail_model is None:
            self._catch_detail_model = self._get_model('catches', 'CatchDetail')
        return self._catch_detail_model

    @property
    def fish_catch_model(self):
        if self._fish_catch_model is None:
            self._fish_catch_model = self._get_model('catches', 'FishCatch')
        return self._fish_catch_model

    def _get_model(self, app_label: str, model_name: str):
        return apps.get_model(app_label, model_name)

    def get_catch_details_for_ship(self, ship_id: int, limit: int = 100) -> List[dict]:
        """
        Get catch details for a specific ship.
        """
        details = self.catch_detail_model.objects.filter(
            fish_catch__ship_id=ship_id
        ).order_by('-fish_catch__catch_date')[:limit]

        return [
            {
                'id': detail.id,
                'fish_catch_id': detail.fish_catch_id,
                'fish_species': detail.fish_species.name if detail.fish_species else None,
                'quantity': float(detail.quantity) if detail.quantity else 0,
                'unit': detail.unit,
                'pnbp': float(detail.pnbp) if detail.pnbp else 0,
                'catch_date': detail.fish_catch.catch_date.isoformat() if detail.fish_catch.catch_date else None,
            }
            for detail in details
        ]

    def calculate_pnbp_for_catch(self, quantity_kg: float, tariff_percent: float = 0.05, base_price_per_kg: float = 20000.0) -> dict:
        """
        Calculate PNBP for a catch using domain rules.
        """
        pnbp_amount = PnbpRules.calculate_catch_pnbp(
            quantity_kg=quantity_kg,
            tariff_percent=tariff_percent,
            base_price_per_kg=base_price_per_kg
        )
        production_value = float(quantity_kg) * float(base_price_per_kg)

        return {
            'quantity_kg': float(quantity_kg),
            'tariff_percent': float(tariff_percent),
            'base_price_per_kg': float(base_price_per_kg),
            'production_value': production_value,
            'pnbp_amount': float(pnbp_amount),
        }
