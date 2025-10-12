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

    def predict(self, sequence):
        """Make prediction for a single sequence"""
        h = np.zeros((self.hidden_size, 1))
        c = np.zeros((self.hidden_size, 1))

        # Process the entire sequence
        for t in range(len(sequence)):
            x_t = np.array([[sequence[t]]])  # Shape: (1, 1)
            y_pred, h, c = self.forward(x_t, h, c)

        return [y_pred.flatten()[0]]

class LSTMQuotaPredictor:
    """
    LSTM-based quota prediction model.
    Uses proper LSTM network for time series forecasting.
    Now supports dynamic epoch selection based on user level.
    """

    def __init__(self, lookback_months=6, hidden_size=50, max_epochs=20):
        self.lookback_months = lookback_months
        self.hidden_size = hidden_size
        self.max_epochs = max_epochs
        self.scaler = MinMaxScaler(feature_range=(-1, 1))
        self.model = None
        self.training_metrics = {}

    def level_to_epochs(self, level):
        """Convert user level (1-5) to actual number of epochs"""
        level_mapping = {
            1: 4,   # 20% of max
            2: 8,   # 40% of max
            3: 12,  # 60% of max
            4: 16,  # 80% of max
            5: 20   # 100% of max
        }
        return level_mapping.get(level, 20)  # Default to max if invalid level

    def create_train_val_split(self, X, y, validation_split=0.2):
        """Split data into training and validation sets"""
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        return X_train, X_val, y_train, y_val

    def create_sequences(self, data):
        """Create input sequences for LSTM training"""
        X, y = [], []
        for i in range(len(data) - self.lookback_months):
            X.append(data[i:i + self.lookback_months])
            y.append(data[i + self.lookback_months])
        return np.array(X), np.array(y)

    def fit(self, historical_data, epoch_level=5, early_stopping=True, patience=3, validation_split=0.2):
        """Train the LSTM model with dynamic epochs and early stopping"""
        import time

        if len(historical_data) < self.lookback_months + 1:
            # Not enough data, fallback to simple methods
            avg_value = np.mean(historical_data) if historical_data else 0
            return {"method": "average", "value": avg_value}

        # Convert level to epochs
        epochs = self.level_to_epochs(epoch_level)

        # Scale the data
        scaled_data = self.scaler.fit_transform(np.array(historical_data).reshape(-1, 1)).flatten()

        # Create sequences
        X, y = self.create_sequences(scaled_data)

        if len(X) == 0:
            return {"method": "insufficient_data", "value": historical_data[-1] if historical_data else 0}

        # Split into train/validation
        X_train, X_val, y_train, y_val = self.create_train_val_split(X, y, validation_split)

        # Initialize LSTM
        self.model = LSTMNetwork(input_size=1, hidden_size=self.hidden_size, output_size=1)

        # Training with early stopping and metrics tracking
        train_losses = []
        val_losses = []
        epoch_durations = []
        best_val_loss = float('inf')
        patience_counter = 0
        epochs_used = 0

        start_time = time.time()

        for epoch in range(epochs):
            epoch_start = time.time()

            # Training pass
            train_loss = self._train_epoch(X_train, y_train)
            train_losses.append(train_loss)

            # Validation pass
            val_loss = self._validate_epoch(X_val, y_val)
            val_losses.append(val_loss)

            epoch_duration = time.time() - epoch_start
            epoch_durations.append(epoch_duration)

            epochs_used = epoch + 1

            # Early stopping check
            if early_stopping:
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                else:
                    patience_counter += 1

                if patience_counter >= patience:
                    break

        total_training_time = time.time() - start_time

        # Calculate confidence score
        max_val_loss = max(val_losses) if val_losses else 1.0
        final_val_loss = val_losses[-1] if val_losses else 1.0
        confidence_score = 1.0 - (final_val_loss / max_val_loss) if max_val_loss > 0 else 0.5

        # Store training metrics
        self.training_metrics = {
            "epoch_level": epoch_level,
            "epochs_used": epochs_used,
            "max_epochs": epochs,
            "train_losses": train_losses,
            "val_losses": val_losses,
            "epoch_durations": epoch_durations,
            "total_training_time": total_training_time,
            "confidence_score": confidence_score,
            "early_stopped": patience_counter >= patience if early_stopping else False
        }

        return {"method": "lstm", "trained": True, "metrics": self.training_metrics}

    def _train_epoch(self, X, y):
        """Train for one epoch and return average loss"""
        total_loss = 0

        for seq_idx in range(len(X)):
            sequence = X[seq_idx]  # This is a sequence of lookback_months values
            target = y[seq_idx]

            # Initialize hidden and cell states for this sequence
            h = np.zeros((self.model.hidden_size, 1))
            c = np.zeros((self.model.hidden_size, 1))

            # Process the entire sequence
            for t in range(len(sequence)):
                x_t = np.array([[sequence[t]]])  # Shape: (1, 1)
                y_pred, h, c = self.model.forward(x_t, h, c)

            # The final prediction should match the target
            y_t = np.array([[target]])
            loss = 0.5 * np.sum((y_pred - y_t) ** 2)
            total_loss += loss

            # Backward pass (simplified - only update output layer)
            dy = y_pred - y_t
            dWy = np.dot(dy, h.T)
            dby = dy

            # Update weights
            self.model.Wy -= self.model.learning_rate * dWy
            self.model.by -= self.model.learning_rate * dby

        return total_loss / len(X)

    def _validate_epoch(self, X, y):
        """Validate for one epoch and return average loss"""
        total_loss = 0

        for seq_idx in range(len(X)):
            sequence = X[seq_idx]
            target = y[seq_idx]

            # Initialize hidden and cell states for this sequence
            h = np.zeros((self.model.hidden_size, 1))
            c = np.zeros((self.model.hidden_size, 1))

            # Process the entire sequence
            for t in range(len(sequence)):
                x_t = np.array([[sequence[t]]])
                y_pred, h, c = self.model.forward(x_t, h, c)

            # Compute loss for this sequence
            y_t = np.array([[target]])
            loss = 0.5 * np.sum((y_pred - y_t) ** 2)
            total_loss += loss

        return total_loss / len(X) if len(X) > 0 else 0

    def predict(self, historical_data, steps=1):
        """Predict future values using trained LSTM"""
        if not self.model or len(historical_data) < self.lookback_months:
            # Fallback to simple prediction
            if historical_data:
                last_value = historical_data[-1]
                # Check if we have enough data points and variance for linear regression
                if len(historical_data) >= 2:
                    try:
                        # Check if data has variance (not all same values)
                        if np.var(historical_data) > 1e-10:  # Small threshold for numerical stability
                            trend = np.polyfit(range(len(historical_data)), historical_data, 1)[0]
                            return [max(0, last_value + trend * i) for i in range(1, steps + 1)]
                        else:
                            # All values are the same, return constant prediction
                            return [max(0, last_value)] * steps
                    except np.linalg.LinAlgError:
                        # SVD did not converge, fallback to constant prediction
                        return [max(0, last_value)] * steps
                else:
                    # Not enough data points for regression, return constant
                    return [max(0, last_value)] * steps
            else:
                return [0] * steps

        # Scale historical data
        scaled_history = self.scaler.transform(np.array(historical_data).reshape(-1, 1)).flatten()

        # Generate predictions iteratively
        predictions = []
        current_sequence = scaled_history[-self.lookback_months:]

        for _ in range(steps):
            # Predict next value
            pred_scaled = self.model.predict(current_sequence)[0]
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


def predict_and_optimize_quota(ship_registration_number, prediction_months=12, epoch_level=5):
    """
    Predict quota using LSTM and then optimize using NSGA-III
    This is the main function that implements the sequential approach:
    1. LSTM performs initial prediction with dynamic epochs based on user level
    2. NSGA-III optimizes the LSTM results
    """
    # Get historical data
    historical_data, ship = get_historical_catch_data(ship_registration_number, months_back=36)  # Use 36 months as per spec

    if not historical_data:
        return {"error": "No historical data found for this ship"}

    # Step 1: LSTM Prediction with dynamic epochs
    lstm_model = LSTMQuotaPredictor(lookback_months=6, hidden_size=32)  # Use smaller hidden size as per spec
    fit_result = lstm_model.fit(historical_data, epoch_level=epoch_level)

    if fit_result["method"] != "lstm":
        # Fallback for insufficient data
        return {"error": "Insufficient historical data for LSTM training"}

    lstm_predictions = lstm_model.predict(historical_data, steps=prediction_months)

    # Get training metrics
    training_metrics = fit_result.get("metrics", {})

    # Step 2: NSGA-III Optimization of LSTM predictions
    nsga3_optimizer = NSGA3QuotaOptimizer(population_size=100, generations=50)
    optimized_predictions = nsga3_optimizer.optimize_lstm_predictions(lstm_predictions, historical_data)
    fitness_scores = nsga3_optimizer.calculate_fitness_scores(optimized_predictions, lstm_predictions, historical_data)
    
    # Prepare results in new format
    lstm_predictions_list = []
    nsga_optimized_list = []
    current_date = datetime.now().date()

    for i in range(prediction_months):
        prediction_date = current_date + timedelta(days=30 * (i + 1))  # Approximate monthly

        # LSTM prediction
        lstm_pred = lstm_predictions[i] if i < len(lstm_predictions) else 0

        # Optimized prediction
        opt_pred = optimized_predictions[i] if i < len(optimized_predictions) else lstm_pred

        lstm_predictions_list.append({
            "date": prediction_date.isoformat(),
            "predicted_value": round(lstm_pred, 2)
        })

        nsga_optimized_list.append({
            "date": prediction_date.isoformat(),
            "optimized_value": round(opt_pred, 2)
        })

    # Calculate recommended quota (average of optimized predictions)
    recommended_quota = round(sum([p["optimized_value"] for p in nsga_optimized_list]) / len(nsga_optimized_list), 2) if nsga_optimized_list else 0

    # Return data for NSGA-III (as per spec)
    lstm_data_for_nsga = {
        "lstm_predictions": lstm_predictions,
        "confidence_score": training_metrics.get("confidence_score", 0.5),
        "epoch_used": training_metrics.get("epochs_used", 0),
        "historical_data": historical_data
    }

    # Final result structure as per spec
    result = {
        "ship_registration": ship_registration_number,
        "epoch_level": epoch_level,
        "epoch_used": training_metrics.get("epochs_used", 0),
        "confidence": round(training_metrics.get("confidence_score", 0.5), 4),
        "lstm_predictions": lstm_predictions_list,
        "nsga_optimized": nsga_optimized_list,
        "recommended_quota": recommended_quota,
        "training_time": f"{round(training_metrics.get('total_training_time', 0), 2)}s",
        "training_metrics": training_metrics  # Include full metrics for debugging/transparency
    }

    return result


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