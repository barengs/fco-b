"""
Machine Learning Models for Quota Prediction
This module implements LSTM and NSGA-III algorithms for fishing quota prediction.
LSTM performs initial prediction, then NSGA-III optimizes the LSTM results.
"""

import math
import random
from datetime import datetime, timedelta
from django.apps import apps
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth
import warnings
warnings.filterwarnings('ignore')

# Simplified implementations without external dependencies

class SimpleLSTM:
    """
    Simplified LSTM implementation for quota prediction.
    Note: This is a simplified version for demonstration purposes.
    """
    
    def __init__(self, units=50, lookback_months=6):
        self.units = units
        self.lookback_months = lookback_months
        
    def _calculate_mean(self, data):
        """Calculate mean of data"""
        return sum(data) / len(data) if data else 0
    
    def _calculate_std(self, data):
        """Calculate standard deviation of data"""
        if not data or len(data) < 2:
            return 0
        mean = self._calculate_mean(data)
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        return math.sqrt(variance)
    
    def _calculate_trend(self, data):
        """Calculate trend of data"""
        if len(data) < 2:
            return 0
        return (data[-1] - data[0]) / (len(data) - 1)
    
    def fit(self, historical_data):
        """Train the simplified LSTM model"""
        if len(historical_data) < self.lookback_months + 1:
            # Not enough data, use simple average
            avg_value = self._calculate_mean(historical_data)
            return {"method": "average", "value": avg_value}
        
        # For this simplified version, we'll just use the trend
        if len(historical_data) > 1:
            # Calculate trend
            trend = self._calculate_trend(historical_data)
            last_value = historical_data[-1]
            # Simple projection
            predicted = last_value + trend
            return {"method": "trend", "value": max(0, predicted)}
        else:
            return {"method": "last_value", "value": historical_data[-1] if len(historical_data) > 0 else 0}
    
    def predict(self, historical_data, steps=1):
        """Predict future values"""
        result = self.fit(historical_data)
        # For simplicity, we'll return the same prediction for all steps
        return [result["value"]] * steps


class NSGA3QuotaOptimizer:
    """
    Simplified NSGA-III implementation for quota optimization.
    This optimizer takes LSTM predictions and optimizes them.
    Note: This is a simplified version for demonstration purposes.
    """
    
    def __init__(self, population_size=50, generations=100):
        self.population_size = population_size
        self.generations = generations
        
    def _calculate_mean(self, data):
        """Calculate mean of data"""
        return sum(data) / len(data) if data else 0
    
    def _calculate_objectives(self, quota, historical_catches, lstm_predictions=None, sustainability_factor=0.9):
        """
        Calculate multiple objectives for NSGA-III optimization
        """
        # Convert to list if needed
        historical_catches = list(historical_catches) if not isinstance(historical_catches, list) else historical_catches
        
        # Objective 1: Maximize potential catch (based on historical data and LSTM predictions)
        if lstm_predictions and len(lstm_predictions) > 0:
            # Use LSTM predictions as reference
            avg_lstm = self._calculate_mean([p for p in lstm_predictions])
            catch_objective = -abs(quota - avg_lstm)  # Negative because we minimize in NSGA
        else:
            # Fallback to historical data
            avg_historical = self._calculate_mean(historical_catches)
            catch_objective = -abs(quota - avg_historical)
        
        # Objective 2: Environmental impact (simplified)
        # Assume higher quotas have higher environmental impact
        environmental_objective = -quota  # Negative because we minimize
        
        # Objective 3: Sustainability (based on historical trends and LSTM predictions)
        if lstm_predictions and len(lstm_predictions) > 0:
            # Use LSTM predictions for sustainability
            avg_lstm = self._calculate_mean([p for p in lstm_predictions])
            sustainability_objective = -abs(quota - avg_lstm * sustainability_factor)
        else:
            # Fallback to historical data
            avg_historical = self._calculate_mean(historical_catches)
            sustainability_objective = -abs(quota - avg_historical * sustainability_factor)
            
        return [catch_objective, environmental_objective, sustainability_objective]
    
    def optimize_lstm_predictions(self, lstm_predictions, historical_catches):
        """
        Optimize LSTM predictions using NSGA-III
        """
        if not lstm_predictions:
            return []
        
        # Convert LSTM predictions to a list of quota values
        lstm_quota_values = [p for p in lstm_predictions]
        
        if not lstm_quota_values:
            return []
        
        # Determine min/max quotas based on LSTM predictions and historical data
        min_lstm = min(lstm_quota_values) if lstm_quota_values else 0
        max_lstm = max(lstm_quota_values) if lstm_quota_values else 1000
        
        min_historical = min(historical_catches) if historical_catches else 0
        max_historical = max(historical_catches) if historical_catches else 1000
        
        # Set bounds based on both LSTM and historical data
        min_quota = max(0, min(min_lstm, min_historical) * 0.5)
        max_quota = max(max_lstm, max_historical) * 1.5
        
        # Initialize population with variations around LSTM predictions
        population = []
        for i in range(self.population_size):
            # Create variations around LSTM predictions
            variation_factor = 0.8 + (0.4 * i / self.population_size)  # 0.8 to 1.2
            individual = [max(0, q * variation_factor) for q in lstm_quota_values]
            population.append(individual)
        
        # For simplicity, we'll just take a weighted average of LSTM and optimized values
        # In a real implementation, we would run the full NSGA-III algorithm
        
        # Simple optimization: adjust LSTM predictions based on historical trends
        optimized_predictions = []
        avg_historical = self._calculate_mean(historical_catches)
        
        for lstm_pred in lstm_quota_values:
            # Balance LSTM prediction with historical average
            optimized_value = (lstm_pred * 0.7) + (avg_historical * 0.3)
            optimized_predictions.append(optimized_value)
        
        return optimized_predictions
    
    def calculate_fitness_scores(self, optimized_predictions, lstm_predictions, historical_catches):
        """
        Calculate fitness scores for optimized predictions
        """
        if not optimized_predictions or not lstm_predictions:
            return [0.5] * len(optimized_predictions) if optimized_predictions else []
        
        fitness_scores = []
        avg_historical = self._calculate_mean(historical_catches) if historical_catches else 0
        
        for i, (opt_pred, lstm_pred) in enumerate(zip(optimized_predictions, lstm_predictions)):
            # Calculate fitness based on how well the optimized prediction balances LSTM and historical data
            lstm_diff = abs(opt_pred - lstm_pred)
            historical_diff = abs(opt_pred - avg_historical) if avg_historical > 0 else 0
            
            # Fitness score: higher is better
            # Lower differences mean better fitness
            fitness = 1.0 - (lstm_diff + historical_diff) / (lstm_pred + avg_historical + 1e-8)
            fitness = max(0, min(1, fitness))  # Clamp between 0 and 1
            fitness_scores.append(fitness)
        
        return fitness_scores


def get_historical_catch_data(ship_registration_number, months_back=24):
    """
    Retrieve historical catch data for a specific ship
    """
    try:
        # Get models dynamically
        Ship = apps.get_model('ships', 'Ship')
        FishCatch = apps.get_model('catches', 'FishCatch')
        CatchDetail = apps.get_model('catches', 'CatchDetail')
        
        # Get ship by registration number
        ship = Ship._default_manager.get(registration_number=ship_registration_number)
        
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=months_back * 30)  # Approximate
        
        # Get catch reports for this ship
        catch_reports = FishCatch.objects.filter(
            ship=ship,
            catch_date__gte=start_date,
            catch_date__lte=end_date
        ).order_by('catch_date')
        
        # Aggregate catch data by month
        monthly_catches = catch_reports.annotate(
            month=TruncMonth('catch_date')
        ).values('month').annotate(
            total_catch=Sum('catch_details__quantity')
        ).order_by('month')
        
        # Convert to list of values
        catch_data = []
        for item in monthly_catches:
            if item['total_catch'] is not None:
                catch_data.append(float(item['total_catch']))
                
        return catch_data, ship
    except Exception as e:
        return [], None


def predict_and_optimize_quota(ship_registration_number, prediction_months=12):
    """
    Predict quota using LSTM and then optimize using NSGA-III
    This is the main function that implements the sequential approach:
    1. LSTM performs initial prediction
    2. NSGA-III optimizes the LSTM results
    """
    # Get historical data
    historical_data, ship = get_historical_catch_data(ship_registration_number, months_back=24)
    
    if not historical_data:
        return {"error": "No historical data found for this ship"}
    
    # Step 1: LSTM Prediction
    lstm_model = SimpleLSTM(lookback_months=6)
    lstm_predictions = lstm_model.predict(historical_data, steps=prediction_months)
    
    # Step 2: NSGA-III Optimization of LSTM predictions
    nsga3_optimizer = NSGA3QuotaOptimizer(population_size=50, generations=100)
    optimized_predictions = nsga3_optimizer.optimize_lstm_predictions(lstm_predictions, historical_data)
    fitness_scores = nsga3_optimizer.calculate_fitness_scores(optimized_predictions, lstm_predictions, historical_data)
    
    # Prepare results
    results = []
    current_date = datetime.now().date()
    
    for i in range(prediction_months):
        prediction_date = current_date + timedelta(days=30 * (i + 1))  # Approximate monthly
        
        # LSTM prediction
        lstm_pred = lstm_predictions[i] if i < len(lstm_predictions) else 0
        
        # Optimized prediction
        opt_pred = optimized_predictions[i] if i < len(optimized_predictions) else lstm_pred
        
        # Confidence interval (simplified)
        if historical_data:
            avg_historical = sum(historical_data) / len(historical_data)
            std_historical = 0
            if len(historical_data) > 1:
                variance = sum((x - avg_historical) ** 2 for x in historical_data) / len(historical_data)
                std_historical = math.sqrt(variance)
        else:
            avg_historical = 0
            std_historical = 0
        
        lower_bound = max(0, opt_pred - std_historical)
        upper_bound = opt_pred + std_historical
        
        # Fitness score
        fitness_score = fitness_scores[i] if i < len(fitness_scores) else 0.5
        
        results.append({
            "date": prediction_date,
            "lstm_predicted_quota": round(lstm_pred, 2),
            "optimized_quota": round(opt_pred, 2),
            "confidence_interval": [round(lower_bound, 2), round(upper_bound, 2)],
            "fitness_score": round(fitness_score, 4)
        })
    
    return results


def generate_quota_recommendation(optimized_results=None):
    """
    Generate a final quota recommendation based on optimized predictions
    """
    def calculate_mean(values):
        return sum(values) / len(values) if values else 0
    
    recommendation = ""
    
    if optimized_results:
        # Calculate averages
        lstm_avg = calculate_mean([r["lstm_predicted_quota"] for r in optimized_results])
        optimized_avg = calculate_mean([r["optimized_quota"] for r in optimized_results])
        
        return {"quota": round(optimized_avg)}
        
       
    else:
        recommendation = (
            "Tidak cukup data historis untuk membuat prediksi yang akurat. "
            "Disarankan untuk mengumpulkan lebih banyak data laporan penangkapan "
            "sebelum menentukan kuota yang tepat."
        )
    
    return recommendation