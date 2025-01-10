import os
import altair as alt
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
import sys
from Login import check_password

# Initialize session state
if 'debug_mode' not in st.session_state:
    st.session_state['debug_mode'] = False
if 'show_arc_lines' not in st.session_state:
    st.session_state['show_arc_lines'] = False

# SETTING PAGE CONFIG TO WIDE MODE AND ADDING A TITLE AND FAVICON
st.set_page_config(layout="wide", page_title="Western US Hospital Referrals", page_icon=":hospital:")

# Check authentication
if not check_password():
    st.stop()  # Do not continue with the rest of the app

# LOAD DATA
@st.cache_data
def load_data():
    """
    Load and preprocess the hospital referral data
    """
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    df = pd.read_csv(os.path.join(data_dir, "model_df_clean_tall.csv"))
    df['year_month_dt'] = pd.to_datetime(df['year_month'].astype(str), format='%Y%m')
    
    if st.session_state['debug_mode']:
        st.sidebar.write("Data Loading Debug:")
        st.sidebar.write(f"Total records: {len(df)}")
        st.sidebar.write(f"Date range: {df['year_month_dt'].min()} to {df['year_month_dt'].max()}")
        st.sidebar.write(f"Unique hospitals: {df['hospital_name'].nunique()}")
    
    return df

# FUNCTION FOR HOSPITAL MAPS
def map(data, lat, lon, zoom, key_suffix=""):
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

# FILTER AND AGGREGATE DATA FOR CUMULATIVE REFERRALS
@st.cache_data
def get_cumulative_data(df, start_date, end_date):
    """
    Calculate cumulative referrals for each hospital within the specified date range.
    
    Args:
        df (pd.DataFrame): Input dataframe with hospital referral data
        start_date: Start date for the range (can be datetime)
        end_date: End date for the range (can be datetime)
    
    Returns:
        pd.DataFrame: Aggregated referral data for each hospital
    """
    if st.session_state['debug_mode']:
        st.sidebar.write("Debug Information:")
        st.sidebar.write(f"Input date range: {start_date} to {end_date}")
    
    # Ensure we have the datetime column
    if 'year_month_dt' not in df.columns:
        df = df.copy()
        df['year_month_dt'] = pd.to_datetime(df['year_month'].astype(str), format='%Y%m')
    
    # Filter data for the date range
    mask = (df["year_month_dt"] >= start_date) & (df["year_month_dt"] <= end_date)
    filtered_df = df[mask].copy()
    
    if st.session_state['debug_mode']:
        st.sidebar.write(f"Filtered records: {len(filtered_df)}")
    
    # Group by hospital and sum referrals
    result = filtered_df.groupby([
        'hospital_name',
        'hospital_state',
        'hospital_latitude',
        'hospital_longitude'
    ])['qualified_referral'].sum().reset_index()
    
    # Debug aggregation results
    if st.session_state['debug_mode']:
        if len(result) > 0:
            st.sidebar.write(f"Max referrals for a hospital: {result['qualified_referral'].max()}")
            st.sidebar.write(f"Total referrals: {result['qualified_referral'].sum()}")
    
    return result

def test_get_cumulative_data():
    """
    Test function for get_cumulative_data
    """
    # Create test data
    test_data = pd.DataFrame({
        'year_month': [202001, 202002, 202003, 202004, 202005, 202006],
        'hospital_name': ['Test Hospital'] * 6,
        'hospital_state': ['CO'] * 6,
        'hospital_latitude': [40.0] * 6,
        'hospital_longitude': [-105.0] * 6,
        'qualified_referral': [10] * 6  # 10 referrals per month
    })
    test_data['year_month_dt'] = pd.to_datetime(test_data['year_month'].astype(str), format='%Y%m')
    
    # Test case 1: Full range
    start_date = pd.to_datetime('2020-01-01')
    end_date = pd.to_datetime('2020-06-30')
    result = get_cumulative_data(test_data, start_date, end_date)
    assert len(result) == 1, "Should have one hospital"
    assert result['qualified_referral'].iloc[0] == 60, "Should have 60 total referrals"
    
    # Test case 2: Partial range
    start_date = pd.to_datetime('2020-03-01')
    end_date = pd.to_datetime('2020-05-31')
    result = get_cumulative_data(test_data, start_date, end_date)
    assert result['qualified_referral'].iloc[0] == 30, "Should have 30 referrals for 3 months"
    
    print("All tests passed!")

# STREAMLIT APP LAYOUT
data = load_data()

# Add toggle button for arc lines in the sidebar
st.sidebar.write("---")
st.sidebar.write("### Visualization Options")
if st.sidebar.checkbox("Show Connections to Englewood, CO", value=st.session_state['show_arc_lines']):
    st.session_state['show_arc_lines'] = True
else:
    st.session_state['show_arc_lines'] = False

# Date range selection
min_date = data['year_month_dt'].min()
max_date = data['year_month_dt'].max()

with st.sidebar:
    st.session_state['debug_mode'] = st.checkbox(
        "Enable Debug Mode",
        value=st.session_state['debug_mode'],
        key="debug_mode_toggle"
    )
    
    if st.session_state['debug_mode'] and st.button("Run Tests", key="run_tests_button"):
        test_get_cumulative_data()

    st.header("Date Range")
    date_range = st.slider(
        "Select time period",
        min_value=min_date.date(),
        max_value=max_date.date(),
        value=(min_date.date(), max_date.date()),
        format="YYYY-MM"
    )
    start_date, end_date = date_range
    
    # Convert back to datetime for filtering
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    if st.session_state['debug_mode']:
        st.write("Date Selection Debug:")
        st.write(f"Selected start: {start_date}")
        st.write(f"Selected end: {end_date}")

# Get cumulative data for selected date range
cumulative_data = get_cumulative_data(data, start_date, end_date)

if st.session_state['debug_mode']:
    st.sidebar.write("Cumulative Data Debug:")
    st.sidebar.write(f"Total hospitals: {len(cumulative_data)}")
    st.sidebar.write(f"Total referrals: {cumulative_data['qualified_referral'].sum():,}")

# Define all western states
western_states = [
    'WA', 'OR', 'CA', 'ID', 'NV', 'MT', 'WY', 'UT', 'AZ', 'CO', 'NM',
    'ND', 'SD', 'NE', 'KS', 'OK', 'TX', 'MN', 'IA', 'MO', 'AR', 'LA'
]

# Add state selection to sidebar
st.sidebar.write("### State Selection")
selected_states = st.sidebar.multiselect(
    "Select States to Display",
    options=western_states,
    default=western_states,
    help="Choose which states to display on the map",
    key="state_selection"
)

# Filter cumulative data for selected states
cumulative_data = cumulative_data[cumulative_data['hospital_state'].isin(selected_states)]

# Add data validation messages after state selection
st.sidebar.write("### Data Validation")
coord_check = data[['hospital_latitude', 'hospital_longitude']].notna().all().all()
range_check = (
    data['hospital_latitude'].between(30, 50).all() and 
    data['hospital_longitude'].between(-125, -100).all()
)

if coord_check:
    st.sidebar.success(" All coordinates present")
else:
    st.sidebar.error(" Missing coordinates detected")
    
if range_check:
    st.sidebar.success(" All coordinates within Western US range")
else:
    st.sidebar.error(" Some coordinates outside Western US range")

# LAYING OUT THE TOP SECTION OF THE APP
row1_1, row1_2 = st.columns((2, 3))

with row1_1:
    st.title("Western US Hospital Referrals")
    
with row1_2:
    st.write(
        """
    ##
    Examining cumulative hospital referrals across the Western United States.
    Move the slider to see how referrals accumulate over time. The visualization shows the total referrals from January 2020 up to the selected date.
    """
    )

# LAYING OUT THE MIDDLE SECTION OF THE APP WITH THE MAPS
row2_1, row2_2, row2_3 = st.columns((2, 1, 1))

# No need to filter western_data separately since cumulative_data is already filtered
western_data = cumulative_data

# SETTING THE ZOOM LOCATIONS FOR DIFFERENT REGIONS
western_us_midpoint = [39.7392, -104.9903]  # Denver, CO as center

# Get the top 2 states by cumulative referral volume
top_states = (cumulative_data.groupby('hospital_state')
              ['qualified_referral'].sum()
              .sort_values(ascending=False)
              .head(2))

# Display total referrals for the period
total_referrals = cumulative_data['qualified_referral'].sum()
st.write(f"### Total Referrals: {total_referrals:,.0f}")

with row2_1:
    st.write(f"""**Western United States - Cumulative from {start_date} to {end_date}**""")
    map(cumulative_data, western_us_midpoint[0], western_us_midpoint[1], 4, key_suffix="western_us")

# Create dropdowns for state selection
state_options = sorted(western_data['hospital_state'].unique())

with row2_2:
    selected_state_1 = st.selectbox("Select State 1", state_options, 
                                  index=state_options.index(top_states.index[0]) if top_states.index[0] in state_options else 0)
    state_data = cumulative_data[cumulative_data['hospital_state'] == selected_state_1]
    state_midpoint = [np.average(state_data['hospital_latitude']), np.average(state_data['hospital_longitude'])]
    st.write(f"### {selected_state_1}")
    map(state_data, state_midpoint[0], state_midpoint[1], 5, key_suffix=f"state_{selected_state_1}")

with row2_3:
    selected_state_2 = st.selectbox("Select State 2", state_options, 
                                  index=state_options.index(top_states.index[1]) if top_states.index[1] in state_options else 0)
    state_data = cumulative_data[cumulative_data['hospital_state'] == selected_state_2]
    state_midpoint = [np.average(state_data['hospital_latitude']), np.average(state_data['hospital_longitude'])]
    st.write(f"### {selected_state_2}")
    map(state_data, state_midpoint[0], state_midpoint[1], 5, key_suffix=f"state_{selected_state_2}")

# CALCULATING DATA FOR THE TIME SERIES
st.write(
    f"""**Cumulative Referral Trends by State**"""
)

# Create time series data
time_series_data = []
current_date = min_date

while current_date <= max_date:
    if st.session_state['debug_mode']:
        st.sidebar.write(f"Processing time series for: {current_date}")
    
    # Get data for this month from the original data, not western_data
    month_data = get_cumulative_data(data[data['hospital_state'].isin(selected_states)], min_date, current_date)
    state_totals = month_data.groupby('hospital_state')['qualified_referral'].sum().reset_index()
    state_totals['year_month_dt'] = current_date
    time_series_data.append(state_totals)
    
    # Increment to next month
    current_date = current_date + pd.DateOffset(months=1)

# Combine all time series data
chart_data = pd.concat(time_series_data) if time_series_data else pd.DataFrame()

if st.session_state['debug_mode']:
    st.sidebar.write("Time Series Debug:")
    st.sidebar.write(f"Total data points: {len(chart_data)}")
    st.sidebar.write(f"Date range: {chart_data['year_month_dt'].min()} to {chart_data['year_month_dt'].max()}")

# Create time series chart
chart = alt.Chart(chart_data).mark_line().encode(
    x=alt.X('year_month_dt:T', title='Date', axis=alt.Axis(format='%Y-%m')),
    y=alt.Y('qualified_referral:Q', title='Cumulative Qualified Referrals'),
    color=alt.Color('hospital_state:N', title='State'),
    tooltip=[
        alt.Tooltip('year_month_dt:T', title='Date', format='%Y-%m'),
        alt.Tooltip('qualified_referral:Q', title='Referrals'),
        alt.Tooltip('hospital_state:N', title='State')
    ]
).properties(
    height=400
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_legend(
    titleFontSize=12,
    labelFontSize=11
)

st.altair_chart(chart, use_container_width=True)

# CALCULATE MIDPOINT FOR GIVEN SET OF DATA
@st.cache_data
def mpoint(lat, lon):
    return (np.average(lat), np.average(lon))
