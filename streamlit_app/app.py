import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# Configure the page
st.set_page_config(
    page_title="Hospital Metrics 3D Visualization",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS to handle the iframe
st.markdown("""
    <style>
        .stApp {
            margin: 0;
            padding: 0;
        }
        iframe {
            width: 100%;
            height: 100vh;
            border: none;
            margin: 0;
            padding: 0;
        }
        .sidebar .sidebar-content {
            width: 300px;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar controls
st.sidebar.title("Hospital Metrics Controls")

# Date range selector
st.sidebar.subheader("Date Range")
today = datetime.now()
start_date = st.sidebar.date_input(
    "Start Date",
    today - timedelta(days=30)
)
end_date = st.sidebar.date_input(
    "End Date",
    today
)

# Metric selector
metric_options = {
    "Patient Satisfaction": "patient_satisfaction",
    "Staff Retention": "staff_retention",
    "Fall Risk Average": "fall_risk_average",
    "Nurse Response Time": "nurse_response_time_avg",
    "Therapy Completion": "therapy_completion_rate",
    "Equipment Utilization": "equipment_utilization",
    "Department Efficiency": "department_efficiency",
    "Space Utilization": "space_utilization"
}
selected_metric = st.sidebar.selectbox(
    "Select Metric",
    list(metric_options.keys())
)

# Category filter
categories = ["Patient Metrics", "Staff Metrics", "Room Metrics"]
selected_categories = st.sidebar.multiselect(
    "Filter by Category",
    categories,
    default=["Patient Metrics"]
)

# Color scheme selector
color_scheme = st.sidebar.color_picker(
    "Select Heatmap Color",
    "#007dc3"
)

# Main content
st.title("Hospital Metrics 3D Visualization")

# Embed the React app in an iframe
# Note: Update the URL to match your React app's deployment URL
react_app_url = "http://localhost:5173"
st.markdown(f'<iframe src="{react_app_url}"></iframe>', unsafe_allow_html=True)

# Add communication between Streamlit and React app
st.markdown("""
    <script>
        // Listen for messages from React app
        window.addEventListener('message', function(event) {
            if (event.data.type === 'metrics_update') {
                // Handle metrics updates
                console.log('Received metrics update:', event.data);
            }
        });

        // Send configuration to React app
        function sendConfig() {
            const iframe = document.querySelector('iframe');
            if (iframe && iframe.contentWindow) {
                iframe.contentWindow.postMessage({
                    type: 'config_update',
                    config: {
                        startDate: '%s',
                        endDate: '%s',
                        metric: '%s',
                        categories: %s,
                        colorScheme: '%s'
                    }
                }, '*');
            }
        }

        // Send initial config
        setTimeout(sendConfig, 1000);
    </script>
""" % (
    start_date.isoformat(),
    end_date.isoformat(),
    metric_options[selected_metric],
    str(selected_categories),
    color_scheme
), unsafe_allow_html=True)

# Add some helpful information
with st.expander("About this visualization"):
    st.write("""
    This 3D visualization shows hospital metrics across different floors and rooms.
    Use the controls in the sidebar to:
    - Select date range for the data
    - Choose which metric to display
    - Filter by metric categories
    - Customize the heatmap color
    
    Navigate the 3D view:
    - Click and drag to rotate
    - Scroll to zoom
    - Right-click and drag to pan
    - Click on floors for detailed views
    """)

# Add a footer
st.markdown("---")
st.markdown("Built with Streamlit & React Three Fiber")
