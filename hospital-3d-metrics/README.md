# Hospital 3D Metrics Visualization

A 3D visualization dashboard for hospital metrics using React Three Fiber and FastAPI. This project provides an interactive 3D representation of hospital buildings with real-time metrics visualization.

## Project Overview

This application visualizes hospital metrics across different floors and buildings in a 3D environment, allowing for intuitive data exploration and comparison. The visualization includes:
- Two main buildings (East and West)
- Connected bridges
- Garden area
- Interactive floor selection
- Real-time metrics display
- Heat map visualization of metrics

### Current Features
- 3D visualization of hospital buildings
- Interactive floor selection with hover and click states
- Real-time metrics data display
- Building layout:
  - West Building: 4 floors (1 West - 4 West)
  - East Building: 3 floors (1 East - 3 East)
  - Connected bridges at specific floors
  - Adjacent garden area
- Metrics visualization:
  - Patient satisfaction
  - Staff retention
  - Fall risk
- Controls panel for metric selection
- Detailed metrics display for selected floors

## Project Structure
```
hospital-3d-metrics/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Building.tsx
│   │   │   ├── Bridge.tsx
│   │   │   ├── Garden.tsx
│   │   │   ├── HospitalView.tsx
│   │   │   ├── Controls.tsx
│   │   │   └── MetricsPanel.tsx
│   │   ├── utils/
│   │   │   └── colorScales.ts
│   │   ├── hooks/
│   │   │   └── useMetrics.ts
│   │   └── index.css
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── routes.py
│   ├── data/
│   │   └── initial_metrics.csv
│   └── requirements.txt
```

## Setup Instructions

### Backend Setup
1. Create and activate a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```
The backend will run on http://localhost:8000

### Frontend Setup
1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Install required packages:
```bash
npm install d3
npm install --save-dev @types/d3
```

3. Set up shadcn/ui:
```bash
npm i -D @shadcn/ui
npx shadcn@latest init
```
Select the following options:
- Style: New York
- Base color: Slate
- CSS variables: Yes

4. Add required components:
```bash
npx shadcn@latest add card
npx shadcn@latest add select
npx shadcn@latest add slider
```

5. Start the development server:
```bash
npm run dev
```
The frontend will run on http://localhost:5173

## Technologies Used
- Frontend:
  - React
  - TypeScript
  - Three.js / React Three Fiber
  - shadcn/ui
  - Tailwind CSS
  - D3.js (for color scales)
- Backend:
  - Python
  - FastAPI
  - Pandas
  - Pydantic

## Future Development
Planned features and improvements:
- [ ] Implement date range filtering
- [ ] Add metric comparison features
- [ ] Add animation transitions for metric changes
- [ ] Implement "explode view" feature
- [ ] Add 2D floor plan view option
- [ ] Enhance heat map visualization
- [ ] Add more metrics and data points
- [ ] Implement real-time data updates
- [ ] Add user authentication
- [ ] Enhance mobile responsiveness

## API Documentation
The backend provides the following endpoints:

### GET /api/metrics
Retrieves metrics data with optional filtering
- Query Parameters:
  - floor (optional): Filter by floor name
  - metric_name (optional): Filter by metric type

### POST /api/metrics/filter
Filters metrics based on provided criteria
- Request Body:
  - metric_name (optional)
  - start_date (optional)
  - end_date (optional)

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
[MIT License](LICENSE)