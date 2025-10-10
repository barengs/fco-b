#!/usr/bin/env python3
"""
Simple test script for PNBP prediction functionality
"""

import sys
import os

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fco_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

def test_pnbp_basic():
    """Test basic PNBP prediction functionality"""
    try:
        # Test imports
        from catches.views import PNBPredictor
        print("✓ PNBP prediction module imported successfully")

        # Create sample historical data
        sample_data = [
            {"total_pnbp": 10000000, "total_volume": 150, "gt_kapal": 70},
            {"total_pnbp": 12000000, "total_volume": 180, "gt_kapal": 75},
            {"total_pnbp": 9500000, "total_volume": 140, "gt_kapal": 65},
            {"total_pnbp": 11000000, "total_volume": 165, "gt_kapal": 72},
            {"total_pnbp": 13000000, "total_volume": 190, "gt_kapal": 78},
        ]

        predictor = PNBPredictor()

        # Test individual predictors
        regression_pred = predictor.regression_predictor.predict(sample_data)
        print(f"✓ Regression prediction: Rp {regression_pred:,.0f}")

        neural_pred = predictor.neural_predictor.predict(sample_data)
        print(f"✓ Neural network prediction: Rp {neural_pred:,.0f}")

        optimization_pred = predictor.optimization_predictor.predict(sample_data)
        print(f"✓ Optimization prediction: Rp {optimization_pred:,.0f}")

        time_series_pred = predictor.time_series_predictor.predict(sample_data)
        print(f"✓ Time series prediction: Rp {time_series_pred:,.0f}")

        # Test full pipeline
        results = predictor.run_prediction_pipeline(sample_data)
        print(f"✓ Full pipeline completed")
        print(f"  Final prediction (normalized): {results['final_prediction']:.4f}")

        # Test saving
        success = predictor.save_results(results, "test_pnbp_predictions.json")
        if success:
            print("✓ Results saved to JSON")
        else:
            print("✗ Failed to save results")

        print("\n🎉 All PNBP prediction tests passed!")
        return True

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing PNBP Prediction Module...")
    print("=" * 50)

    success = test_pnbp_basic()

    if success:
        print("\n✅ PNBP prediction module is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ PNBP prediction module has issues!")
        sys.exit(1)