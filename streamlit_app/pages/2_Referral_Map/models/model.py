from typing import Tuple, Dict, Optional, List
import pandas as pd
import numpy as np
from catboost import CatBoostRegressor, Pool
from sklearn.model_selection import TimeSeriesSplit
from .feature_engineering import FeatureEngineer

class ReferralPredictor:
    """Referral prediction model using CatBoost with confidence intervals."""
    
    def __init__(self,
                 selected_features: List[str],
                 confidence_level: float = 0.90,
                 feature_engineer: Optional[FeatureEngineer] = None,
                 model_params: Optional[Dict] = None,
                 cat_features: Optional[list] = None):
        """
        Initialize the ReferralPredictor.
        
        Args:
            selected_features: List of feature names to use
            confidence_level: Confidence level for prediction intervals (default: 0.90)
            feature_engineer: Optional FeatureEngineer instance for feature transformation
            model_params: Optional dictionary of CatBoost parameters
            cat_features: List of categorical feature names
        """
        self.selected_features = selected_features
        self.confidence_level = confidence_level
        self.feature_engineer = feature_engineer
        
        # Default model parameters
        default_params = {
            'iterations': 1000,
            'learning_rate': 0.03,
            'depth': 6,
            'loss_function': 'RMSE',
            'verbose': False
        }
        
        # Update with custom parameters if provided
        self.model_params = default_params.copy()
        if model_params:
            self.model_params.update(model_params)
        
        # Initialize model
        self.model = CatBoostRegressor(**self.model_params)
        self.feature_names = None
        self.cat_feature_names = None
        self.cat_features = cat_features or []
        
    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Fit the model on training data.
        
        Args:
            X: Training features
            y: Target values
        """
        print("Starting model fitting...")
        print(f"Selected features: {self.selected_features}")
        print(f"Initial columns: {X.columns.tolist()}")
        
        # Apply feature engineering first
        if self.feature_engineer:
            print("Applying feature engineering...")
            X = self.feature_engineer.fit_transform(X)
            print(f"Columns after feature engineering: {X.columns.tolist()}")
        
        # Then verify all selected features are present
        missing_features = set(self.selected_features) - set(X.columns)
        if missing_features:
            print(f"Missing features detected: {missing_features}")
            print(f"Available features: {X.columns.tolist()}")
            raise ValueError(f"Missing features in data: {missing_features}")
        
        # Select only the specified features
        X = X[self.selected_features]
        print(f"Final features for training: {X.columns.tolist()}")
        
        # Identify categorical features by name and index
        cat_feature_names = [col for col in X.columns if X[col].dtype == 'object' or X[col].dtype == 'category']
        cat_feature_indices = [i for i, col in enumerate(X.columns) if col in cat_feature_names]
        
        print(f"Categorical features: {cat_feature_names}")
        print(f"Categorical indices: {cat_feature_indices}")
        
        # Store feature names and types
        self.feature_names = X.columns.tolist()
        self.cat_feature_names = cat_feature_names
        
        # Convert categorical columns to category dtype
        for col in cat_feature_names:
            X[col] = X[col].astype('category')
        
        # Create CatBoost pool with categorical features
        train_pool = Pool(
            data=X,
            label=y,
            cat_features=cat_feature_indices
        )
        
        # Fit the model
        self.model.fit(
            train_pool,
            eval_set=train_pool
        )
    
    def predict(self, X: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Generate predictions with confidence intervals.
        
        Args:
            X: Input features
            
        Returns:
            Tuple of (predictions, lower_bound, upper_bound)
        """
        # Keep a copy of the full data for feature engineering
        X_full = X.copy()
        
        # Apply feature engineering first
        if self.feature_engineer:
            X_full = self.feature_engineer.transform(X_full)
            # After feature engineering, select only the required features
            X = X_full[self.selected_features]
        else:
            # If no feature engineering, verify all selected features are present
            missing_features = set(self.selected_features) - set(X.columns)
            if missing_features:
                raise ValueError(f"Missing features in data: {missing_features}")
            X = X[self.selected_features]
        
        # Convert categorical columns to category dtype
        for col in self.cat_feature_names:
            X[col] = X[col].astype('category')
        
        # Create pool with categorical features
        cat_feature_indices = [i for i, col in enumerate(X.columns) if col in self.cat_feature_names]
        pred_pool = Pool(
            data=X,
            cat_features=cat_feature_indices
        )
            
        # Generate predictions
        predictions = self.model.predict(pred_pool)
        
        # Calculate prediction intervals using bootstrap
        n_bootstrap = 100
        bootstrap_predictions = []
        
        for _ in range(n_bootstrap):
            # Generate predictions with random seed
            bootstrap_pred = self.model.predict(
                pred_pool,
                ntree_start=np.random.randint(0, self.model.tree_count_),
                ntree_end=self.model.tree_count_
            )
            bootstrap_predictions.append(bootstrap_pred)
        
        # Calculate confidence intervals
        alpha = (1 - self.confidence_level) / 2
        lower_bound = np.percentile(bootstrap_predictions, alpha * 100, axis=0)
        upper_bound = np.percentile(bootstrap_predictions, (1 - alpha) * 100, axis=0)
        
        return pd.Series(predictions), pd.Series(lower_bound), pd.Series(upper_bound)
    
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        Evaluate model performance.
        
        Args:
            X: Test features
            y: True target values
            
        Returns:
            Dictionary of performance metrics
        """
        predictions, lower_bound, upper_bound = self.predict(X)
        
        # Calculate metrics
        mae = np.abs(predictions - y).mean()
        rmse = np.sqrt(((predictions - y) ** 2).mean())
        r2 = 1 - ((y - predictions) ** 2).sum() / ((y - y.mean()) ** 2).sum()
        coverage = ((y >= lower_bound) & (y <= upper_bound)).mean()
        
        return {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'prediction_interval_coverage': coverage
        }
        
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance from the trained model."""
        if not hasattr(self.model, 'feature_importances_'):
            raise ValueError("Model must be trained before getting feature importance")
        
        importance = self.model.get_feature_importance()
        return pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
    
    def get_feature_coefficients(self) -> pd.Series:
        """
        Get the feature coefficients from the trained model.
        
        Returns:
            pd.Series: Feature coefficients indexed by feature names
        """
        if not hasattr(self.model, 'feature_importances_'):
            raise ValueError("Model must be trained before getting coefficients")
        
        # Get feature importance values using regular importance
        importance = self.model.get_feature_importance()
        
        # Create a Series with feature names as index
        coefficients = pd.Series(importance, index=self.feature_names)
        
        # Normalize coefficients to be between 0 and 1
        coefficients = coefficients / coefficients.abs().max()
        
        return coefficients
