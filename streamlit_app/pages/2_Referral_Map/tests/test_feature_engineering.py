import unittest
import pandas as pd
import numpy as np
from models.feature_engineering import FeatureEngineer

class TestFeatureEngineering(unittest.TestCase):
    def setUp(self):
        """Set up test data."""
        # Create sample data
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='M')
        n_facilities = 3
        n_states = 2
        
        data = []
        for state in range(n_states):
            for facility in range(n_facilities):
                for date in dates:
                    # Create seasonal pattern with noise
                    month = date.month
                    seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * month / 12)
                    referrals = int(100 * seasonal_factor + np.random.normal(0, 10))
                    
                    data.append({
                        'year_month': date.strftime('%Y%m'),
                        'state': f'State_{state}',
                        'aha_identification_number': f'Facility_{facility}',
                        'qualified_referrals': max(0, referrals),  # Ensure non-negative
                        'beds': 100 + facility * 50,
                        'trauma_level': f'Level_{facility + 1}'
                    })
        
        self.test_data = pd.DataFrame(data)
        
    def test_seasonality_features(self):
        """Test seasonality feature generation."""
        # Initialize feature engineer with seasonality
        fe = FeatureEngineer(
            categorical_features=['state', 'trauma_level'],
            add_seasonality=True,
            date_column='year_month'
        )
        
        # Transform data
        transformed = fe.fit_transform(self.test_data)
        
        # Check that seasonal features exist
        seasonal_features = ['seasonal_index', 'month_sin', 'month_cos']
        for feature in seasonal_features:
            self.assertIn(feature, transformed.columns)
            
        # Check that seasonal index has expected properties
        self.assertTrue(transformed['seasonal_index'].mean() > 0.5)  # Should be roughly centered around 1
        self.assertTrue(transformed['seasonal_index'].std() > 0)  # Should have variation
        
        # Check cyclical features
        self.assertTrue(np.all(transformed['month_sin'].between(-1, 1)))
        self.assertTrue(np.all(transformed['month_cos'].between(-1, 1)))
        
    def test_time_lag_features(self):
        """Test time lag feature generation."""
        # Initialize feature engineer with time lags
        fe = FeatureEngineer(
            categorical_features=['state', 'trauma_level'],
            time_lags=[1, 3, 6],
            target_column='qualified_referrals',
            date_column='year_month'
        )
        
        # Transform data
        transformed = fe.fit_transform(self.test_data)
        
        # Check that lag features exist
        for lag in [1, 3, 6]:
            lag_features = [
                f'qualified_referrals_lag_{lag}',
                f'qualified_referrals_lag_{lag}_rolling_mean'
            ]
            for feature in lag_features:
                self.assertIn(feature, transformed.columns)
                
        # Check that lag 1 values match original values shifted by 1
        facility = self.test_data['aha_identification_number'].iloc[0]
        state = self.test_data['state'].iloc[0]
        facility_data = transformed[
            (transformed['aha_identification_number'] == facility) & 
            (transformed['state'] == state)
        ].sort_values('year_month')
        
        # Compare non-zero values only (skip first value which should be 0)
        pd.testing.assert_series_equal(
            facility_data['qualified_referrals'].shift(1).fillna(0),
            facility_data['qualified_referrals_lag_1'],
            check_dtype=False,
            check_names=False  # Don't compare series names
        )
        
    def test_combined_features(self):
        """Test both seasonality and time lag features together."""
        # Initialize feature engineer with both feature types
        fe = FeatureEngineer(
            categorical_features=['state', 'trauma_level'],
            add_seasonality=True,
            time_lags=[1, 3],
            target_column='qualified_referrals',
            date_column='year_month'
        )
        
        # Transform data
        transformed = fe.fit_transform(self.test_data)
        
        # Check all expected features exist
        expected_features = [
            'seasonal_index', 'month_sin', 'month_cos',
            'qualified_referrals_lag_1', 'qualified_referrals_lag_1_rolling_mean',
            'qualified_referrals_lag_3', 'qualified_referrals_lag_3_rolling_mean'
        ]
        
        for feature in expected_features:
            self.assertIn(feature, transformed.columns)
            
        # Check no NaN values in engineered features
        for feature in expected_features:
            self.assertFalse(transformed[feature].isna().any())
            
    def test_error_handling(self):
        """Test error handling for missing columns."""
        # Create data without required columns
        bad_data = self.test_data.drop(columns=['year_month'])
        
        fe = FeatureEngineer(
            categorical_features=['state', 'trauma_level'],
            add_seasonality=True
        )
        
        # Should return original data unchanged when date column missing
        result = fe.fit_transform(bad_data)
        pd.testing.assert_frame_equal(result, bad_data)

if __name__ == '__main__':
    unittest.main()
