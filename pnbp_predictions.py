"""
Modul Prediksi PNBP (Penerimaan Negara Bukan Pajak) Sektor Perikanan

Modul ini menyediakan fungsi-fungsi untuk memprediksi PNBP menggunakan 4 metode:
1. Analisis Regresi
2. Jaringan Saraf (Neural Network)
3. Optimasi Multi-Objektif (NSGA-III)
4. Peramalan Deret Waktu (Time Series Forecasting)

Modul ini terintegrasi dengan model Django yang ada untuk mengakses data historis PNBP.
"""

import json
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
import os
from datetime import datetime

warnings.filterwarnings('ignore')

# Import Django models
try:
    from catches.models import CatchDetail, Tariff
    from ships.models import Ship
    from fish.models import FishSpecies
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    print("Warning: Django models not available. Some functions may not work properly.")


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
        if not DJANGO_AVAILABLE:
            return []

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


class PNBPVisualizer:
    """Visualisasi hasil prediksi PNBP"""

    @staticmethod
    def create_comparison_chart(predictions_data):
        """
        Membuat visualisasi perbandingan antar-metode dan hasil final.
        """
        try:
            methods = list(predictions_data['individual_predictions'].keys())
            values = list(predictions_data['individual_predictions'].values())

            # Create bar chart
            plt.figure(figsize=(14, 8))

            # Individual predictions
            plt.subplot(2, 2, 1)
            bars = plt.bar(methods, values, color=['blue', 'green', 'red', 'orange'])
            plt.title('Prediksi PNBP per Metode', fontsize=12, fontweight='bold')
            plt.ylabel('Nilai PNBP (Rp)', fontsize=10)
            plt.xticks(rotation=45, fontsize=8)

            # Add value labels on bars
            for bar, value in zip(bars, values):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_y() + bar.get_height(),
                        f'Rp {value:,.0f}', ha='center', va='bottom', fontsize=8)

            # Normalized predictions and final result
            plt.subplot(2, 2, 2)
            normalized_methods = list(predictions_data['normalized_predictions'].keys())
            normalized_values = list(predictions_data['normalized_predictions'].values())

            bars_norm = plt.bar(normalized_methods, normalized_values,
                               color=['lightblue', 'lightgreen', 'lightcoral', 'orange'])
            plt.axhline(y=predictions_data['final_prediction'], color='red', linestyle='--',
                       label=f'Final Prediction: {predictions_data["final_prediction"]:.3f}')
            plt.title('Prediksi PNBP Ternormalisasi & Final', fontsize=12, fontweight='bold')
            plt.ylabel('Nilai Ternormalisasi', fontsize=10)
            plt.xticks(rotation=45, fontsize=8)
            plt.legend(fontsize=8)

            # Pie chart for weights
            plt.subplot(2, 2, 3)
            weights = {
                'regression': 0.25,
                'neural_network': 0.35,
                'nsga3_optimization': 0.25,
                'time_series': 0.15
            }
            labels = ['Regresi (25%)', 'Neural Network (35%)', 'NSGA-III (25%)', 'Time Series (15%)']
            sizes = list(weights.values())
            colors = ['blue', 'green', 'red', 'orange']
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            plt.title('Bobot Metode Prediksi', fontsize=12, fontweight='bold')

            # Line chart showing historical trend + prediction
            plt.subplot(2, 2, 4)
            # This would need historical data to plot trend
            plt.title('Trend Historis + Prediksi', fontsize=12, fontweight='bold')
            plt.text(0.5, 0.5, 'Data historis diperlukan\nuntuk menampilkan trend',
                    ha='center', va='center', transform=plt.gca().transAxes, fontsize=10)

            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"Error creating visualization: {e}")


class PNBPredictor:
    """Main class untuk menjalankan prediksi PNBP"""

    def __init__(self):
        self.regression_predictor = PNBPRegressionPredictor()
        self.neural_predictor = PNBPNeuralNetworkPredictor()
        self.optimization_predictor = PNBPOptimizationPredictor()
        self.time_series_predictor = PNBPTimeSeriesPredictor()
        self.data_manager = PNBPDataManager()
        self.visualizer = PNBPVisualizer()

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

    def visualize_results(self, predictions_data):
        """Menampilkan visualisasi hasil prediksi"""
        self.visualizer.create_comparison_chart(predictions_data)

    def get_historical_data_from_django(self):
        """Mendapatkan data historis dari model Django"""
        return self.data_manager.get_django_historical_data()


# Utility functions for easy access
def predict_pnbp_future(historical_data=None, ships_data=None):
    """
    Fungsi utility untuk memprediksi PNBP masa depan
    """
    predictor = PNBPredictor()
    return predictor.run_prediction_pipeline(historical_data, ships_data)


def save_pnbp_predictions(predictions_data, filename="pnbp_predictions.json"):
    """
    Fungsi utility untuk menyimpan hasil prediksi
    """
    predictor = PNBPredictor()
    return predictor.save_results(predictions_data, filename)


def visualize_pnbp_predictions(predictions_data):
    """
    Fungsi utility untuk memvisualisasikan hasil prediksi
    """
    predictor = PNBPredictor()
    predictor.visualize_results(predictions_data)


if __name__ == "__main__":
    # Example usage
    predictor = PNBPredictor()

    # Load historical data
    historical_data = predictor.data_manager.load_historical_data()

    # Run prediction
    results = predictor.run_prediction_pipeline(historical_data)

    print("PNBP Prediction Results:")
    print(f"Regression: Rp {results['individual_predictions']['regression']:,.0f}")
    print(f"Neural Network: Rp {results['individual_predictions']['neural_network']:,.0f}")
    print(f"NSGA-III Optimization: Rp {results['individual_predictions']['nsga3_optimization']:,.0f}")
    print(f"Time Series: Rp {results['individual_predictions']['time_series']:,.0f}")
    print(f"Final Prediction: {results['final_prediction']:.4f} (normalized)")

    # Save results
    predictor.save_results(results)

    # Visualize (uncomment to show plot)
    # predictor.visualize_results(results)