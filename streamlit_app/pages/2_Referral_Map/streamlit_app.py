import os
import altair as alt
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SETTING PAGE CONFIG TO WIDE MODE AND ADDING A TITLE AND FAVICON
st.set_page_config(layout="wide", page_title="Western US Hospital Referrals", page_icon=":hospital:")

def test_data_validity(df, name="DataFrame"):
    """Test data validity and log results"""
    try:
        logger.info(f"Testing {name}...")
        logger.info(f"Shape: {df.shape}")
        logger.info(f"Columns: {df.columns.tolist()}")
        logger.info(f"Sample data:\n{df.head()}")
        return True
    except Exception as e:
        logger.error(f"Error testing {name}: {str(e)}")
        return False

# LOAD DATA ONCE
@st.cache_resource
def load_data():
    try:
        logger.info("Loading data...")
        data = pd.read_csv(
            "model_df_clean.csv",
            low_memory=False
        )
        
        # Test initial data
        test_data_validity(data, "raw_data")
        
        # Convert year_month from yyyymm string to datetime
        data['year_month'] = pd.to_datetime(data['year_month'].astype(str).str.zfill(6), format='%Y%m')
        
        # Convert coordinates to float and handle any errors
        for col in ['hospital,_latitude', 'hospital,_longitude']:
            data[col] = pd.to_numeric(data[col], errors='coerce')
            logger.info(f"{col} range: [{data[col].min()}, {data[col].max()}]")
        
        # Convert qualified_referrals to numeric
        data['qualified_referrals'] = pd.to_numeric(data['qualified_referrals'], errors='coerce')
        logger.info(f"Referrals range: [{data['qualified_referrals'].min()}, {data['qualified_referrals'].max()}]")
        
        # Drop any rows with invalid data
        original_len = len(data)
        data = data.dropna(subset=['hospital,_latitude', 'hospital,_longitude', 'qualified_referrals'])
        logger.info(f"Dropped {original_len - len(data)} rows with invalid data")
        
        return data
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        st.error("Error loading data. Please check the logs for details.")
        return pd.DataFrame()

# FILTER DATA FOR A SPECIFIC MONTH AND CALCULATE CUMULATIVE SUMS
@st.cache_data
def filter_data(df, selected_date):
    try:
        logger.info(f"Filtering data for date: {selected_date}")
        # Filter data up to the selected date
        mask = df["year_month"] <= selected_date
        filtered_df = df[mask].copy()
        
        logger.info(f"Filtered data shape: {filtered_df.shape}")
        
        # Group by hospital and sum the referrals up to this point
        cumulative_data = filtered_df.groupby([
            'hospital_name', 
            'hospital,_latitude', 
            'hospital,_longitude',
            'hospital_2-letter_state_abbreviation'
        ])['qualified_referrals'].sum().reset_index()
        
        logger.info(f"Cumulative data shape: {cumulative_data.shape}")
        
        # Normalize referrals for visualization
        if not cumulative_data.empty:
            min_refs = cumulative_data['qualified_referrals'].min()
            max_refs = cumulative_data['qualified_referrals'].max()
            logger.info(f"Referrals range: [{min_refs}, {max_refs}]")
            
            # Use square root scaling for better visualization
            cumulative_data['radius'] = np.sqrt(cumulative_data['qualified_referrals']) * 100
            
        return cumulative_data.to_dict('records')
    except Exception as e:
        logger.error(f"Error filtering data: {str(e)}")
        return []

# FUNCTION FOR HOSPITAL MAPS
def map(data, lat, lon, zoom):
    try:
        if not data:
            st.warning("No data available for the selected time period.")
            return
        
        logger.info(f"Creating map with {len(data)} points")
        logger.info(f"Sample point data: {data[0] if data else 'No data'}")
        
        st.pydeck_chart(
            pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                initial_view_state=pdk.ViewState(
                    latitude=lat,
                    longitude=lon,
                    zoom=zoom,
                    pitch=50,
                ),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=data,
                        get_position=["hospital,_longitude", "hospital,_latitude"],
                        get_radius="radius",
                        radius_min_pixels=5,
                        radius_max_pixels=50,
                        get_fill_color=[255, 140, 0, 200],
                        pickable=True,
                    ),
                ],
                tooltip={
                    "html": "<b>Hospital:</b> {hospital_name}<br/>"
                           "<b>Total Referrals:</b> {qualified_referrals}<br/>"
                           "<b>State:</b> {hospital_2-letter_state_abbreviation}",
                }
            )
        )
    except Exception as e:
        logger.error(f"Error creating map: {str(e)}")
        st.error("Error creating map. Please check the logs for details.")

# CALCULATE MIDPOINT FOR GIVEN SET OF DATA
@st.cache_data
def mpoint(data):
    try:
        if not data:
            return (39.8283, -98.5795)  # Default to center of US if no data
        
        lat = np.mean([d['hospital,_latitude'] for d in data])
        lon = np.mean([d['hospital,_longitude'] for d in data])
        logger.info(f"Calculated midpoint: ({lat}, {lon})")
        return (lat, lon)
    except Exception as e:
        logger.error(f"Error calculating midpoint: {str(e)}")
        return (39.8283, -98.5795)

# Debug function to show data statistics
def show_debug_info(data, filtered_data):
    with st.expander("Debug Information"):
        try:
            st.write("Original Data Shape:", len(data))
            st.write("Filtered Data Shape:", len(filtered_data))
            if filtered_data:
                sample_hospital = filtered_data[0]
                st.write("Sample Hospital Data:")
                st.json(sample_hospital)
                
                referrals = [d['qualified_referrals'] for d in filtered_data]
                st.write("Referral Statistics:")
                st.write({
                    "Min": min(referrals),
                    "Max": max(referrals),
                    "Mean": np.mean(referrals),
                    "Median": np.median(referrals),
                    "Total Points": len(referrals)
                })
                
                # Add coordinate ranges
                st.write("Coordinate Ranges:")
                st.write({
                    "Latitude": [min(d['hospital,_latitude'] for d in filtered_data),
                               max(d['hospital,_latitude'] for d in filtered_data)],
                    "Longitude": [min(d['hospital,_longitude'] for d in filtered_data),
                                max(d['hospital,_longitude'] for d in filtered_data)]
                })
        except Exception as e:
            st.error(f"Error in debug info: {str(e)}")

# STREAMLIT APP LAYOUT
data = load_data()

if data.empty:
    st.error("No data available. Please check the data file and logs.")
    st.stop()

# LAYING OUT THE TOP SECTION OF THE APP
row1_1, row1_2 = st.columns((2, 3))

with row1_1:
    st.title("Western US Hospital Referrals")
    
    # Create a list of available dates for the slider
    available_dates = sorted(data["year_month"].unique())
    date_to_index = {date: idx for idx, date in enumerate(available_dates)}
    index_to_date = {idx: date for idx, date in enumerate(available_dates)}
    
    # Create a slider for month selection
    selected_index = st.slider(
        "Select Month",
        min_value=0,
        max_value=len(available_dates)-1,
        value=len(available_dates)-1,
        format="",
    )
    
    # Convert the index back to a datetime
    selected_date = index_to_date[selected_index]
    
    # Display the selected date in a more readable format
    st.write(f"Selected: {selected_date.strftime('%B %Y')}")
    st.write("(Showing cumulative referrals from 2020 to selected date)")

with row1_2:
    st.write(
        """
    ##
    Examining how hospital referrals accumulate over time across the Western United States.
    Move the slider to see how referral patterns develop from January 2020 onwards.
    The size of each point represents the total number of referrals up to the selected date.
    """
    )

# LAYING OUT THE MIDDLE SECTION OF THE APP WITH THE MAPS
row2_1, row2_2, row2_3, row2_4 = st.columns((2, 1, 1, 1))

# Filter for Western states
western_states = ['WA', 'OR', 'CA', 'ID', 'NV', 'MT', 'WY', 'UT', 'AZ', 'CO', 'NM']
western_data = data[data['hospital_2-letter_state_abbreviation'].isin(western_states)]

# Get cumulative data up to selected date
filtered_data = filter_data(western_data, selected_date)

# Show debug information
show_debug_info(western_data, filtered_data)

# Get the top 3 states by cumulative referral volume
state_totals = pd.DataFrame(filtered_data).groupby('hospital_2-letter_state_abbreviation')['qualified_referrals'].sum()
top_states = state_totals.sort_values(ascending=False).head(3)

# Calculate the center of the Western US based on the actual data
western_us_midpoint = mpoint(filtered_data)

with row2_1:
    st.write(f"""**Western United States - Cumulative through {selected_date.strftime('%B %Y')}**""")
    map(filtered_data, western_us_midpoint[0], western_us_midpoint[1], 4)

# Show details for top 3 states
for i, (state, total) in enumerate(top_states.items()):
    state_data = [d for d in filtered_data if d['hospital_2-letter_state_abbreviation'] == state]
    if state_data:
        state_midpoint = mpoint(state_data)
        
        with eval(f"row2_{i+2}"):
            st.write(f"**{state} Hospitals**")
            st.write(f"Total Referrals: {int(total):,}")
            map(state_data, state_midpoint[0], state_midpoint[1], 5)

# CALCULATING DATA FOR THE HISTOGRAM
st.write(
    f"""**Monthly Referral Distribution**"""
)

# Create histogram data
def histdata(df, selected_date):
    try:
        # Filter data for the selected month
        month_data = df[df['year_month'] == selected_date].copy()
        
        # Create histogram of referrals by state
        hist_data = month_data.groupby('hospital_2-letter_state_abbreviation')['qualified_referrals'].sum()
        
        # Convert to DataFrame with reset index
        hist_df = pd.DataFrame({
            'state': hist_data.index,
            'referrals': hist_data.values
        })
        
        return hist_df
    except Exception as e:
        logger.error(f"Error creating histogram data: {str(e)}")
        return pd.DataFrame()

# Get histogram data
hist_data = histdata(western_data, selected_date)

# Create area chart
if not hist_data.empty:
    chart = alt.Chart(hist_data).mark_area(
        interpolate='step-after',
        line=True
    ).encode(
        x=alt.X('state:N', title='State'),
        y=alt.Y('referrals:Q', title='Referrals'),
        tooltip=['state', 'referrals']
    ).configure_mark(
        opacity=0.2,
        color='red'
    ).properties(
        height=400
    )

    st.altair_chart(chart, use_container_width=True)
