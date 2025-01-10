# Referral Map

A machine learning-powered tool for healthcare referral prediction and scenario planning.

## Overview

This application helps healthcare organizations analyze and predict patient referral patterns. It uses advanced machine learning techniques to model referral behavior and allows users to explore "what-if" scenarios such as adding new facilities or competitors.

## Features

### 0. Authentication System
- Secure login system with password hashing
- Role-based access control
- Session state management
- Configurable user credentials via YAML

### 1. Predictive Model
- Machine learning model built with CatBoost
- Predicts referral patterns based on:
  - Facility characteristics (beds, trauma levels)
  - Geographic factors
  - Market dynamics (competition, saturation)
  - Historical referral data

### 2. Advanced Scenario Planning
- Multiple scenario management:
  - Create and save multiple scenarios
  - Run scenarios in parallel
  - Compare results side by side
- Interactive scenario creation for:
  - New facilities
  - Competitor analysis
  - Trauma center additions
- Facility modifications:
  - Edit existing facility parameters
  - Bulk edit via data grid
  - Real-time updates
- Impact analysis showing:
  - State-level effects
  - Market-wide changes
  - Facility-specific predictions
- Data visualization:
  - Interactive time series charts
  - Scenario comparison plots
  - Downloadable results in CSV format

### 3. Market Analysis
- Comprehensive market insights:
  - Current referral patterns
  - Competitor presence
  - Market saturation levels
  - Geographic distribution

## Technical Details

### Authentication
- Secure password hashing using SHA-256
- Session-based authentication
- Configuration via YAML file
- Protected routes and pages

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

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure user credentials in `config.yaml`
4. Run the Streamlit app:
   ```bash
   streamlit run Home.py
   ```

## Default Login
- Username: `admin`
- Password: `admin`

*Note: Change these credentials in production by modifying the `config.yaml` file.*

## Security Notes
- Change default credentials before deployment
- Keep `config.yaml` secure and backup regularly
- Use environment variables for sensitive data in production
- Regularly update dependencies for security patches

## Deployment

### Local Docker Deployment
1. Build the Docker image:
   ```bash
   docker build -t referral-map .
   ```
2. Run the container:
   ```bash
   docker run -p 8501:8501 referral-map
   ```
3. Access the app at `http://localhost:8501`

### Azure Deployment
1. Install Azure CLI and log in:
   ```bash
   az login
   ```
2. Create Azure Container Registry (ACR):
   ```bash
   az acr create --name referralmapregistry --resource-group your-resource-group --sku Basic
   ```
3. Build and push to ACR:
   ```bash
   az acr build --registry referralmapregistry --image referral-map .
   ```
4. Deploy to Azure Container Apps:
   ```bash
   az containerapp up \
     --name referral-map \
     --resource-group your-resource-group \
     --image referralmapregistry.azurecr.io/referral-map:latest \
     --target-port 8501 \
     --ingress external \
     --env-vars STREAMLIT_SERVER_PORT=8501
   ```

### Security Notes for Production
- Use Azure Key Vault for storing sensitive credentials
- Enable Azure AD authentication
- Configure SSL/TLS certificates
- Set up network security rules
- Regular security updates and monitoring

## Current Status

### Working Features
- Base predictive model
- Feature engineering pipeline
- Basic scenario planning
- Market analysis tools
- Authentication system
- Advanced scenario planning

### In Development
- Enhanced competitor impact modeling
- More sophisticated market dynamics
- Improved visualization tools
- Extended scenario options

### Known Issues
- Competitor impact calculations need refinement
- Index alignment in scenario predictions
- Data validation improvements needed

## Next Steps

1. **Model Improvements**:
   - Refine competitor impact calculations
   - Enhance market dynamics modeling
   - Add more sophisticated facility interactions

2. **User Interface**:
   - Add detailed visualizations
   - Improve error handling
   - Enhance debugging tools

3. **Data Quality**:
   - Implement more validation checks
   - Add data quality monitoring
   - Improve error reporting

## Dependencies
- Python 3.8+
- Streamlit
- CatBoost
- Pandas
- NumPy
- Altair

## Contributing
This is an active development project. Please report any issues or suggestions for improvement.
