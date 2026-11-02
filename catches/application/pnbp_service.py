"""
PNBP Prediction Application Service (Application Layer)
Orchestrates PNBP prediction using multiple ML models.
"""

from typing import Optional, Dict, Any, List

from ..infrastructure.pnbp_predictor import PNBPredictor


class PNBPredictionService:
    """
    Application service for PNBP prediction.
    Orchestrates multiple ML models via infrastructure layer.
    """

    def __init__(self):
        self._predictor = None

    @property
    def predictor(self) -> PNBPredictor:
        if self._predictor is None:
            self._predictor = PNBPredictor()
        return self._predictor

    def predict_pnbp_future(
        self,
        historical_data: Optional[list] = None,
        ships_data: Optional[list] = None,
        use_database_data: bool = True,
    ) -> dict:
        """
        Run complete PNBP prediction pipeline using 4 methods.
        """
        if historical_data is None and use_database_data:
            historical_data = self.predictor.get_historical_data_from_django()

        return self.predictor.run_prediction_pipeline(
            historical_data=historical_data,
            ships_data=ships_data,
        )

    def get_pnbp_history(self) -> list:
        """
        Get historical PNBP data from Django models.
        """
        return self.predictor.get_historical_data_from_django()

    def get_latest_pnbp_predictions(self) -> dict:
        """
        Get latest PNBP predictions from saved JSON file.
        """
        return self.predictor.data_manager.load_historical_data(
            'data/samples/pnbp_predictions.json'
        )

    def get_unified_chart_data(self) -> dict:
        """
        Get unified chart data combining historical PNBP, predictions, and quota data.
        """
        predictor = self.predictor

        # 1. Get historical PNBP data
        historical_data = predictor.get_historical_data_from_django()

        # 2. Get latest PNBP predictions
        pnbp_predictions = None
        try:
            pnbp_predictions = predictor.data_manager.load_historical_data(
                'data/samples/pnbp_predictions.json'
            )
        except Exception:
            pnbp_predictions = None

        # 3. Get quota prediction for first ship with data
        quota_predictions = None
        if historical_data:
            ships_with_data = list(set([
                item.get('nama_kapal') for item in historical_data
                if item.get('nama_kapal')
            ]))
            if ships_with_data:
                from ships.ml_models import predict_and_optimize_quota
                ship_name = ships_with_data[0]
                from ships.models import Ship
                ship_obj = Ship.objects.filter(name=ship_name).first()
                if ship_obj:
                    quota_result = predict_and_optimize_quota(
                        ship_obj.registration_number, 6, 3
                    )
                    if not isinstance(quota_result, dict) or 'error' not in quota_result:
                        quota_predictions = {
                            'ship_name': ship_name,
                            'ship_registration': ship_obj.registration_number,
                            'predictions': quota_result
                        }
        # 4. Calculate summary statistics
        summary_stats = {}
        if historical_data:
            pnbp_values = [
                item.get('total_pnbp', 0)
                for item in historical_data
                if item.get('total_pnbp')
            ]
            volume_values = [
                item.get('total_volume', 0)
                for item in historical_data
                if item.get('total_volume')
            ]

            if pnbp_values:
                summary_stats = {
                    'total_historical_records': len(historical_data),
                    'total_pnbp_sum': sum(pnbp_values),
                    'avg_pnbp_per_record': sum(pnbp_values) / len(pnbp_values),
                    'max_pnbp': max(pnbp_values),
                    'min_pnbp': min(pnbp_values),
                    'total_volume_sum': sum(volume_values) if volume_values else 0,
                    'avg_volume_per_record': (
                        sum(volume_values) / len(volume_values)
                        if volume_values else 0
                    ),
                    'unique_ships': len(set([
                        item.get('nama_kapal')
                        for item in historical_data
                        if item.get('nama_kapal')
                    ])),
                }

        charts_data = {
            'historical_pnbp': {
                'data': historical_data,
                'count': len(historical_data),
                'chart_type': 'line',
                'x_axis': 'timestamp',
                'y_axis': 'total_pnbp',
                'title': 'Historical PNBP Trends'
            },
            'pnbp_predictions': {
                'data': pnbp_predictions,
                'available': pnbp_predictions is not None,
                'chart_type': 'bar',
                'title': 'PNBP Prediction Methods Comparison'
            },
            'quota_predictions': {
                'data': quota_predictions,
                'available': quota_predictions is not None,
                'chart_type': 'line',
                'title': 'Ship Quota Predictions (LSTM vs NSGA-III)'
            },
            'summary_stats': summary_stats
        }

        return {
            'status': 'success',
            'charts_data': charts_data,
            'message': 'Data grafik berhasil dimuat'
        }
