import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import ReferralPredictor, FeatureEngineer

class TestScenarioPlanning(unittest.TestCase):
    def setUp(self):
        """Set up test data and model"""
        # Create sample dates
        self.dates = pd.date_range(
            start='2024-01-01',
            end='2024-12-31',
            freq='ME'
        )
        
        # Create sample facilities with more realistic data
        self.facilities = ['FAC1', 'FAC2', 'FAC3']
        self.states = ['CA', 'CA', 'CA']
        self.beds = [300, 200, 150]  # Larger facilities have more beds
        self.referrals = [100.0, 75.0, 50.0]  # Larger facilities get more referrals, using float
        
        # Create sample data with proper dtypes
        self.data = pd.DataFrame({
            'year_month': np.repeat(self.dates, len(self.facilities)),
            'aha_identification_number': self.facilities * len(self.dates),
            'state': self.states * len(self.dates),
            'beds': self.beds * len(self.dates),
            'trauma_1': [1, 0, 0] * len(self.dates),  # Largest facility is Level 1
            'trauma_2': [0, 1, 0] * len(self.dates),  # Medium facility is Level 2
            'trauma_3': [0, 0, 1] * len(self.dates),  # Small facility is Level 3
            'trauma_4': [0, 0, 0] * len(self.dates),
            'low_rship': [0, 0, 1] * len(self.dates),  # Relationship strength correlates with size
            'mid_rship': [0, 1, 0] * len(self.dates),
            'strong_rship': [1, 0, 0] * len(self.dates),
            'model_system_member': [1, 1, 0] * len(self.dates),  # Larger facilities are members
            'is_competitor': [0, 0, 0] * len(self.dates),
            'num_irfs_in_state': [3, 3, 3] * len(self.dates),
            'referrals': self.referrals * len(self.dates)
        }).astype({
            'referrals': 'float64',
            'beds': 'int64',
            'trauma_1': 'int64',
            'trauma_2': 'int64',
            'trauma_3': 'int64',
            'trauma_4': 'int64',
            'low_rship': 'int64',
            'mid_rship': 'int64',
            'strong_rship': 'int64',
            'model_system_member': 'int64',
            'is_competitor': 'int64',
            'num_irfs_in_state': 'int64'
        })
        
        # Initialize model
        self.model = ReferralPredictor()
        self.feature_engineer = FeatureEngineer()
        
        # Define categorical features
        self.cat_features = [
            'aha_identification_number',
            'state',
            'trauma_1',
            'trauma_2',
            'trauma_3',
            'trauma_4',
            'low_rship',
            'mid_rship',
            'strong_rship',
            'model_system_member',
            'is_competitor'
        ]
        
        # Prepare training data
        self.X = self.data.drop(['referrals', 'year_month'], axis=1)
        self.y = self.data['referrals']
        
        # Set categorical features in model
        self.model.cat_features = self.cat_features
        
        # Train model
        self.model.fit(self.X, self.y)
        
    def test_data_preparation(self):
        """Test data preparation for scenario planning"""
        # Test date handling
        self.assertEqual(len(self.dates), 12, "Should have 12 months of data")
        self.assertTrue(all(isinstance(d, pd.Timestamp) for d in self.dates), 
                       "All dates should be pandas Timestamps")
        
        # Test facility data structure
        facility_counts = self.data.groupby('aha_identification_number').size()
        self.assertTrue(all(count == 12 for count in facility_counts), 
                       "Each facility should have 12 months of data")
        
    def test_add_competitor(self):
        """Test adding a competitor scenario"""
        # Create competitor scenario
        competitor_data = self.data.copy()
        
        # Reduce referrals more for smaller facilities (they're more vulnerable)
        state_mask = competitor_data['state'] == 'CA'
        
        # Convert to float64 before multiplication
        competitor_data['referrals'] = competitor_data['referrals'].astype('float64')
        competitor_data['beds'] = competitor_data['beds'].astype('float64')  # Convert beds to float
        
        # Apply reductions based on facility size
        small_mask = competitor_data['beds'] <= 200
        large_mask = competitor_data['beds'] > 200
        
        # More aggressive reductions in referrals
        competitor_data.loc[state_mask & small_mask, 'referrals'] = (
            competitor_data.loc[state_mask & small_mask, 'referrals'] * 0.5  # 50% reduction for smaller facilities
        )
        competitor_data.loc[state_mask & large_mask, 'referrals'] = (
            competitor_data.loc[state_mask & large_mask, 'referrals'] * 0.7  # 30% reduction for larger facilities
        )
        
        competitor_data.loc[state_mask, 'num_irfs_in_state'] += 2  # Add two competitors to increase market pressure
        
        # Add new competitor facility targeting mid-size market
        new_competitor = pd.DataFrame({
            'year_month': self.dates,
            'aha_identification_number': ['NEW_COMP'] * len(self.dates),
            'state': ['CA'] * len(self.dates),
            'beds': [250.0] * len(self.dates),  # Larger facility to be more competitive
            'trauma_2': [1] * len(self.dates),  # Level 2 trauma center
            'trauma_1': [0] * len(self.dates),
            'trauma_3': [0] * len(self.dates),
            'trauma_4': [0] * len(self.dates),
            'low_rship': [0] * len(self.dates),
            'mid_rship': [1] * len(self.dates),  # Moderate relationships
            'strong_rship': [0] * len(self.dates),
            'model_system_member': [1] * len(self.dates),  # Part of a system
            'is_competitor': [1] * len(self.dates),
            'num_irfs_in_state': [5] * len(self.dates),  # Account for both new competitors
            'referrals': [25.0] * len(self.dates)  # Lower initial referrals
        }).astype({
            'referrals': 'float64',
            'beds': 'float64',
            'trauma_1': 'int64',
            'trauma_2': 'int64',
            'trauma_3': 'int64',
            'trauma_4': 'int64',
            'low_rship': 'int64',
            'mid_rship': 'int64',
            'strong_rship': 'int64',
            'model_system_member': 'int64',
            'is_competitor': 'int64',
            'num_irfs_in_state': 'int64'
        })
        
        competitor_data = pd.concat([competitor_data, new_competitor], ignore_index=True)
        
        # Get predictions
        baseline_pred = self.model.predict(self.X)[0]
        scenario_pred = self.model.predict(competitor_data.drop(['year_month', 'referrals'], axis=1))[0]
        
        # Test impact
        self.assertLess(scenario_pred.sum(), baseline_pred.sum(), 
                       "Adding competitor should decrease total referrals")
        
    def test_add_trauma_center(self):
        """Test adding a trauma center scenario"""
        # Create trauma center scenario
        trauma_data = self.data.copy()
        
        # Add new trauma center
        new_trauma = pd.DataFrame({
            'year_month': self.dates,
            'aha_identification_number': ['NEW_TRAUMA'] * len(self.dates),
            'state': ['CA'] * len(self.dates),
            'beds': [500] * len(self.dates),
            'trauma_1': [1] * len(self.dates),
            'trauma_2': [0] * len(self.dates),
            'trauma_3': [0] * len(self.dates),
            'trauma_4': [0] * len(self.dates),
            'low_rship': [0] * len(self.dates),
            'mid_rship': [0] * len(self.dates),
            'strong_rship': [1] * len(self.dates),
            'model_system_member': [1] * len(self.dates),
            'is_competitor': [0] * len(self.dates),
            'num_irfs_in_state': [3] * len(self.dates)
        })
        
        trauma_data = pd.concat([trauma_data, new_trauma], ignore_index=True)
        
        # Get predictions
        baseline_pred = self.model.predict(self.X)[0]
        scenario_pred = self.model.predict(trauma_data.drop(['year_month'], axis=1))[0]
        
        # Test impact
        self.assertGreater(scenario_pred.sum(), baseline_pred.sum(), 
                          "Adding trauma center should increase total referrals")
        
    def test_annual_calculations(self):
        """Test annual impact calculations"""
        # Get last 12 months predictions
        baseline_pred = self.model.predict(self.X)[0]
        
        # Calculate annual total
        annual_total = baseline_pred.sum() * 12
        
        # Test calculations
        self.assertGreater(annual_total, 0, "Annual total should be positive")
        self.assertEqual(len(baseline_pred), len(self.data), 
                        "Should have predictions for all data points")

if __name__ == '__main__':
    unittest.main()
