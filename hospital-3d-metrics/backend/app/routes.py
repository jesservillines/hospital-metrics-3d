# backend/app/routes.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import pandas as pd
from .models import MetricData, FloorMetrics, MetricFilter

router = APIRouter()

# In-memory data store (replace with database in production)
df = pd.read_csv("data/initial_metrics.csv")


@router.get("/metrics", response_model=List[MetricData])
async def get_metrics(
        floor: Optional[str] = None,
        metric_name: Optional[str] = None
):
    filtered_df = df.copy()

    if floor:
        filtered_df = filtered_df[filtered_df['floor'] == floor]
    if metric_name:
        filtered_df = filtered_df[filtered_df['metric_name'] == metric_name]

    return filtered_df.to_dict('records')


@router.get("/floors/{floor_id}/metrics", response_model=FloorMetrics)
async def get_floor_metrics(floor_id: str):
    floor_data = df[df['floor'] == floor_id]
    if floor_data.empty:
        raise HTTPException(status_code=404, detail="Floor not found")

    metrics = dict(zip(floor_data['metric_name'], floor_data['value']))
    return FloorMetrics(floor=floor_id, metrics=metrics)


@router.post("/metrics/filter", response_model=List[MetricData])
async def filter_metrics(filter_params: MetricFilter):
    filtered_df = df.copy()

    if filter_params.metric_name:
        filtered_df = filtered_df[filtered_df['metric_name'] == filter_params.metric_name]
    if filter_params.start_date:
        filtered_df = filtered_df[filtered_df['timestamp'] >= filter_params.start_date]
    if filter_params.end_date:
        filtered_df = filtered_df[filtered_df['timestamp'] <= filter_params.end_date]

    return filtered_df.to_dict('records')