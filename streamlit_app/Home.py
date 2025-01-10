import streamlit as st

st.set_page_config(
    page_title="Hospital Analytics Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page content
st.title("Hospital Analytics Dashboard 🏥")

st.markdown("""
Welcome to the Hospital Analytics Dashboard! This comprehensive platform provides multiple tools for hospital analytics and visualization:

### 1. Hospital 3D Metrics Visualization 🏢
- Interactive 3D visualization of hospital buildings
- Real-time metrics display across different floors
- Detailed floor and room-level analytics
- Customizable metrics and color schemes

### 2. Referral Map Analytics 🗺️
- Predictive modeling for patient referrals
- Scenario planning and analysis
- Geographic visualization of referral patterns
- Data-driven insights for referral optimization

### Getting Started
Select a tool from the sidebar to begin exploring the analytics capabilities.

### Need Help?
Each tool includes detailed documentation and help sections to guide you through the features.
""")

# Add some metrics or KPIs
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Active Floors", value="7")
    
with col2:
    st.metric(label="Total Rooms", value="245")
    
with col3:
    st.metric(label="Active Metrics", value="8")

# Add footer
st.markdown("---")
st.markdown("Built with Streamlit, React Three Fiber, and Python")
