# Quota Prediction Module - Implementation Summary

## Overview

This document summarizes the implementation of the quota prediction module for the FCO Fish Catch Management System. The module provides intelligent fishing quota recommendations using a sequential approach with LSTM and NSGA-III algorithms.

## Sequential Process

The quota prediction works in a sequential manner:

1. **LSTM Prediction**: LSTM analyzes historical data and generates initial quota predictions
2. **NSGA-III Optimization**: NSGA-III takes the LSTM predictions and optimizes them based on multiple objectives:
   - Maximize potential catch (productivity)
   - Minimize environmental impact
   - Ensure long-term sustainability

## Files Created

### 1. `/ships/serializers_quota.py`

- **Purpose**: Serializers for quota prediction input and output
- **Key Components**:
  - `QuotaPredictionInputSerializer`: Validates input parameters
  - `LSTMQuotaPredictionSerializer`: Formats LSTM prediction results
  - `NSGA3QuotaPredictionSerializer`: Formats NSGA-III optimized results
  - `QuotaPredictionResponseSerializer`: Formats the complete response

### 2. `/ships/ml_models.py`

- **Purpose**: Implementation of machine learning algorithms for quota prediction
- **Key Components**:
  - `SimpleLSTM`: Simplified LSTM implementation for trend analysis
  - `NSGA3QuotaOptimizer`: Simplified NSGA-III implementation that optimizes LSTM predictions
  - `predict_and_optimize_quota`: Main function implementing the sequential approach
  - Helper functions for data retrieval and recommendation generation

### 3. `/ships/views_quota.py`

- **Purpose**: Django REST Framework view for the quota prediction endpoint
- **Key Components**:
  - `predict_ship_quota`: Main view function handling POST requests
  - Input validation and error handling
  - Integration with sequential ML process
  - Response formatting

### 4. `/ships/simple_test.py`

- **Purpose**: Simple test script to verify ML model functionality
- **Key Components**:
  - Tests for SimpleLSTM class
  - Tests for NSGA3QuotaOptimizer class
  - Tests for sequential prediction process

### 5. `/ships/test_quota_prediction.py`

- **Purpose**: Comprehensive test script with Django integration
- **Key Components**:
  - Tests for all ML model components
  - Integration tests with Django models

## Files Modified

### 1. `/ships/urls.py`

- **Changes**: Added URL pattern for the new quota prediction endpoint
- **New Endpoint**: `predict-quota/` mapped to `predict_ship_quota` view

### 2. `/requirements.txt`

- **Changes**: Added numpy and pandas dependencies
- **New Dependencies**:
  - `numpy==1.24.3`
  - `pandas==2.0.3`

### 3. `/README.md`

- **Changes**: Updated documentation to include quota prediction feature
- **Additions**:
  - New feature in "Fitur Utama" section
  - New endpoint in "Modul Ships" section
  - New "Modul Prediksi Kuota" section
  - Information about AI quota prediction in main description

## API Endpoint

### POST `/api/ships/predict-quota/`

**Request Body**:

```json
{
  "ship_registration_number": "string",
  "prediction_months": "integer (optional, default: 12)",
  "algorithm": "string (optional, choices: 'lstm', 'nsga3', 'both', default: 'both')"
}
```

**Response**:

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

## Sequential Algorithm Details

### Step 1: LSTM (Long Short-Term Memory)

- Analyzes historical catch trends
- Provides initial trend-based predictions
- Includes confidence intervals

### Step 2: NSGA-III (Non-dominated Sorting Genetic Algorithm III)

- Takes LSTM predictions as input
- Multi-objective optimization balancing:
  - Productivity (based on LSTM predictions)
  - Environmental impact minimization
  - Long-term sustainability
- Provides optimized quota values with fitness scores

## Implementation Approach

1. **Sequential Design**: LSTM predictions are optimized by NSGA-III in a single process
2. **Modular Design**: Separate files for serializers, models, and views
3. **Django Integration**: Full compatibility with Django REST Framework
4. **Type Safety**: Proper type annotations and error handling
5. **Documentation**: OpenAPI/Swagger documentation with drf-spectacular
6. **Testing**: Comprehensive test suite for all components

## Usage Instructions

1. Ensure required dependencies are installed:

   ```bash
   pip install numpy pandas
   ```

2. Apply any new migrations (if applicable):

   ```bash
   python manage.py migrate
   ```

3. Start the development server:

   ```bash
   python manage.py runserver
   ```

4. Access the new endpoint at:
   `POST /api/ships/predict-quota/`

5. View API documentation at:
   - Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
   - Redoc: `http://localhost:8000/api/schema/redoc/`

## Testing

Run the simple test to verify functionality:

```bash
cd /Users/ROFI/Develop/proyek/fco_project/ships
python simple_test.py
```

## Future Improvements

1. **Enhanced LSTM Implementation**: Use proper TensorFlow/Keras implementation
2. **Advanced NSGA-III**: Use pymoo library for more sophisticated optimization
3. **Additional Features**:
   - Seasonal pattern recognition
   - External factor integration (weather, regulations)
   - Real-time model updating
4. **Performance Optimization**:
   - Caching mechanisms
   - Asynchronous processing
   - Database query optimization

## Dependencies

The quota prediction module requires:

- numpy (for numerical computations)
- pandas (for data manipulation)
- Django REST Framework (for API integration)
- drf-spectacular (for API documentation)

These dependencies have been added to the requirements.txt file.
