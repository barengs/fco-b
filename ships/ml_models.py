"""
Machine Learning Models for Quota Prediction
This module implements LSTM and NSGA-III algorithms for fishing quota prediction.
LSTM performs initial prediction, then NSGA-III optimizes the LSTM results.
"""

import math
import numpy as np
from datetime import datetime, timedelta
from django.apps import apps
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth
from sklearn.preprocessing import MinMaxScaler
from platypus import NSGAIII, Problem, Real
import warnings
warnings.filterwarnings('ignore')

class LSTMNetwork:
    """
    Proper LSTM implementation for time series prediction using numpy.
    This implements a basic LSTM network from scratch.
    """

    def __init__(self, input_size=1, hidden_size=50, output_size=1, learning_rate=0.001):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.learning_rate = learning_rate

        # Initialize weights and biases
        self.Wf = np.random.randn(hidden_size, input_size + hidden_size) * 0.1
        self.bf = np.zeros((hidden_size, 1))

        self.Wi = np.random.randn(hidden_size, input_size + hidden_size) * 0.1
        self.bi = np.zeros((hidden_size, 1))

        self.Wc = np.random.randn(hidden_size, input_size + hidden_size) * 0.1
        self.bc = np.zeros((hidden_size, 1))

        self.Wo = np.random.randn(hidden_size, input_size + hidden_size) * 0.1
        self.bo = np.zeros((hidden_size, 1))

        self.Wy = np.random.randn(output_size, hidden_size) * 0.1
        self.by = np.zeros((output_size, 1))

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def tanh(self, x):
        return np.tanh(x)

    def forward(self, x, h_prev, c_prev):
        """Forward pass for one time step"""
        # Concatenate input and previous hidden state
        concat = np.vstack((h_prev, x))

        # Forget gate
        ft = self.sigmoid(np.dot(self.Wf, concat) + self.bf)

        # Input gate
        it = self.sigmoid(np.dot(self.Wi, concat) + self.bi)

        # Candidate values
        c_tilde = self.tanh(np.dot(self.Wc, concat) + self.bc)

        # Cell state
        c = ft * c_prev + it * c_tilde

        # Output gate
        ot = self.sigmoid(np.dot(self.Wo, concat) + self.bo)

        # Hidden state
        h = ot * self.tanh(c)

        # Output
        y = np.dot(self.Wy, h) + self.by

        return y, h, c

    def train(self, X, y, epochs=100):
        """Train the LSTM network"""
        for epoch in range(epochs):
            loss = 0
            h = np.zeros((self.hidden_size, 1))
            c = np.zeros((self.hidden_size, 1))

            for t in range(len(X)):
                x_t = X[t].reshape(-1, 1)
                y_t = y[t].reshape(-1, 1)

                # Forward pass
                y_pred, h, c = self.forward(x_t, h, c)

                # Compute loss (MSE)
                loss += 0.5 * np.sum((y_pred - y_t) ** 2)

                # Backward pass (simplified - only output layer)
                dy = y_pred - y_t
                dWy = np.dot(dy, h.T)
                dby = dy

                # Update weights (simplified gradient descent)
                self.Wy -= self.learning_rate * dWy
                self.by -= self.learning_rate * dby

            if epoch % 20 == 0:
                print(f"Epoch {epoch}, Loss: {loss}")

    def predict(self, X):
        """Make predictions"""
        h = np.zeros((self.hidden_size, 1))
        c = np.zeros((self.hidden_size, 1))
        predictions = []

        for t in range(len(X)):
            x_t = X[t].reshape(-1, 1)
            y_pred, h, c = self.forward(x_t, h, c)
            predictions.append(y_pred.flatten()[0])

        return predictions

class LSTMQuotaPredictor:
    """
    LSTM-based quota prediction model.
    Uses proper LSTM network for time series forecasting.
    """

    def __init__(self, lookback_months=6, hidden_size=50, epochs=100):
        self.lookback_months = lookback_months
        self.hidden_size = hidden_size
        self.epochs = epochs
        self.scaler = MinMaxScaler(feature_range=(-1, 1))
        self.model = None

    def create_sequences(self, data):
        """Create input sequences for LSTM training"""
        X, y = [], []
        for i in range(len(data) - self.lookback_months):
            X.append(data[i:i + self.lookback_months])
            y.append(data[i + self.lookback_months])
        return np.array(X), np.array(y)

    def fit(self, historical_data):
        """Train the LSTM model"""
        if len(historical_data) < self.lookback_months + 1:
            # Not enough data, fallback to simple methods
            avg_value = np.mean(historical_data) if historical_data else 0
            return {"method": "average", "value": avg_value}

        # Scale the data
        scaled_data = self.scaler.fit_transform(np.array(historical_data).reshape(-1, 1)).flatten()

        # Create sequences
        X, y = self.create_sequences(scaled_data)

        if len(X) == 0:
            return {"method": "insufficient_data", "value": historical_data[-1] if historical_data else 0}

        # Initialize and train LSTM
        self.model = LSTMNetwork(input_size=1, hidden_size=self.hidden_size, output_size=1)
        self.model.train(X, y, epochs=self.epochs)

        return {"method": "lstm", "trained": True}

    def predict(self, historical_data, steps=1):
        """Predict future values using trained LSTM"""
        if not self.model or len(historical_data) < self.lookback_months:
            # Fallback to simple prediction
            if historical_data:
                trend = np.polyfit(range(len(historical_data)), historical_data, 1)[0]
                last_value = historical_data[-1]
                return [max(0, last_value + trend * i) for i in range(1, steps + 1)]
            else:
                return [0] * steps

        # Scale historical data
        scaled_history = self.scaler.transform(np.array(historical_data).reshape(-1, 1)).flatten()

        # Generate predictions iteratively
        predictions = []
        current_sequence = scaled_history[-self.lookback_months:]

        for _ in range(steps):
            # Predict next value
            pred_scaled = self.model.predict(current_sequence.reshape(1, -1))[0]
            predictions.append(pred_scaled)

            # Update sequence for next prediction
            current_sequence = np.roll(current_sequence, -1)
            current_sequence[-1] = pred_scaled

        # Inverse transform predictions
        predictions_unscaled = self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()

        return [max(0, pred) for pred in predictions_unscaled]


class NSGA3QuotaOptimizer:
    """
    Proper NSGA-III implementation for quota optimization using Platypus.
    This optimizer takes LSTM predictions and optimizes them based on multiple objectives.
    """

    def __init__(self, population_size=100, generations=100):
        self.population_size = population_size
        self.generations = generations

    def optimize_lstm_predictions(self, lstm_predictions, historical_catches, environmental_weights=None):
        """
        Optimize LSTM predictions using NSGA-III with multiple objectives:
        1. Maximize total catch potential
        2. Minimize environmental impact
        3. Maximize fairness (equal distribution)
        4. Minimize overfishing risk
        """
        if not lstm_predictions or len(lstm_predictions) == 0:
            return []

        num_ships = len(lstm_predictions)
        if num_ships == 0:
            return []

        # Convert to numpy arrays
        lstm_preds = np.array(lstm_predictions)
        hist_catches = np.array(historical_catches) if historical_catches else np.zeros(num_ships)

        # Set environmental weights (higher values = more environmental concern)
        if environmental_weights is None:
            environmental_weights = np.ones(num_ships) * 0.1

        def objective_function(vars):
            """
            Multi-objective function for NSGA-III:
            vars: multipliers for each ship's quota (0.1 to 2.0)
            """
            multipliers = np.array(vars)

            # Calculate actual quotas
            quotas = multipliers * lstm_preds

            # Objective 1: Maximize total catch (minimize negative total)
            total_catch = np.sum(quotas)
            obj1 = -total_catch

            # Objective 2: Minimize environmental impact
            # Higher quotas and environmental weights increase impact
            env_impact = np.sum(quotas * environmental_weights)
            obj2 = env_impact

            # Objective 3: Maximize fairness (minimize standard deviation of quotas)
            if len(quotas) > 1:
                fairness = np.std(quotas / (lstm_preds + 1e-8))  # Normalized by predictions
            else:
                fairness = 0
            obj3 = fairness

            # Objective 4: Minimize overfishing risk
            # Risk increases when quota exceeds historical average significantly
            hist_avg = np.mean(hist_catches) if len(hist_catches) > 0 else np.mean(lstm_preds)
            overfish_penalty = 0
            for i, quota in enumerate(quotas):
                if quota > hist_avg * 1.5:  # Over 150% of historical average
                    overfish_penalty += (quota - hist_avg * 1.5) * 10
            obj4 = overfish_penalty

            return [obj1, obj2, obj3, obj4]

        # Setup NSGA-III problem
        problem = Problem(num_ships, 4)  # num_vars, num_objectives
        problem.types[:] = Real(0.1, 2.0)  # Multipliers between 0.1 and 2.0
        problem.function = objective_function

        # Run NSGA-III
        algorithm = NSGAIII(problem, divisions_outer=12, divisions_inner=2)
        algorithm.run(self.population_size * self.generations)

        if not algorithm.result:
            # Fallback: return slightly adjusted LSTM predictions
            return [pred * 0.9 for pred in lstm_predictions]

        # Select best solution based on compromise programming
        # Find solution that balances all objectives
        best_solution = self._select_best_solution(algorithm.result, lstm_preds, hist_catches)

        # Apply the multipliers to get optimized quotas
        multipliers = np.array(best_solution.variables)
        optimized_quotas = multipliers * lstm_preds

        return optimized_quotas.tolist()

    def _select_best_solution(self, solutions, lstm_predictions, historical_catches):
        """
        Select the best solution from Pareto front based on balanced criteria
        """
        if not solutions:
            return None

        best_score = float('inf')
        best_solution = solutions[0]

        hist_avg = np.mean(historical_catches) if historical_catches.size > 0 else np.mean(lstm_predictions)

        for solution in solutions:
            multipliers = np.array(solution.variables)
            quotas = multipliers * lstm_predictions

            # Calculate composite score
            total_catch = np.sum(quotas)
            env_impact = np.sum(quotas * 0.1)  # Simplified environmental impact
            fairness = np.std(quotas) if len(quotas) > 1 else 0

            # Overfishing penalty
            overfish_penalty = sum(max(0, q - hist_avg * 1.3) for q in quotas)

            # Composite score (lower is better)
            score = (env_impact * 0.3 + fairness * 0.3 + overfish_penalty * 0.4 - total_catch * 0.1)

            if score < best_score:
                best_score = score
                best_solution = solution

        return best_solution

    def calculate_fitness_scores(self, optimized_predictions, lstm_predictions, historical_catches):
        """
        Calculate fitness scores for optimized predictions based on multiple criteria
        """
        if not optimized_predictions or not lstm_predictions:
            return [0.5] * len(optimized_predictions) if optimized_predictions else []

        fitness_scores = []
        hist_avg = np.mean(historical_catches) if historical_catches else 0

        for opt_pred, lstm_pred in zip(optimized_predictions, lstm_predictions):
            # Multi-criteria fitness score
            # 1. How close to LSTM prediction (stability)
            stability_score = 1.0 - min(1.0, abs(opt_pred - lstm_pred) / (lstm_pred + 1e-8))

            # 2. Sustainability (not too far from historical average)
            if hist_avg > 0:
                sustainability_score = 1.0 - min(1.0, abs(opt_pred - hist_avg) / hist_avg)
            else:
                sustainability_score = 0.8  # Default good score if no historical data

            # 3. Environmental consideration (prefer lower quotas)
            env_score = min(1.0, 1000 / (opt_pred + 100))  # Higher for lower quotas

            # Combined fitness (weighted average)
            fitness = (stability_score * 0.4 + sustainability_score * 0.4 + env_score * 0.2)
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
    lstm_model = LSTMQuotaPredictor(lookback_months=6, hidden_size=50, epochs=50)
    lstm_model.fit(historical_data)
    lstm_predictions = lstm_model.predict(historical_data, steps=prediction_months)

    # Step 2: NSGA-III Optimization of LSTM predictions
    nsga3_optimizer = NSGA3QuotaOptimizer(population_size=100, generations=50)
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