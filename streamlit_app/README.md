# Hospital Metrics 3D Visualization - Streamlit App

This Streamlit application serves as a wrapper for the Hospital Metrics 3D visualization, providing an integrated interface with additional controls and features.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the React development server:
```bash
cd ../hospital-3d-metrics/frontend
npm run dev
```

3. Run the Streamlit app:
```bash
streamlit run app.py
```

## Features

- Date range selection for temporal data analysis
- Metric selection and filtering
- Category-based filtering
- Custom color scheme selection
- Responsive 3D visualization
- Detailed floor and room-level metrics

## Architecture

The application consists of two main components:

1. Streamlit Frontend:
   - Provides the user interface and controls
   - Handles date range and metric selection
   - Manages communication with the React app

2. React 3D Visualization:
   - Renders the 3D hospital model
   - Handles user interaction with the 3D scene
   - Displays metrics using color-coded heatmaps

## Communication

The Streamlit app communicates with the React application through postMessage:

1. Configuration updates are sent from Streamlit to React
2. Metric updates and user interactions are sent from React to Streamlit

## Development

To modify the application:

1. Streamlit UI changes: Edit `app.py`
2. React visualization changes: Edit files in the `../hospital-3d-metrics/frontend/src` directory
3. Update the communication protocol in both applications if adding new features

## Notes

- The React app must be running on port 5173 for the iframe embedding to work
- Cross-origin communication must be properly configured in both applications
- Ensure all metric data is properly formatted before visualization
