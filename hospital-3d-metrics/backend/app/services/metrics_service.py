import pandas as pd
import numpy as np
from pathlib import Path
import os
from typing import List, Dict, Optional, Union
import logging
from fastapi.encoders import jsonable_encoder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricsService:
    def __init__(self):
        # Get the absolute path to the backend directory
        current_file = Path(__file__)
        backend_dir = current_file.parent.parent.parent
        self.data_dir = backend_dir / 'data'

        logger.info(f"Data directory path: {self.data_dir}")

        self.floor_metrics_df = None
        self.room_metrics_df = None
        self.patient_metrics_df = None
        self.staff_metrics_df = None
        self.load_data()

    def load_data(self):
        """Load all CSV data files into pandas DataFrames"""
        try:
            logger.info("Loading data files...")

            # Load each DataFrame
            self.floor_metrics_df = pd.read_csv(self.data_dir / 'floor_metrics.csv')
            self.room_metrics_df = pd.read_csv(self.data_dir / 'room_metrics.csv')
            self.patient_metrics_df = pd.read_csv(self.data_dir / 'patient_metrics.csv')
            self.staff_metrics_df = pd.read_csv(self.data_dir / 'staff_metrics.csv')

            # Clean each DataFrame
            self.floor_metrics_df = self.clean_dataframe(self.floor_metrics_df)
            self.room_metrics_df = self.clean_dataframe(self.room_metrics_df)
            self.patient_metrics_df = self.clean_dataframe(self.patient_metrics_df)
            self.staff_metrics_df = self.clean_dataframe(self.staff_metrics_df)

            logger.info("Data files loaded successfully")
        except Exception as e:
            logger.error(f"Error loading data files: {str(e)}")
            raise

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame values."""
        if df is None:
            return pd.DataFrame()

        df = df.replace([np.inf, -np.inf], 0)
        df = df.fillna(0)
        return df

    def to_dict(self, row: pd.Series) -> dict:
        """Convert a pandas Series to a JSON-safe dictionary."""
        return {k: float(v) if isinstance(v, (int, float)) else v
                for k, v in row.to_dict().items()}

    def get_floor_metrics(self, floor: str) -> List[Dict]:
        """Get metrics for a specific floor"""
        try:
            floor_data = self.floor_metrics_df[self.floor_metrics_df['floor'] == floor]
            return [self.to_dict(row) for _, row in floor_data.iterrows()]
        except Exception as e:
            logger.error(f"Error getting floor metrics: {str(e)}")
            return []

    def get_room_metrics_by_floor(self, floor: str) -> List[Dict]:
        """Get all room metrics for a specific floor"""
        try:
            floor_rooms = self.room_metrics_df[self.room_metrics_df['floor'] == floor]
            return [self.to_dict(row) for _, row in floor_rooms.iterrows()]
        except Exception as e:
            logger.error(f"Error getting floor room metrics: {str(e)}")
            return []

    def get_heatmap_data(self, floor: str, metric_name: str) -> List[Dict]:
        """Get heatmap data for a specific floor and metric"""
        try:
            # Get metrics from all relevant sources
            all_metrics = []

            # Add floor metrics if they exist
            floor_metrics = self.floor_metrics_df[
                (self.floor_metrics_df['floor'] == floor) &
                (self.floor_metrics_df['metric_name'] == metric_name)
                ]
            all_metrics.extend([self.to_dict(row) for _, row in floor_metrics.iterrows()])

            # Add room metrics if they exist
            room_metrics = self.room_metrics_df[
                (self.room_metrics_df['floor'] == floor) &
                (self.room_metrics_df['metric_name'] == metric_name)
                ]
            all_metrics.extend([self.to_dict(row) for _, row in room_metrics.iterrows()])

            return all_metrics
        except Exception as e:
            logger.error(f"Error getting heatmap data: {str(e)}")
            return []

    def get_filtered_metrics(self, floor: Optional[str] = None,
                             metric_name: Optional[str] = None,
                             metric_type: Optional[str] = None) -> List[Dict]:
        """Get metrics with optional filtering"""
        try:
            # Start with floor metrics
            metrics = []
            df = self.floor_metrics_df

            if floor:
                df = df[df['floor'] == floor]
            if metric_name:
                df = df[df['metric_name'] == metric_name]

            metrics.extend([self.to_dict(row) for _, row in df.iterrows()])
            return metrics
        except Exception as e:
            logger.error(f"Error getting filtered metrics: {str(e)}")
            return []


# Create singleton instance
metrics_service = MetricsService()