"""
Dual-Stage Sequential Quota Optimization Pipeline
1. LSTM network predicts preliminary seasonal catch trend.
2. NSGA-III multi-objective genetic algorithm balances economics, ecology, fairness, and overfishing risks.
"""

from datetime import datetime, timedelta
from .lstm_predictor import LSTMQuotaPredictor
from .nsga3_optimizer import NSGA3QuotaOptimizer
from .data_generator import get_historical_catch_data, synthesize_seasonal_baseline

def predict_and_optimize_quota(ship_registration_number, prediction_months=12, epoch_level=5):
    """
    Predict quota using LSTM and then optimize using NSGA-III.
    """
    historical_data, ship = get_historical_catch_data(ship_registration_number, months_back=36)

    # Cold-start synthesis if history is under 7 months
    if len(historical_data) < 7:
        historical_data = synthesize_seasonal_baseline(ship, historical_data)

    # Step 1: LSTM Prediction with dynamic epochs
    lstm_model = LSTMQuotaPredictor(lookback_months=6, hidden_size=32)
    fit_result = lstm_model.fit(historical_data, epoch_level=epoch_level)

    if fit_result.get("method") != "lstm":
        return {"error": "Data tangkapan belum cukup untuk analisis AI"}

    lstm_predictions = lstm_model.predict(historical_data, steps=prediction_months)
    training_metrics = fit_result.get("metrics", {})

    # Step 2: NSGA-III Multi-objective Optimization
    nsga3_optimizer = NSGA3QuotaOptimizer(population_size=30, generations=20)
    optimized_predictions = nsga3_optimizer.optimize_lstm_predictions(lstm_predictions, historical_data)

    # Structure predictions per month
    lstm_predictions_list = []
    nsga_optimized_list = []
    current_date = datetime.now().date()

    for i in range(prediction_months):
        prediction_date = current_date + timedelta(days=30 * (i + 1))
        lstm_pred = lstm_predictions[i] if i < len(lstm_predictions) else 0
        opt_pred = optimized_predictions[i] if i < len(optimized_predictions) else lstm_pred

        lstm_predictions_list.append({
            "date": prediction_date.isoformat(),
            "predicted_value": round(lstm_pred, 2)
        })

        nsga_optimized_list.append({
            "date": prediction_date.isoformat(),
            "optimized_value": round(opt_pred, 2)
        })

    recommended_quota = (
        round(sum(p["optimized_value"] for p in nsga_optimized_list) / len(nsga_optimized_list), 2)
        if nsga_optimized_list else 0
    )

    return {
        "ship_registration": ship_registration_number,
        "epoch_level": epoch_level,
        "epoch_used": training_metrics.get("epochs_used", 0),
        "confidence": round(training_metrics.get("confidence_score", 0.5), 4),
        "lstm_predictions": lstm_predictions_list,
        "nsga_optimized": nsga_optimized_list,
        "recommended_quota": recommended_quota,
        "training_time": f"{round(training_metrics.get('total_training_time', 0), 2)}s",
        "training_metrics": training_metrics
    }

def generate_quota_recommendation(optimized_results=None):
    """
    Generate a final quota recommendation based on optimized predictions.
    """
    if optimized_results:
        optimized_avg = sum(r["optimized_quota"] for r in optimized_results) / len(optimized_results)
        return {"quota": round(optimized_avg)}

    return {
        "recommendation": (
            "Tidak cukup data historis untuk membuat prediksi yang akurat. "
            "Disarankan untuk mengumpulkan lebih banyak data laporan penangkapan."
        )
    }
