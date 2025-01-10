import streamlit as st
import os
import sys
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
from datetime import datetime, timedelta

# Add the referral map directory to the Python path
referral_map_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '2_Referral_Map'))
if referral_map_path not in sys.path:
    sys.path.append(referral_map_path)

# Import from the referral map modules
from models import ReferralPredictor, FeatureEngineer
from referral_utils import load_data, map, get_cumulative_data

# Configure the page
st.set_page_config(
    page_title="Western US Hospital Referrals",
    page_icon="🏥",
    layout="wide"
)

# Initialize session states from the original app
if 'debug_mode' not in st.session_state:
    st.session_state['debug_mode'] = False
if 'show_arc_lines' not in st.session_state:
    st.session_state['show_arc_lines'] = False
if 'model' not in st.session_state:
    st.session_state['model'] = None
if 'model_trained' not in st.session_state:
    st.session_state['model_trained'] = False

try:
    # Load the data
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
        st.write(f"""**Western United States - Cumulative from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}**""")
        map(cumulative_data, western_us_midpoint[0], western_us_midpoint[1], 4, "western_us")

    # Create dropdowns for state selection
    state_options = sorted(cumulative_data['hospital_state'].unique())

    with row2_2:
        selected_state_1 = st.selectbox("Select State 1", state_options, 
                                    index=state_options.index(top_states.index[0]) if top_states.index[0] in state_options else 0)
        state_data = cumulative_data[cumulative_data['hospital_state'] == selected_state_1]
        state_midpoint = [np.average(state_data['hospital_latitude']), np.average(state_data['hospital_longitude'])]
        st.write(f"### {selected_state_1}")
        map(state_data, state_midpoint[0], state_midpoint[1], 5, f"state_{selected_state_1}")

    with row2_3:
        selected_state_2 = st.selectbox("Select State 2", state_options, 
                                    index=state_options.index(top_states.index[1]) if top_states.index[1] in state_options else 0)
        state_data = cumulative_data[cumulative_data['hospital_state'] == selected_state_2]
        state_midpoint = [np.average(state_data['hospital_latitude']), np.average(state_data['hospital_longitude'])]
        st.write(f"### {selected_state_2}")
        map(state_data, state_midpoint[0], state_midpoint[1], 5, f"state_{selected_state_2}")

    # Add tabs for additional analysis
    tab1, tab2 = st.tabs(["Predictive Model", "Scenario Planning"])

    with tab1:
        # Import and run the Predictive Model page
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "predictive_model",
            os.path.join(referral_map_path, "pages", "1_Predictive_Model.py")
        )
        predictive_model = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(predictive_model)
        predictive_model.run()

    with tab2:
        # Import and run the Scenario Planning page
        spec = importlib.util.spec_from_file_location(
            "scenario_planning",
            os.path.join(referral_map_path, "pages", "2_Scenario_Planning.py")
        )
        scenario_planning = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scenario_planning)
        scenario_planning.run()

except Exception as e:
    st.error(f"Error: {str(e)}")
    st.write("Debug info:")
    st.write(f"Referral map path: {referral_map_path}")
    st.write(f"Python path: {sys.path}")

# Add footer
st.markdown("---")
st.markdown("Built with Streamlit & Python")
