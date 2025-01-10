import pandas as pd
import numpy as np

def test_coordinate_data():
    # Load the data
    data = pd.read_csv("model_df_clean_monthly.csv")
    
    # Test 1: Check if latitude and longitude columns exist
    assert 'hospital_latitude' in data.columns, "hospital_latitude column missing"
    assert 'hospital_longitude' in data.columns, "hospital_longitude column missing"
    
    # Test 2: Check for null values
    assert not data['hospital_latitude'].isnull().any(), "Found null values in latitude"
    assert not data['hospital_longitude'].isnull().any(), "Found null values in longitude"
    
    # Test 3: Check coordinate ranges for Western US
    assert data['hospital_latitude'].between(30, 50).all(), "Latitude values out of Western US range"
    assert data['hospital_longitude'].between(-125, -100).all(), "Longitude values out of Western US range"
    
    # Test 4: Check for non-numeric values
    assert pd.to_numeric(data['hospital_latitude'], errors='coerce').notnull().all(), "Non-numeric values in latitude"
    assert pd.to_numeric(data['hospital_longitude'], errors='coerce').notnull().all(), "Non-numeric values in longitude"
    
    print("All coordinate tests passed!")

if __name__ == "__main__":
    test_coordinate_data()
