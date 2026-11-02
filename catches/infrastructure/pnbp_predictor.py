"""
PNBP Machine Learning & Statistical Predictors (Infrastructure Layer)
Ensemble models for forecasting Non-Tax State Revenue (PNBP):
1. Multivariate Linear Regression
2. Multi-Layer Perceptron (Neural Network)
3. NSGA-III Multi-Objective Genetic Optimizer
4. ARIMA Time-Series Model
"""

import os
import json
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.arima.model import ARIMA
from platypus import NSGAIII, Problem, Real
from django.apps import apps

class PNBPRegressionPredictor:
    """Prediktor PNBP menggunakan Analisis Regresi Multivariat."""

    @staticmethod
    def predict(historical_data):
        if len(historical_data) < 3:
            return PNBPRegressionPredictor._fallback_prediction(historical_data)

        features = []
        targets = []

        for item in historical_data:
            volume = item.get('total_volume', 100)
            gt = item.get('gt_kapal', 60)
            operational_cost = volume * 0.1
            features.append([volume, gt, operational_cost])
            targets.append(item.get('total_pnbp', 0))

        try:
            model = LinearRegression()
            model.fit(features, targets)

            avg_volume = np.mean([f[0] for f in features])
            avg_gt = np.mean([f[1] for f in features])
            avg_cost = np.mean([f[2] for f in features])

            prediction = model.predict([[avg_volume, avg_gt, avg_cost]])[0]
            return max(0, prediction)
        except Exception:
            return PNBPRegressionPredictor._fallback_prediction(historical_data)

    @staticmethod
    def _fallback_prediction(historical_data):
        if not historical_data:
            return 0
        return np.mean([item.get('total_pnbp', 0) for item in historical_data])

class PNBPNeuralNetworkPredictor:
    """Prediktor PNBP menggunakan Jaringan Saraf Tiruan (MLPRegressor)."""

    @staticmethod
    def predict(historical_data):
        if len(historical_data) < 5:
            return PNBPNeuralNetworkPredictor._fallback_prediction(historical_data)

        pnbp_values = [item.get('total_pnbp', 0) for item in historical_data]

        X, y = [], []
        for i in range(3, len(pnbp_values)):
            X.append(pnbp_values[i-3:i])
            y.append(pnbp_values[i])

        if len(X) < 2:
            return PNBPNeuralNetworkPredictor._fallback_prediction(historical_data)

        try:
            model = MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=1000, random_state=42)
            model.fit(X, y)
            last_sequence = pnbp_values[-3:]
            prediction = model.predict([last_sequence])[0]
            return max(0, prediction)
        except Exception:
            return PNBPNeuralNetworkPredictor._fallback_prediction(historical_data)

    @staticmethod
    def _fallback_prediction(historical_data):
        if not historical_data:
            return 0
        return np.mean([item.get('total_pnbp', 0) for item in historical_data])

class PNBPOptimizationPredictor:
    """Prediktor PNBP menggunakan Optimasi Multi-Objektif NSGA-III."""

    @staticmethod
    def predict(historical_data, ships_data=None):
        if not ships_data or len(ships_data) == 0:
            return PNBPOptimizationPredictor._fallback_prediction(historical_data)

        num_ships = len(ships_data)

        def pnbp_objective_function(vars):
            efficiencies = np.array(vars)
            avg_historical_pnbp = np.mean([item.get('total_pnbp', 0) for item in historical_data])
            base_pnbp = avg_historical_pnbp * 0.8
            efficiency_bonus = np.sum(efficiencies) * avg_historical_pnbp * 0.2
            total_pnbp = base_pnbp + efficiency_bonus

            resource_variance = np.var(efficiencies)
            environmental_impact = np.sum(efficiencies > 1.2) * 100
            return [-total_pnbp, resource_variance, environmental_impact]

        try:
            problem = Problem(num_ships, 3)
            problem.types[:] = Real(0.5, 1.5)
            problem.function = pnbp_objective_function

            algorithm = NSGAIII(problem, divisions_outer=12, divisions_inner=2)
            algorithm.run(100)

            if not algorithm.result:
                return PNBPOptimizationPredictor._fallback_prediction(historical_data)

            best_solution = algorithm.result[0]
            return max(0, -best_solution.objectives[0])
        except Exception:
            return PNBPOptimizationPredictor._fallback_prediction(historical_data)

    @staticmethod
    def _fallback_prediction(historical_data):
        if not historical_data:
            return 0
        return np.mean([item.get('total_pnbp', 0) for item in historical_data])

class PNBPTimeSeriesPredictor:
    """Prediktor PNBP menggunakan Peramalan Deret Waktu ARIMA."""

    @staticmethod
    def predict(historical_data):
        if len(historical_data) < 5:
            return PNBPTimeSeriesPredictor._fallback_prediction(historical_data)

        pnbp_values = [item.get('total_pnbp', 0) for item in historical_data]

        try:
            model = ARIMA(pnbp_values, order=(1, 1, 1))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=1)[0]
            return max(0, forecast)
        except Exception:
            return PNBPTimeSeriesPredictor._fallback_prediction(historical_data)

    @staticmethod
    def _fallback_prediction(historical_data):
        if not historical_data:
            return 0
        pnbp_values = [item.get('total_pnbp', 0) for item in historical_data]
        if len(pnbp_values) >= 2:
            alpha = 0.3
            smoothed = pnbp_values[0]
            for value in pnbp_values[1:]:
                smoothed = alpha * value + (1 - alpha) * smoothed
            return max(0, smoothed)
        return np.mean(pnbp_values)

class PNBPDataManager:
    """Manajer data untuk PNBP predictions."""

    @staticmethod
    def load_historical_data(filepath="data/samples/pnbp_history.json"):
        # Fallback to local root if data/samples does not have it yet
        candidates = [filepath, "pnbp_history.json", os.path.join(os.path.dirname(__file__), "../../data/samples/pnbp_history.json")]
        for path in candidates:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        return json.load(f)
                except Exception:
                    pass
        return []

    @staticmethod
    def save_predictions_to_json(predictions_data, filename="data/samples/pnbp_predictions.json"):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_to_save = {
            'timestamp': timestamp,
            'predictions': predictions_data
        }
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as f:
                json.dump(data_to_save, f, indent=2, default=str)
            return True
        except Exception:
            return False

    @staticmethod
    def get_django_historical_data():
        try:
            CatchDetail = apps.get_model('catches', 'CatchDetail')
            catch_details = CatchDetail.objects.select_related('fish_catch', 'fish_catch__ship').all().order_by('fish_catch__catch_date')
            historical_data = []

            for detail in catch_details:
                pnbp_val = detail.pnbp
                if not pnbp_val or float(pnbp_val) <= 0:
                    try:
                        detail.calculate_pnbp()
                        pnbp_val = detail.pnbp
                    except Exception:
                        pnbp_val = None

                if not pnbp_val or float(pnbp_val) <= 0:
                    vol = float(detail.quantity or 0)
                    val = float(detail.value or 0)
                    pnbp_val = round(val * 0.05 if val > 0 else vol * 18000.0 * 0.05, 2)

                gt_val = 60.0
                if hasattr(detail.fish_catch, 'ship') and detail.fish_catch.ship and detail.fish_catch.ship.gross_tonnage:
                    gt_val = float(detail.fish_catch.ship.gross_tonnage)

                historical_data.append({
                    'date': detail.fish_catch.catch_date.isoformat(),
                    'total_volume': float(detail.quantity),
                    'total_pnbp': float(pnbp_val),
                    'gt_kapal': gt_val
                })

            return historical_data
        except Exception:
            return []

class PNBPredictor:
    """Kelas utama orkestrasi peramalan ensemble PNBP 4-metode."""

    def __init__(self):
        self.regression_predictor = PNBPRegressionPredictor()
        self.neural_predictor = PNBPNeuralNetworkPredictor()
        self.optimization_predictor = PNBPOptimizationPredictor()
        self.time_series_predictor = PNBPTimeSeriesPredictor()
        self.data_manager = PNBPDataManager()

    def run_prediction_pipeline(self, historical_data=None, ships_data=None):
        if historical_data is None:
            historical_data = self.data_manager.load_historical_data()

        predictions = {
            'regression': self.regression_predictor.predict(historical_data),
            'neural_network': self.neural_predictor.predict(historical_data),
            'nsga3_optimization': self.optimization_predictor.predict(historical_data, ships_data),
            'time_series': self.time_series_predictor.predict(historical_data),
        }

        normalized_predictions = self._normalize_predictions(predictions)
        final_prediction = self._calculate_weighted_average(normalized_predictions)

        return {
            'individual_predictions': predictions,
            'normalized_predictions': normalized_predictions,
            'final_prediction': final_prediction,
            'timestamp': datetime.now().isoformat(),
            'methods_used': ['regression', 'neural_network', 'nsga3_optimization', 'time_series']
        }

    def _normalize_predictions(self, predictions):
        if not predictions:
            return {}
        values = list(predictions.values())
        scaler = MinMaxScaler()
        normalized_values = scaler.fit_transform(np.array(values).reshape(-1, 1)).flatten()
        return dict(zip(predictions.keys(), normalized_values))

    def _calculate_weighted_average(self, normalized_predictions):
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

        return (weighted_sum / total_weight) if total_weight > 0 else 0

    def save_results(self, predictions_data, filename="data/samples/pnbp_predictions.json"):
        return self.data_manager.save_predictions_to_json(predictions_data, filename)

    def get_historical_data_from_django(self):
        return self.data_manager.get_django_historical_data()
