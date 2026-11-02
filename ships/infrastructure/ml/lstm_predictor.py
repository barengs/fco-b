"""
LSTM Quota Predictor
Trains LSTM network with early stopping, sliding window, and autoregressive forecasting.
"""

import time
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from .lstm_network import LSTMNetwork

class LSTMQuotaPredictor:
    """
    LSTM-based quota prediction model.
    Uses proper LSTM network for time series forecasting.
    Supports dynamic epoch selection based on user level.
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
        return level_mapping.get(level, 20)

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
        if len(historical_data) < self.lookback_months + 1:
            avg_value = np.mean(historical_data) if historical_data else 0
            return {"method": "average", "value": avg_value}

        epochs = self.level_to_epochs(epoch_level)
        scaled_data = self.scaler.fit_transform(np.array(historical_data).reshape(-1, 1)).flatten()
        X, y = self.create_sequences(scaled_data)

        if len(X) == 0:
            return {"method": "insufficient_data", "value": historical_data[-1] if historical_data else 0}

        X_train, X_val, y_train, y_val = self.create_train_val_split(X, y, validation_split)
        self.model = LSTMNetwork(input_size=1, hidden_size=self.hidden_size, output_size=1)

        train_losses = []
        val_losses = []
        epoch_durations = []
        best_val_loss = float('inf')
        patience_counter = 0
        epochs_used = 0

        start_time = time.time()

        for epoch in range(epochs):
            epoch_start = time.time()

            train_loss = self._train_epoch(X_train, y_train)
            train_losses.append(train_loss)

            val_loss = self._validate_epoch(X_val, y_val)
            val_losses.append(val_loss)

            epoch_durations.append(time.time() - epoch_start)
            epochs_used = epoch + 1

            if early_stopping:
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                else:
                    patience_counter += 1

                if patience_counter >= patience:
                    break

        total_training_time = time.time() - start_time

        max_val_loss = max(val_losses) if val_losses else 1.0
        final_val_loss = val_losses[-1] if val_losses else 1.0
        confidence_score = 1.0 - (final_val_loss / max_val_loss) if max_val_loss > 0 else 0.5

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
            sequence = X[seq_idx]
            target = y[seq_idx]

            h = np.zeros((self.model.hidden_size, 1))
            c = np.zeros((self.model.hidden_size, 1))

            for t in range(len(sequence)):
                x_t = np.array([[sequence[t]]])
                y_pred, h, c = self.model.forward(x_t, h, c)

            y_t = np.array([[target]])
            loss = 0.5 * np.sum((y_pred - y_t) ** 2)
            total_loss += loss

            dy = y_pred - y_t
            dWy = np.dot(dy, h.T)
            dby = dy

            self.model.Wy -= self.model.learning_rate * dWy
            self.model.by -= self.model.learning_rate * dby

        return total_loss / len(X)

    def _validate_epoch(self, X, y):
        """Validate for one epoch and return average loss"""
        total_loss = 0

        for seq_idx in range(len(X)):
            sequence = X[seq_idx]
            target = y[seq_idx]

            h = np.zeros((self.model.hidden_size, 1))
            c = np.zeros((self.model.hidden_size, 1))

            for t in range(len(sequence)):
                x_t = np.array([[sequence[t]]])
                y_pred, h, c = self.model.forward(x_t, h, c)

            y_t = np.array([[target]])
            loss = 0.5 * np.sum((y_pred - y_t) ** 2)
            total_loss += loss

        return total_loss / len(X) if len(X) > 0 else 0

    def predict(self, historical_data, steps=1):
        """Predict future values using trained LSTM"""
        if not self.model or len(historical_data) < self.lookback_months:
            if historical_data:
                last_value = historical_data[-1]
                if len(historical_data) >= 2:
                    try:
                        if np.var(historical_data) > 1e-10:
                            trend = np.polyfit(range(len(historical_data)), historical_data, 1)[0]
                            return [max(0, last_value + trend * i) for i in range(1, steps + 1)]
                        else:
                            return [max(0, last_value)] * steps
                    except np.linalg.LinAlgError:
                        return [max(0, last_value)] * steps
                else:
                    return [max(0, last_value)] * steps
            else:
                return [0] * steps

        scaled_history = self.scaler.transform(np.array(historical_data).reshape(-1, 1)).flatten()
        predictions = []
        current_sequence = scaled_history[-self.lookback_months:]

        for _ in range(steps):
            pred_scaled = self.model.predict(current_sequence)[0]
            predictions.append(pred_scaled)
            current_sequence = np.roll(current_sequence, -1)
            current_sequence[-1] = pred_scaled

        predictions_unscaled = self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
        return [max(0, pred) for pred in predictions_unscaled]
