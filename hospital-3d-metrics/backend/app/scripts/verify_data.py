import sys
import os
from sqlalchemy import text

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database import engine

def verify_data():
    """Verify the imported data."""
    with engine.connect() as conn:
        # Check floor_metrics count
        result = conn.execute(text("SELECT COUNT(*) FROM floor_metrics"))
        floor_count = result.scalar()
        print(f"Floor metrics count: {floor_count}")
        
        # Check room_metrics count
        result = conn.execute(text("SELECT COUNT(*) FROM room_metrics"))
        room_count = result.scalar()
        print(f"Room metrics count: {room_count}")
        
        # Sample floor metrics
        result = conn.execute(text("SELECT floor, metric_name, value, metric_category FROM floor_metrics LIMIT 5"))
        print("\nSample floor metrics:")
        for row in result:
            print(f"Floor: {row.floor}, Metric: {row.metric_name}, Value: {row.value}, Category: {row.metric_category}")
        
        # Sample room metrics
        result = conn.execute(text("SELECT room_id, floor, metric_name, value, metric_category FROM room_metrics LIMIT 5"))
        print("\nSample room metrics:")
        for row in result:
            print(f"Room: {row.room_id}, Floor: {row.floor}, Metric: {row.metric_name}, Value: {row.value}, Category: {row.metric_category}")

if __name__ == "__main__":
    verify_data()
