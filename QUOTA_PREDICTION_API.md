# Quota Prediction API Documentation

## Overview

The Quota Prediction API provides intelligent fishing quota recommendations for ships based on their historical catch reports. It uses a sequential approach with two advanced algorithms:

1. **LSTM (Long Short-Term Memory)**: A neural network architecture that analyzes historical catch trends to predict initial quotas
2. **NSGA-III (Non-dominated Sorting Genetic Algorithm III)**: A multi-objective optimization algorithm that optimizes the LSTM predictions based on sustainability and environmental factors

## Sequential Process

The quota prediction works in a sequential manner:

1. **LSTM Prediction**: LSTM analyzes historical data and generates initial quota predictions
2. **NSGA-III Optimization**: NSGA-III takes the LSTM predictions and optimizes them based on multiple objectives:
   - Maximize potential catch (productivity)
   - Minimize environmental impact
   - Ensure long-term sustainability

## Endpoint

**POST** `/api/ships/predict-quota/`

## Authentication

This endpoint requires authentication. Include your token in the Authorization header:

```
Authorization: Token <your_token>
```

## Request Body

```json
{
  "ship_registration_number": "string",
  "prediction_months": "integer (optional, default: 12)",
  "algorithm": "string (optional, choices: 'lstm', 'nsga3', 'both', default: 'both')"
}
```

### Parameters

| Parameter                | Type    | Required | Description                                                    |
| ------------------------ | ------- | -------- | -------------------------------------------------------------- |
| ship_registration_number | string  | Yes      | The registration number of the ship to predict quotas for      |
| prediction_months        | integer | No       | Number of months to predict (default: 12)                      |
| algorithm                | string  | No       | Algorithm to use: 'lstm', 'nsga3', or 'both' (default: 'both') |

## Response

```json
{
  "ship_registration_number": "string",
  "ship_name": "string",
  "prediction_period": "string",
  "lstm_predictions": [
    {
      "date": "YYYY-MM-DD",
      "predicted_quota": "float",
      "confidence_interval": ["float", "float"]
    }
  ],
  "nsga3_predictions": [
    {
      "date": "YYYY-MM-DD",
      "predicted_quota": "float",
      "fitness_score": "float"
    }
  ],
  "recommendation": "string"
}
```

## Example Request

```bash
curl -X POST \
  http://localhost:8000/api/ships/predict-quota/ \
  -H 'Authorization: Token your_auth_token' \
  -H 'Content-Type: application/json' \
  -d '{
    "ship_registration_number": "KM-2023-001",
    "prediction_months": 6,
    "algorithm": "both"
  }'
```

## Example Response

```json
{
  "ship_registration_number": "KM-2023-001",
  "ship_name": "Nusantara Jaya",
  "prediction_period": "6 bulan ke depan",
  "lstm_predictions": [
    {
      "date": "2023-06-01",
      "predicted_quota": 1250.5,
      "confidence_interval": [1100.0, 1400.0]
    },
    {
      "date": "2023-07-01",
      "predicted_quota": 1275.0,
      "confidence_interval": [1120.0, 1430.0]
    }
  ],
  "nsga3_predictions": [
    {
      "date": "2023-06-01",
      "predicted_quota": 1180.0,
      "fitness_score": 0.85
    },
    {
      "date": "2023-07-01",
      "predicted_quota": 1195.0,
      "fitness_score": 0.83
    }
  ],
  "recommendation": "Berdasarkan analisis gabungan LSTM dan NSGA-III, kuota bulanan yang direkomendasikan adalah 1187.5 kg. Prediksi awal LSTM adalah 1262.75 kg, yang kemudian dioptimasi oleh algoritma NSGA-III menjadi 1187.5 kg berdasarkan faktor keberlanjutan, dampak lingkungan, dan tren historis."
}
```

## Error Responses

### 400 Bad Request

```json
{
  "error": "Invalid input data",
  "details": {
    "ship_registration_number": ["This field is required."]
  }
}
```

### 404 Not Found

```json
{
  "error": "Kapal dengan nomor registrasi KM-2023-001 tidak ditemukan"
}
```

## Algorithm Details

### LSTM (Long Short-Term Memory)

LSTM is a type of recurrent neural network capable of learning order dependence in sequence prediction problems. For quota prediction:

1. **Data Preparation**: Historical monthly catch data is normalized and prepared as sequences
2. **Training**: The model learns patterns and trends from historical data
3. **Prediction**: Future quotas are predicted based on learned patterns
4. **Confidence Intervals**: Statistical measures provide uncertainty bounds

### NSGA-III (Non-dominated Sorting Genetic Algorithm III)

NSGA-III is a state-of-the-art multi-objective evolutionary algorithm that optimizes the LSTM predictions by balancing multiple conflicting objectives:

1. **Objectives**:

   - Maximize potential catch (productivity) based on LSTM predictions
   - Minimize environmental impact
   - Ensure long-term sustainability based on historical trends

2. **Process**:

   - Takes LSTM predictions as input
   - Creates population variations around LSTM predictions
   - Evaluates multiple objectives for each individual
   - Non-dominated sorting to identify optimized solutions
   - Selection, crossover, and mutation operations
   - Convergence to optimally balanced quota values

3. **Output**:
   - Optimized quota recommendations that balance LSTM predictions with sustainability factors
   - Fitness scores indicating solution quality

## Requirements

The quota prediction module requires the following Python packages:

- numpy
- pandas

These are included in the requirements.txt file.

## Implementation Details

The implementation follows these principles:

1. **Sequential Design**: LSTM predictions are optimized by NSGA-III in a single process
2. **Modular Architecture**: Separate modules for serializers, ML models, and views
3. **Django Integration**: Uses Django REST Framework for API endpoints
4. **Type Safety**: Proper type annotations and error handling
5. **Documentation**: OpenAPI/Swagger documentation with drf-spectacular
6. **Scalability**: Efficient database queries and caching strategies

## Usage Recommendations

1. **Data Quality**: Ensure comprehensive historical catch data for accurate predictions
2. **Regular Updates**: Update predictions periodically as new catch data becomes available
3. **Parameter Tuning**: Adjust prediction_months based on planning horizons
4. **Validation**: Validate predictions against actual catches to improve model accuracy

## Limitations

1. **Data Dependency**: Accuracy depends on quality and quantity of historical data
2. **Simplified Models**: Current implementation uses simplified versions of complex algorithms
3. **Environmental Factors**: Does not account for external factors like weather, regulations, or market conditions
4. **Seasonal Variations**: Basic seasonal pattern recognition without advanced time-series analysis

For production use, consider implementing more sophisticated versions of these algorithms with proper ML libraries.
