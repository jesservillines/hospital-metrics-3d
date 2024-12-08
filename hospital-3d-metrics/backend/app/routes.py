# backend/app/routes.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import pandas as pd
from .models import MetricData, FloorMetrics, MetricFilter

router = APIRouter()

# In-memory data store (replace with database in production)
df = pd.read_csv("data/initial_metrics.csv")
# Fill NaN values in room column with empty string
df['room'] = df['room'].fillna('')
# Ensure metric_type has a default value
df['metric_type'] = df['metric_type'].fillna('floor')

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

    # Convert DataFrame to dict records and ensure all fields are properly formatted
    results = []
    for _, row in filtered_df.iterrows():
        metric_data = {
            'floor': row['floor'],
            'room': row['room'] if pd.notna(row.get('room', '')) else '',
            'metric_name': row['metric_name'],
            'value': float(row['value']),
            'timestamp': row['timestamp'],
            'metric_type': row.get('metric_type', 'floor')
        }
        results.append(metric_data)

    return results

@router.get("/floors/{floor_id}/metrics", response_model=FloorMetrics)
async def get_floor_metrics(floor_id: str):
    floor_data = df[df['floor'] == floor_id]
    if floor_data.empty:
        raise HTTPException(status_code=404, detail="Floor not found")

    # Get floor-level metrics
    floor_metrics_data = floor_data[floor_data['metric_type'] == 'floor']
    floor_metrics = dict(zip(floor_metrics_data['metric_name'], floor_metrics_data['value']))

    # Get room-level metrics
    room_metrics_data = floor_data[floor_data['metric_type'] == 'room']
    room_metrics = {}
    for room in room_metrics_data['room'].unique():
        if pd.notna(room) and room != '':
            room_data = room_metrics_data[room_metrics_data['room'] == room]
            room_metrics[room] = dict(zip(room_data['metric_name'], room_data['value']))

    return FloorMetrics(
        floor=floor_id,
        floor_metrics=floor_metrics,
        room_metrics=room_metrics
    )

@router.post("/metrics/filter", response_model=List[MetricData])
async def filter_metrics(filter_params: MetricFilter):
    filtered_df = df.copy()

    if filter_params.metric_name:
        filtered_df = filtered_df[filtered_df['metric_name'] == filter_params.metric_name]
    if filter_params.start_date:
        filtered_df = filtered_df[filtered_df['timestamp'] >= filter_params.start_date]
    if filter_params.end_date:
        filtered_df = filtered_df[filtered_df['timestamp'] <= filter_params.end_date]
    if filter_params.metric_type:
        filtered_df = filtered_df[filtered_df['metric_type'] == filter_params.metric_type]

    # Convert DataFrame to dict records with proper null handling
    results = []
    for _, row in filtered_df.iterrows():
        metric_data = {
            'floor': row['floor'],
            'room': row['room'] if pd.notna(row.get('room', '')) else '',
            'metric_name': row['metric_name'],
            'value': float(row['value']),
            'timestamp': row['timestamp'],
            'metric_type': row.get('metric_type', 'floor')
        }
        results.append(metric_data)

    return results