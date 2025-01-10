import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
import pytest

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from models import ReferralPredictor, FeatureEngineer

def load_test_data():
    """Load the actual data file for testing"""
    data_path = project_root / "model_df_ml.csv"
    df = pd.read_csv(data_path)
    df['year_month'] = pd.to_datetime(df['year_month'].astype(str), format='%Y%m')
    return df

def test_data_loading():
    """Test if we can load the data correctly"""
    df = load_test_data()
    print("\nData shape:", df.shape)
    print("\nColumns:", df.columns.tolist())
    print("\nSample data:\n", df.head())
    assert 'qualified_referrals' in df.columns
    assert 'year_month' in df.columns

def test_feature_engineering():
    """Test the feature engineering pipeline"""
    df = load_test_data()
    
    # Get feature columns
    feature_cols = [col for col in df.columns if col not in ['year_month', 'qualified_referrals']]
    print("\nFeature columns:", feature_cols)
    
    # Initialize feature engineer
    feature_engineer = FeatureEngineer(
        categorical_features=[col for col in feature_cols if df[col].dtype == 'object'],
        numerical_features=[col for col in feature_cols if df[col].dtype != 'object'],
        temporal_column=None,  # No temporal features for now
        target_column=None  # No rolling features for now
    )
    
    # Transform features
    X = df[feature_cols]
    print("\nInput shape:", X.shape)
    X_transformed = feature_engineer.fit_transform(X)
    print("\nTransformed shape:", X_transformed.shape)
    print("\nTransformed columns:", X_transformed.columns.tolist())

def test_model_training():
    """Test the full model training pipeline"""
    df = load_test_data()
    
    # Prepare features and target
    feature_cols = [col for col in df.columns if col not in ['year_month', 'qualified_referrals']]
    X = df[feature_cols]
    y = df['qualified_referrals']
    
    # Initialize feature engineer
    feature_engineer = FeatureEngineer(
        categorical_features=[col for col in feature_cols if df[col].dtype == 'object'],
        numerical_features=[col for col in feature_cols if df[col].dtype != 'object'],
        temporal_column=None,  # No temporal features for now
        target_column=None  # No rolling features for now
    )
    
    # Initialize model with parameters
    model_params = {
        'iterations': 100,
        'learning_rate': 0.1
    }
    
    # Initialize model
    model = ReferralPredictor(
        confidence_level=0.9,
        feature_engineer=feature_engineer,
        model_params=model_params
    )
    
    print("\nTraining model...")
    model.fit(X, y)
    
    # Make predictions
    print("\nMaking predictions...")
    predictions, lower_bound, upper_bound = model.predict(X)
    
    print("\nPrediction shape:", predictions.shape)
    print("\nSample predictions:")
    results_df = pd.DataFrame({
        'Actual': y[:5],
        'Predicted': predictions[:5],
        'Lower': lower_bound[:5],
        'Upper': upper_bound[:5]
    })
    print(results_df)

if __name__ == '__main__':
    print("Running tests...")
    test_data_loading()
    print("\n" + "="*50 + "\n")
    test_feature_engineering()
    print("\n" + "="*50 + "\n")
    test_model_training()
