import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import (
    MetricDefinition, MetricCategory,
    Floor, Room, RoomMetric, FloorMetric
)

def seed_metric_definitions():
    """Seed initial metric definitions"""
    metrics = [
        # Patient metrics
        {
            'name': 'fall_risk',
            'display_name': 'Fall Risk',
            'category': MetricCategory.PATIENT,
            'data_type': 'numeric',
            'description': 'Patient fall risk assessment score',
            'units': 'score',
            'aggregation_type': 'avg'
        },
        {
            'name': 'mobility_score',
            'display_name': 'Mobility Score',
            'category': MetricCategory.PATIENT,
            'data_type': 'numeric',
            'description': 'Patient mobility assessment score',
            'units': 'score',
            'aggregation_type': 'avg'
        },
        {
            'name': 'pain_level',
            'display_name': 'Pain Level',
            'category': MetricCategory.PATIENT,
            'data_type': 'numeric',
            'description': 'Patient pain level assessment',
            'units': 'score',
            'aggregation_type': 'avg'
        },
        {
            'name': 'satisfaction_score',
            'display_name': 'Satisfaction Score',
            'category': MetricCategory.PATIENT,
            'data_type': 'numeric',
            'description': 'Patient satisfaction score',
            'units': 'score',
            'aggregation_type': 'avg'
        },
        {
            'name': 'therapy_completion',
            'display_name': 'Therapy Completion',
            'category': MetricCategory.PATIENT,
            'data_type': 'numeric',
            'description': 'Therapy completion rate',
            'units': 'percentage',
            'aggregation_type': 'avg'
        },
        # Staff metrics
        {
            'name': 'schedule_compliance',
            'display_name': 'Schedule Compliance',
            'category': MetricCategory.STAFF,
            'data_type': 'numeric',
            'description': 'Staff schedule compliance rate',
            'units': 'percentage',
            'aggregation_type': 'avg'
        },
        {
            'name': 'patient_engagement',
            'display_name': 'Patient Engagement',
            'category': MetricCategory.STAFF,
            'data_type': 'numeric',
            'description': 'Staff patient engagement score',
            'units': 'score',
            'aggregation_type': 'avg'
        },
        {
            'name': 'documentation_completion',
            'display_name': 'Documentation Completion',
            'category': MetricCategory.STAFF,
            'data_type': 'numeric',
            'description': 'Documentation completion rate',
            'units': 'percentage',
            'aggregation_type': 'avg'
        },
        {
            'name': 'patients_per_day',
            'display_name': 'Patients Per Day',
            'category': MetricCategory.STAFF,
            'data_type': 'numeric',
            'description': 'Number of patients seen per day',
            'units': 'count',
            'aggregation_type': 'avg'
        },
        {
            'name': 'equipment_maintenance',
            'display_name': 'Equipment Maintenance',
            'category': MetricCategory.STAFF,
            'data_type': 'numeric',
            'description': 'Equipment maintenance compliance score',
            'units': 'percentage',
            'aggregation_type': 'avg'
        },
        {
            'name': 'patients_assigned',
            'display_name': 'Patients Assigned',
            'category': MetricCategory.STAFF,
            'data_type': 'numeric',
            'description': 'Number of patients assigned to staff',
            'units': 'count',
            'aggregation_type': 'avg'
        },
        {
            'name': 'shift_hours',
            'display_name': 'Shift Hours',
            'category': MetricCategory.STAFF,
            'data_type': 'numeric',
            'description': 'Number of hours worked per shift',
            'units': 'hours',
            'aggregation_type': 'avg'
        },
        {
            'name': 'response_time_avg',
            'display_name': 'Average Response Time',
            'category': MetricCategory.STAFF,
            'data_type': 'numeric',
            'description': 'Average time to respond to patient calls',
            'units': 'minutes',
            'aggregation_type': 'avg'
        },
        {
            'name': 'treatment_hours',
            'display_name': 'Treatment Hours',
            'category': MetricCategory.STAFF,
            'data_type': 'numeric',
            'description': 'Hours spent on patient treatment',
            'units': 'hours',
            'aggregation_type': 'avg'
        }
    ]
    
    with get_db() as db:
        for metric in metrics:
            existing = db.query(MetricDefinition).filter_by(name=metric['name']).first()
            if not existing:
                db.add(MetricDefinition(**metric))
        db.commit()

def seed_floors():
    """Seed floor data"""
    floors = [
        {'floor_id': '1_east', 'name': '1 East', 'building': 'East', 'level': 1},
        {'floor_id': '2_east', 'name': '2 East', 'building': 'East', 'level': 2},
        {'floor_id': '3_east', 'name': '3 East', 'building': 'East', 'level': 3},
        {'floor_id': '4_east', 'name': '4 East', 'building': 'East', 'level': 4},
        {'floor_id': '1_west', 'name': '1 West', 'building': 'West', 'level': 1},
        {'floor_id': '2_west', 'name': '2 West', 'building': 'West', 'level': 2},
        {'floor_id': '3_west', 'name': '3 West', 'building': 'West', 'level': 3},
        {'floor_id': '4_west', 'name': '4 West', 'building': 'West', 'level': 4}
    ]
    
    with get_db() as db:
        for floor in floors:
            existing = db.query(Floor).filter_by(floor_id=floor['floor_id']).first()
            if not existing:
                db.add(Floor(**floor))
        db.commit()

def seed_rooms():
    """Seed initial room data"""
    rooms = [
        # 2nd Floor East Patient Rooms
        {'room_id': '227A', 'floor_id': '2_east', 'room_type': 'patient'},
        {'room_id': '228A', 'floor_id': '2_east', 'room_type': 'patient'},
        {'room_id': '229A', 'floor_id': '2_east', 'room_type': 'patient'},
        {'room_id': '230A', 'floor_id': '2_east', 'room_type': 'patient'},
        {'room_id': '231A', 'floor_id': '2_east', 'room_type': 'patient'},
        {'room_id': '232A', 'floor_id': '2_east', 'room_type': 'patient'},
        
        # 2nd Floor East Staff Rooms
        {'room_id': 'T2E-1', 'floor_id': '2_east', 'room_type': 'therapy'},
        {'room_id': 'T2E-2', 'floor_id': '2_east', 'room_type': 'therapy'},
        {'room_id': 'N2E-1', 'floor_id': '2_east', 'room_type': 'nurse'},
        
        # 3rd Floor West Patient Rooms
        {'room_id': '301A', 'floor_id': '3_west', 'room_type': 'patient'},
        {'room_id': '302A', 'floor_id': '3_west', 'room_type': 'patient'},
        
        # 4th Floor West Patient Rooms
        {'room_id': '401A', 'floor_id': '4_west', 'room_type': 'patient'},
        {'room_id': '402A', 'floor_id': '4_west', 'room_type': 'patient'},
        
        # 1st Floor East Staff Rooms
        {'room_id': 'T1E-1', 'floor_id': '1_east', 'room_type': 'therapy'},
        {'room_id': 'A1E-1', 'floor_id': '1_east', 'room_type': 'admin'},
        {'room_id': 'Q1E-1', 'floor_id': '1_east', 'room_type': 'quality'},
        
        # 1st Floor West Staff Rooms
        {'room_id': 'G1W-1', 'floor_id': '1_west', 'room_type': 'gym'},
        {'room_id': 'G1W-2', 'floor_id': '1_west', 'room_type': 'gym'},
        {'room_id': 'A1W-1', 'floor_id': '1_west', 'room_type': 'admin'},
        {'room_id': 'T1W-1', 'floor_id': '1_west', 'room_type': 'therapy'},
        {'room_id': 'N1W-1', 'floor_id': '1_west', 'room_type': 'nurse'},
        
        # 2nd Floor West Staff Rooms
        {'room_id': 'G2W-1', 'floor_id': '2_west', 'room_type': 'gym'},
        {'room_id': 'T2W-1', 'floor_id': '2_west', 'room_type': 'therapy'},
        {'room_id': 'N2W-1', 'floor_id': '2_west', 'room_type': 'nurse'},
        
        # 3rd Floor West Staff Rooms
        {'room_id': 'G3W-1', 'floor_id': '3_west', 'room_type': 'gym'},
        {'room_id': 'T3W-1', 'floor_id': '3_west', 'room_type': 'therapy'},
        {'room_id': 'N3W-1', 'floor_id': '3_west', 'room_type': 'nurse'},
        
        # 4th Floor West Staff Rooms
        {'room_id': 'G4W-1', 'floor_id': '4_west', 'room_type': 'gym'},
        {'room_id': 'T4W-1', 'floor_id': '4_west', 'room_type': 'therapy'},
        {'room_id': 'N4W-1', 'floor_id': '4_west', 'room_type': 'nurse'}
    ]
    
    with get_db() as db:
        for room_data in rooms:
            room = db.query(Room).filter_by(room_id=room_data['room_id']).first()
            if not room:
                room = Room(**room_data)
                db.add(room)
        db.commit()

def load_csv_data():
    """Load metrics data from CSV files"""
    with get_db() as db:
        # Load room metrics from the combined CSV file
        df = pd.read_csv('app/data/room_metrics.csv')
        
        # Process each row in the dataframe
        for _, row in df.iterrows():
            # Get the metric definition
            metric_def = db.query(MetricDefinition).filter_by(name=row['metric_name']).first()
            if not metric_def:
                print(f"Warning: Metric definition not found for {row['metric_name']}")
                continue
                
            # Create room metric
            metric = RoomMetric(
                room_id=row['room_id'],
                metric_id=metric_def.id,
                value=float(row['value']),
                timestamp=datetime.fromisoformat(row['timestamp']),
                is_calculated=False
            )
            db.add(metric)
            
            # Create floor metric (aggregated by floor)
            floor_metric = FloorMetric(
                floor_id=row['floor_id'],
                metric_id=metric_def.id,
                value=float(row['value']),
                timestamp=datetime.fromisoformat(row['timestamp']),
                is_calculated=True
            )
            db.add(floor_metric)
        
        db.commit()

def seed_all():
    """Run all seeding functions"""
    print("Seeding metric definitions...")
    seed_metric_definitions()
    
    print("Seeding floors...")
    seed_floors()
    
    print("Seeding rooms...")
    seed_rooms()
    
    print("Loading metrics data...")
    try:
        load_csv_data()
        print("Successfully loaded metrics data")
    except Exception as e:
        print(f"Error loading metrics data: {str(e)}")
        raise

if __name__ == '__main__':
    seed_all()
