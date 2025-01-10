import pandas as pd
import numpy as np
from typing import List, Optional
from sklearn.base import BaseEstimator, TransformerMixin

class FeatureEngineer(BaseEstimator, TransformerMixin):
    """Feature engineering pipeline for referral prediction."""
    
    def __init__(self, 
                 categorical_features: List[str],
                 numerical_features: List[str] = None,
                 temporal_column: Optional[str] = None,
                 target_column: Optional[str] = 'qualified_referrals',
                 add_seasonality: bool = False,
                 time_lags: List[int] = None,
                 date_column: str = 'year_month'):
        """
        Initialize feature engineering pipeline.
        
        Args:
            categorical_features: List of categorical column names
            numerical_features: List of numerical column names
            temporal_column: Name of the temporal column
            target_column: Name of the target column for rolling features
            add_seasonality: Whether to add seasonality features
            time_lags: List of months to lag
            date_column: Name of the date column (default: 'year_month')
        """
        self.categorical_features = categorical_features
        self.numerical_features = numerical_features or []
        self.temporal_column = temporal_column
        self.target_column = target_column
        self.add_seasonality = add_seasonality
        self.time_lags = time_lags or []
        self.state_seasons = {}  # Store state-specific seasonality patterns
        self.date_column = date_column
        self.engineered_features = []
        
    def fit(self, X: pd.DataFrame, y=None):
        """Fit the feature engineer (compute statistics if needed)."""
        if self.add_seasonality:
            self._add_seasonality(X)
        return self
        
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform the data using the feature engineering pipeline."""
        X = X.copy()
        
        print("Starting feature engineering transformation...")
        print(f"Initial columns: {X.columns.tolist()}")
        print(f"Settings - Seasonality: {self.add_seasonality}, Time Lags: {self.time_lags}")
        
        # Track engineered features
        self.engineered_features = []
        
        # Add seasonality features if requested
        if self.add_seasonality and self.date_column in X.columns:
            print("Adding seasonality features...")
            X = self._add_seasonality(X)
            self.engineered_features.extend(['seasonal_index', 'month_sin', 'month_cos'])
            print(f"After seasonality features: {X.columns.tolist()}")
        
        # Add time lags if specified
        if self.time_lags and self.date_column in X.columns:
            print(f"Adding time lag features for lags: {self.time_lags}")
            X = self._add_time_lags(X)
            for lag in self.time_lags:
                self.engineered_features.extend([
                    f'{self.target_column}_lag_{lag}',
                    f'{self.target_column}_lag_{lag}_rolling_mean'
                ])
            print(f"After time lag features: {X.columns.tolist()}")
        
        # Fill missing values in engineered features
        for feature in self.engineered_features:
            if feature in X.columns:
                X[feature] = X[feature].fillna(0)
        
        print(f"Final engineered features: {self.engineered_features}")
        print(f"Final columns: {X.columns.tolist()}")
        
        return X
    
    def fit_transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        """Fit to data, then transform it."""
        return self.fit(X).transform(X)
    
    def _extract_date_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract date-based features from date column."""
        df = df.copy()
        
        if self.date_column not in df.columns:
            return df
            
        # Convert to datetime if string
        if df[self.date_column].dtype == 'object':
            try:
                df[self.date_column] = pd.to_datetime(df[self.date_column], format='%Y%m')
            except ValueError:
                # Try parsing without specific format
                df[self.date_column] = pd.to_datetime(df[self.date_column])
            
        # Extract basic time features
        df['month'] = df[self.date_column].dt.month
        df['year'] = df[self.date_column].dt.year
        df['quarter'] = df[self.date_column].dt.quarter
        
        return df
    
    def _add_seasonality(self, X: pd.DataFrame) -> pd.DataFrame:
        """Add seasonality features to the data."""
        X = X.copy()
        
        print("Converting date column to datetime...")
        X[self.date_column] = pd.to_datetime(X[self.date_column])
        
        print("Calculating month components...")
        # Extract month from date for cyclical encoding
        month = X[self.date_column].dt.month
        
        # Calculate cyclical features
        X['month_sin'] = np.sin(2 * np.pi * month/12)
        X['month_cos'] = np.cos(2 * np.pi * month/12)
        
        # Calculate seasonal index only if target column is available
        if self.target_column in X.columns:
            seasonal_means = X.groupby(month)[self.target_column].mean()
            overall_mean = X[self.target_column].mean()
            seasonal_index = seasonal_means / overall_mean
            
            # Map seasonal index back to original data
            X['seasonal_index'] = month.map(seasonal_index)
        else:
            # If target column is not available (during prediction), set seasonal_index to 1
            X['seasonal_index'] = 1.0
            print(f"Warning: {self.target_column} not found in data. Setting seasonal_index to 1.0")
        
        print("Added seasonality features")
        return X

    def _add_time_lags(self, X: pd.DataFrame) -> pd.DataFrame:
        """Add time-lagged features to the data."""
        X = X.copy()
        
        print("Converting date column to datetime...")
        X[self.date_column] = pd.to_datetime(X[self.date_column])
        
        print(f"Adding time lags: {self.time_lags}")
        # Sort by facility and date
        X = X.sort_values([self.date_column])
        
        # Add lag features only if target column is available
        if self.target_column in X.columns:
            for lag in self.time_lags:
                # Create lag feature
                lag_col = f'{self.target_column}_lag_{lag}'
                X[lag_col] = X[self.target_column].shift(lag)
                
                # Create rolling mean feature
                rolling_mean_col = f'{self.target_column}_lag_{lag}_rolling_mean'
                X[rolling_mean_col] = X[self.target_column].rolling(window=lag, min_periods=1).mean()
                
                print(f"Added lag {lag} features: {lag_col}, {rolling_mean_col}")
        else:
            # If target column is not available (during prediction), set lag features to 0
            for lag in self.time_lags:
                lag_col = f'{self.target_column}_lag_{lag}'
                rolling_mean_col = f'{self.target_column}_lag_{lag}_rolling_mean'
                X[lag_col] = 0.0
                X[rolling_mean_col] = 0.0
                print(f"Warning: {self.target_column} not found in data. Setting {lag_col} and {rolling_mean_col} to 0.0")
        
        return X
    
    def get_feature_names(self) -> List[str]:
        """Get list of engineered feature names."""
        return self.engineered_features
