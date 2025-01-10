import os
import pandas as pd
import pydeck as pdk
import streamlit as st
import numpy as np

@st.cache_data
def load_data():
    """
    Load and preprocess the hospital referral data
    """
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    df = pd.read_csv(os.path.join(data_dir, "model_df_clean_tall.csv"))
    df['year_month_dt'] = pd.to_datetime(df['year_month'].astype(str), format='%Y%m')
    
    if st.session_state.get('debug_mode', False):
        st.sidebar.write("Data Loading Debug:")
        st.sidebar.write(f"Total records: {len(df)}")
        st.sidebar.write(f"Date range: {df['year_month_dt'].min()} to {df['year_month_dt'].max()}")
        st.sidebar.write(f"Unique hospitals: {df['hospital_name'].nunique()}")
    
    return df

def map(data, lat, lon, zoom, key_suffix=""):
    """Create an interactive map visualization using deck.gl"""
    # Calculate dynamic radius based on zoom level
    hex_radius = max(9000, 90000/ (zoom** 2))  # Base hex radius
    scatter_radius = max(100, 1000 / (zoom))  # Smaller points at higher zoom levels
    
    # Dynamic elevation scaling based on data
    max_referrals = data['qualified_referral'].max()
    elevation_scale = max(200, min(1000, max_referrals / 10))  # Scale elevation based on data range

    # Create color array for each data point
    colors = []
    for referral in data['qualified_referral']:
        normalized = referral / max_referrals if max_referrals > 0 else 0
        
        # Color gradient: yellow (low) -> orange (medium) -> red (high)
        if normalized < 0.33:
            # Yellow to Orange
            r = 255
            g = int(255 - (normalized * 3 * 90))  # Gradually reduce green
            b = 0
        else:
            # Orange to Red
            r = 255
            g = int(165 - ((normalized - 0.33) * 1.5 * 165))  # Further reduce green
            b = 0
        
        colors.append([r, g, b, 140])
    
    # Add colors to the dataframe
    data = data.copy()
    data['color'] = colors

    # Define base layers
    layers = [
        pdk.Layer(
            "ColumnLayer",
            data=data,
            get_position=["hospital_longitude", "hospital_latitude"],
            get_elevation="qualified_referral",
            elevation_scale=elevation_scale * 5,
            radius=hex_radius,
            pickable=True,
            extruded=True,
            auto_highlight=True,
            get_fill_color="color",
            coverage=0.8,
            material=True,
            disk_resolution=6,
        ),
        # Add a ScatterplotLayer for individual hospitals
        pdk.Layer(
            "ScatterplotLayer",
            data=data,
            get_position=["hospital_longitude", "hospital_latitude"],
            get_radius=scatter_radius,
            get_fill_color=[255, 140, 0],
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True,
        ),
    ]

    # Add arc layers if toggle is on
    if st.session_state['show_arc_lines']:
        layers.extend([
            # Add ArcLayer to show connections to Englewood
            pdk.Layer(
                "ArcLayer",
                data=data,
                get_source_position=["hospital_longitude", "hospital_latitude"],
                get_target_position=[-104.9878, 39.6478],  # Englewood, CO coordinates
                get_width=2,
                get_height={"type": "identity", "value": 1},
                get_tilt={"type": "identity", "value": 0},
                get_source_color=[255, 165, 0, 80],  # Orange with transparency
                get_target_color=[255, 0, 0, 80],  # Red with transparency
                pickable=True,
            ),
            # Add a point for Englewood, CO
            pdk.Layer(
                "ScatterplotLayer",
                data=[{
                    "longitude": -104.9878,
                    "latitude": 39.6478,
                    "name": "Englewood, CO"
                }],
                get_position=["longitude", "latitude"],
                get_radius=scatter_radius * 2,
                get_fill_color=[255, 0, 0],  # Red
                pickable=True,
                opacity=0.8,
                stroked=True,
                filled=True,
            ),
        ])

    st.write(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=lat,
                longitude=lon,
                zoom=zoom,
                pitch=45,
                bearing=0,
            ),
            layers=layers,
            tooltip={
                "html": """
                    <b>Hospital:</b> {hospital_name}<br/>
                    <b>State:</b> {hospital_2-letter_state_abbreviation}<br/>
                    <b>Referrals:</b> {qualified_referral}
                    <br/><br/>
                    <b>Aggregated Data (if available):</b><br/>
                    <b>Points in Hex:</b> {points}<br/>
                    <b>Total Referrals:</b> {colorValue}
                """,
                "style": {
                    "backgroundColor": "steelblue",
                    "color": "white"
                }
            }
        )
    )

    # Add a table below the map showing hospital details
    if st.checkbox("Show Hospital Details Table", value=False, key=f"show_details_table_{key_suffix}"):
        st.dataframe(
            data[['hospital_name', 'hospital_state', 'qualified_referral']]
            .sort_values('qualified_referral', ascending=False),
            hide_index=True,
            use_container_width=True
        )

@st.cache_data
def get_cumulative_data(df, start_date, end_date):
    """
    Calculate cumulative referrals for each hospital within the specified date range.
    """
    if st.session_state.get('debug_mode', False):
        st.sidebar.write("Debug Information:")
        st.sidebar.write(f"Input date range: {start_date} to {end_date}")
    
    # Ensure we have the datetime column
    if 'year_month_dt' not in df.columns:
        df = df.copy()
        df['year_month_dt'] = pd.to_datetime(df['year_month'].astype(str), format='%Y%m')
    
    # Filter data for the date range
    mask = (df["year_month_dt"] >= start_date) & (df["year_month_dt"] <= end_date)
    filtered_df = df[mask].copy()
    
    # Group by hospital and calculate metrics
    hospital_metrics = filtered_df.groupby([
        'hospital_name', 'hospital_state', 'hospital_latitude', 'hospital_longitude'
    ]).agg({
        'qualified_referral': 'sum',
        'year_month': 'count'
    }).reset_index()
    
    hospital_metrics.rename(columns={'year_month': 'months_active'}, inplace=True)
    
    if st.session_state.get('debug_mode', False):
        st.sidebar.write(f"Hospitals after filtering: {len(hospital_metrics)}")
        st.sidebar.write(f"Total referrals: {hospital_metrics['qualified_referral'].sum()}")
    
    return hospital_metrics
