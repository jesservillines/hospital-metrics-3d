# Referral Map

A machine learning-powered tool for healthcare referral prediction and scenario planning.

## Overview

This application helps healthcare organizations analyze and predict patient referral patterns. It uses advanced machine learning techniques to model referral behavior and allows users to explore "what-if" scenarios such as adding new facilities or competitors.

## Features

### 1. Predictive Model
- Machine learning model built with CatBoost
- Organized feature selection interface with categories:
  - Basic Features (core metrics)
  - Hospital Info (facility characteristics)
  - Relationship Strength (referral relationships)
  - Distance Features (geographic factors)
  - Seasonal Features (temporal patterns)
  - Census Features (demographic indicators)
- Interactive feature selection with:
  - Search/filter functionality
  - Group-level controls
  - Feature descriptions
- Advanced feature engineering:
  - Seasonality detection
  - Time lag analysis

### 2. Scenario Planning
- Interactive scenario creation for:
  - New facilities
  - Competitor analysis
  - Trauma center additions
- Impact analysis showing:
  - State-level effects
  - Market-wide changes
  - Facility-specific predictions

### 3. Market Analysis
- Comprehensive market insights:
  - Current referral patterns
  - Competitor presence
  - Market saturation levels
  - Geographic distribution

## Technical Details

### Model Architecture
- **Framework**: CatBoost
- **Features**:
  - Categorical: trauma levels, relationships, system membership
  - Numerical: beds, distances, facility counts
  - Geographic: state, regional indicators
- **Performance Metrics**: RMSE, R²

### Data Processing
- Feature engineering pipeline
- Categorical encoding
- Geographic calculations
- Market dynamics computations

### Scenario Engine
- Real-time prediction updates
- Competitor impact modeling
- Market saturation effects
- System membership influences

## Current Status

### Working Features
- Base predictive model
- Enhanced feature selection interface
- Feature engineering pipeline
- Basic scenario planning
- Market analysis tools

### In Development
- Enhanced competitor impact modeling
- More sophisticated market dynamics
- Improved visualization tools
- Extended scenario options

### Known Issues
- Competitor impact calculations need refinement
- Index alignment in scenario predictions
- Data validation improvements needed

## Setup and Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run Home.py
```

3. Navigate to:
- Predictive Model (Page 1)
- Scenario Planning (Page 2)

## Next Steps

1. **Model Improvements**:
   - Refine competitor impact calculations
   - Enhance market dynamics modeling
   - Add more sophisticated facility interactions

2. **User Interface**:
   - Add detailed visualizations
   - Improve scenario planning interface
   - Enhance data exploration tools

3. **Documentation**:
   - Add feature descriptions
   - Include usage examples
   - Document model assumptions
