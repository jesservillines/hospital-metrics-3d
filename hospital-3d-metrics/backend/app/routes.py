from fastapi import APIRouter, HTTPException
from typing import List, Optional
import pandas as pd
import numpy as np
from .models import MetricData, FloorMetrics, MetricFilter
from .services.metrics_service import metrics_service
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


def clean_float_value(value, to_int=False) -> float:
    """Clean float values to ensure JSON compliance and optionally convert to integers."""
    if pd.isna(value) or np.isnan(value):
        return 0 if to_int else 0.0
    if np.isinf(value):
        return 0 if to_int else 0.0
    try:
        cleaned_value = float(value)
        return int(cleaned_value) if to_int else cleaned_value
    except (TypeError, ValueError):
        return 0 if to_int else 0.0


@router.get("/metrics")
async def get_metrics(
        floor: Optional[str] = None,
        metric_name: Optional[str] = None,
        metric_type: Optional[str] = None
):
    try:
        logger.info(f"Getting metrics with filters - floor: {floor}, metric: {metric_name}, type: {metric_type}")
        metrics = metrics_service.get_filtered_metrics(floor, metric_name, metric_type)
        logger.info(f"Retrieved {len(metrics)} metrics")

        # Clean float values
        for metric in metrics:
            if 'value' in metric:
                metric['value'] = clean_float_value(metric['value'])

        return metrics
    except Exception as e:
        logger.error(f"Error in get_metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/floors/{floor_id}/metrics")
async def get_floor_metrics(floor_id: str):
    try:
        floor_name = floor_id.replace("%20", " ")
        logger.info(f"Getting metrics for floor: {floor_name}")

        # Get floor metrics
        floor_metrics = metrics_service.get_floor_metrics(floor_name)
        logger.info(f"Retrieved {len(floor_metrics)} floor metrics")

        # Get room metrics
        room_metrics = metrics_service.get_room_metrics_by_floor(floor_name)
        logger.info(f"Retrieved {len(room_metrics)} room metrics")

        # Format response
        formatted_metrics = []

        # Add floor-level metrics
        for metric in floor_metrics:
            formatted_metric = {
                "floor": floor_name,
                "metric_name": metric["metric_name"],
                "value": clean_float_value(metric["value"]),
                "timestamp": metric["timestamp"],
                "metric_type": "floor"
            }
            formatted_metrics.append(formatted_metric)

        # Add room-level metrics
        for metric in room_metrics:
            formatted_metric = {
                "floor": floor_name,
                "room": metric["room_id"],
                "metric_name": metric["metric_name"],
                "value": clean_float_value(metric["value"]),
                "timestamp": metric["timestamp"],
                "metric_type": "room"
            }
            formatted_metrics.append(formatted_metric)

        logger.info(f"Returning {len(formatted_metrics)} total metrics for floor {floor_name}")
        return formatted_metrics

    except Exception as e:
        logger.error(f"Error getting floor metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heatmap/{floor_id}")
async def get_heatmap_data(
        floor_id: str,
        metric_name: str
):
    try:
        floor_name = floor_id.replace("%20", " ")
        logger.info(f"Getting heatmap data for floor {floor_name} and metric {metric_name}")

        metrics = metrics_service.get_heatmap_data(floor_name, metric_name)
        logger.info(f"Retrieved {len(metrics)} metrics for heatmap")

        # Format the response
        formatted_metrics = []
        for metric in metrics:
            formatted_metric = {
                "floor": floor_name,
                "metric_name": metric["metric_name"],
                "value": clean_float_value(metric["value"]),
                "timestamp": metric["timestamp"],
                "metric_type": "floor" if not metric.get("room_id") else "room"
            }
            if "room_id" in metric:
                formatted_metric["room"] = metric["room_id"]
            formatted_metrics.append(formatted_metric)

        logger.info(f"Returning {len(formatted_metrics)} formatted metrics for heatmap")
        return formatted_metrics
    except Exception as e:
        logger.error(f"Error getting heatmap data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))