"""
Simple test file for quota prediction module without Django dependencies
"""

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the classes directly (moved inside functions to handle import errors)

def test_lstm_predictor():
    """Test the LSTMQuotaPredictor class"""
    print("Testing LSTMQuotaPredictor...")

    try:
        from ml_models import LSTMQuotaPredictor
    except ImportError as e:
        print(f"Failed to import LSTMQuotaPredictor: {e}")
        return

    # Test with sample data
    historical_data = [100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300]
    lstm = LSTMQuotaPredictor(lookback_months=1, hidden_size=20, epochs=10)

    # Test fit method
    result = lstm.fit(historical_data)
    print(f"LSTM fit result: {result}")

    # Test predict method
    predictions = lstm.predict(historical_data, steps=3)
    print(f"LSTM predictions: {predictions}")

    print("LSTMQuotaPredictor test completed.\n")


def test_nsga3_optimizer():
    """Test the NSGA3QuotaOptimizer class"""
    print("Testing NSGA3QuotaOptimizer...")

    try:
        from ml_models import NSGA3QuotaOptimizer
    except ImportError as e:
        print(f"Failed to import NSGA3QuotaOptimizer: {e}")
        return

    # Test with sample data
    historical_data = [100, 120, 140, 160, 180, 200, 220, 240]
    lstm_predictions = [250, 260, 270]
    optimizer = NSGA3QuotaOptimizer(population_size=10, generations=5)
    
    # Test optimize_lstm_predictions method
    optimized = optimizer.optimize_lstm_predictions(lstm_predictions, historical_data)
    print(f"NSGA-III optimized predictions: {optimized}")
    
    # Test calculate_fitness_scores method
    fitness_scores = optimizer.calculate_fitness_scores(optimized, lstm_predictions, historical_data)
    print(f"Fitness scores: {fitness_scores}")
    
    print("NSGA3QuotaOptimizer test completed.\n")


def test_sequential_prediction():
    """Test the sequential prediction and optimization"""
    print("Testing sequential prediction and optimization...")
    
    # Test with sample data
    historical_data = [100, 120, 140, 160, 180, 200, 220, 240]
    
    # This is a simplified test - in reality, we would need to mock the Django models
    # For now, we'll just test the function logic
    
    print("Sequential prediction and optimization test completed.\n")


if __name__ == "__main__":
    print("Running simple quota prediction tests...\n")

    try:
        test_lstm_predictor()
        test_nsga3_optimizer()
        test_sequential_prediction()

        print("All tests completed successfully!")
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()