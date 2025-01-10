import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from models import ReferralPredictor, FeatureEngineer
import pickle
from pathlib import Path
import os
import datetime
import traceback

def run():
    # Initialize session states
    if 'model' not in st.session_state:
        st.session_state['model'] = None
    if 'feature_columns' not in st.session_state:
        st.session_state['feature_columns'] = []
    if 'selected_features' not in st.session_state:
        st.session_state['selected_features'] = set()
    if 'last_training_time' not in st.session_state:
        st.session_state['last_training_time'] = None
    if 'model_trained' not in st.session_state:
        st.session_state['model_trained'] = False
    if 'advanced_features' not in st.session_state:
        st.session_state['advanced_features'] = {
            'add_seasonality': False,
            'time_lags': []
        }

    # Page title
    st.title("📊 Predictive Model Results")

    # Load data
    @st.cache_data
    def load_model_data():
        """Load and prepare the modeling dataset."""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        df = pd.read_csv(os.path.join(data_dir, "model_df_ml.csv"))
        df['year_month'] = pd.to_datetime(df['year_month'].astype(str), format='%Y%m')
        return df

    try:
        data = load_model_data()
        # Store dates separately but keep in data
        dates = data['year_month']
        
        # Create copy for training
        data_for_training = data.copy()
        
        # Get feature columns (excluding target)
        feature_columns = [col for col in data.columns if col != 'qualified_referrals']
        st.session_state['feature_columns'] = feature_columns
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return

    # Sidebar for model configuration
    st.sidebar.write("### Model Configuration")

    # Model parameters
    st.sidebar.write("#### Model Parameters")
    confidence_level = st.sidebar.slider("Confidence Level", 0.8, 0.99, 0.90, 0.01)
    iterations = st.sidebar.number_input("Number of Iterations", 100, 2000, 1000, 100)
    learning_rate = st.sidebar.number_input("Learning Rate", 0.001, 0.1, 0.03, 0.001, format="%.3f")
    depth = st.sidebar.number_input("Depth", 1, 10, 5, 1)

    # Only show feature selection if model not trained
    if not st.session_state['model_trained']:
        # Feature selection
        st.sidebar.header("Feature Selection")

        # Add feature search/filter
        feature_search = st.sidebar.text_input("🔍 Search Features", "", key="feature_search")
        
        # Initialize selected features in session state if not present
        if 'selected_features' not in st.session_state:
            st.session_state['selected_features'] = set()  # Start with empty set
        
        # Quick selection buttons
        col1, col2, col3 = st.sidebar.columns(3)
        if col1.button("Select All", key="global_select"):
            st.session_state['selected_features'] = set(st.session_state['feature_columns'])
        if col2.button("Clear All", key="global_clear"):
            st.session_state['selected_features'] = set()
        if col3.button("Reset", key="global_reset"):
            st.session_state['selected_features'] = set(basic_features)  # Reset to just basic features
        
        selected_features = st.session_state['selected_features']
        
        # Define feature groups
        basic_features = ["year_month", "total_referrals", "hospital_name"]
        
        # Remove basic features from consideration for other groups
        remaining_features = [f for f in st.session_state['feature_columns'] if f not in basic_features]
        
        # Hospital Info (excluding basic features)
        hospital_features = [f for f in remaining_features if ("hospital_" in f) or ("trauma_level_" in f)]
        remaining_features = [f for f in remaining_features if f not in hospital_features]
        
        # Census features
        rship_features = [f for f in remaining_features if any(term in f for term in ["rship"])]
        remaining_features = [f for f in remaining_features if f not in rship_features]

        # Distance Features
        distance_features = [f for f in remaining_features if ("distance" in f) or ("within_" in f)]
        remaining_features = [f for f in remaining_features if f not in distance_features]
        
        # Referral Stats (excluding basic features)
        seasonal_features = [f for f in remaining_features if any(term in f for term in ["referral", "lag"])]
        remaining_features = [f for f in remaining_features if f not in seasonal_features]
        
        # Census features
        census_features = [f for f in remaining_features if any(term in f for term in ["occ", "ind", "income","insurance", "families", "civilian", "commuters"])]
        remaining_features = [f for f in remaining_features if f not in census_features]
        
        # Other Features
        other_features = remaining_features
        
        feature_groups = {
            "Basic Features": basic_features,
            "Hospital Info": hospital_features,
            "Relationship Strength": rship_features,    
            "Distance Features": distance_features,
            "Seasonal": seasonal_features,
            "Census": census_features,
            "Other": other_features
        }
        
        # Remove empty groups
        feature_groups = {k: v for k, v in feature_groups.items() if v}
        
        # Display features by group
        for group_name, features in feature_groups.items():
            if not features:
                continue
                
            # Filter features based on search
            if feature_search:
                features = [f for f in features if feature_search.lower() in f.lower()]
                if not features:
                    continue
            
            with st.sidebar.expander(f"{group_name} ({len(features)})"):
                # Group selection buttons
                col1, col2 = st.columns(2)
                group_key = group_name.lower().replace(" ", "_").replace("-", "_")
                
                if col1.button("Select All", key=f"select_{group_key}"):
                    st.session_state['selected_features'].update(features)
                if col2.button("Clear", key=f"clear_{group_key}"):
                    st.session_state['selected_features'].difference_update(features)
                
                # Individual feature toggles
                for feature in sorted(features):
                    feature_key = f"{group_key}_{feature}"
                    if st.checkbox(
                        feature, 
                        value=feature in st.session_state['selected_features'], 
                        key=feature_key,
                        help=f"Include {feature} in model training"
                    ):
                        st.session_state['selected_features'].add(feature)
                    else:
                        st.session_state['selected_features'].discard(feature)
        
        st.sidebar.write(f"Selected {len(st.session_state['selected_features'])} features")
        
        # Advanced Features section
        with st.sidebar.expander("Advanced Features ⚙️"):
            # Initialize advanced features in session state if not present
            if 'advanced_features' not in st.session_state:
                st.session_state['advanced_features'] = {
                    'add_seasonality': False,
                    'time_lags': []
                }
            
            # Add seasonality toggle
            add_seasonality = st.checkbox(
                "Add Seasonality Features",
                value=st.session_state['advanced_features'].get('add_seasonality', False),
                help="Add seasonal indices and cyclical features",
                key="advanced_seasonality"
            )
            
            # Add time lag selection
            time_lags = st.multiselect(
                "Add Time Lag Features",
                options=[1, 3, 6, 12],
                default=st.session_state['advanced_features'].get('time_lags', []),
                help="Add lagged values of referrals",
                key="advanced_time_lags"
            )
            
            # Update session state
            st.session_state['advanced_features'] = {
                'add_seasonality': add_seasonality,
                'time_lags': time_lags
            }

        # Train model button
        if st.sidebar.button("Train Model"):
            with st.spinner("Training model..."):
                try:
                    print("Available columns in data:")
                    print(data_for_training.columns.tolist())
                    print("\nSample of data:")
                    print(data_for_training.head())
                    
                    # Identify categorical and numerical features
                    categorical_features = [col for col in st.session_state['selected_features'] if data_for_training[col].dtype == 'object']
                    numerical_features = [col for col in st.session_state['selected_features'] if data_for_training[col].dtype != 'object']
                    
                    print(f"Categorical features: {categorical_features}")
                    print(f"Numerical features: {numerical_features}")
                    print(f"Advanced Features from Session State: {st.session_state['advanced_features']}")
                    
                    # Initialize feature engineer with advanced features
                    feature_engineer = FeatureEngineer(
                        categorical_features=categorical_features,
                        numerical_features=numerical_features,
                        add_seasonality=st.session_state['advanced_features']['add_seasonality'],
                        time_lags=st.session_state['advanced_features']['time_lags'],
                        target_column='qualified_referrals',
                        date_column='year_month'
                    )
                    
                    # Apply feature engineering to get engineered feature names
                    print("Starting feature engineering...")
                    X_temp = feature_engineer.fit_transform(data_for_training.copy())
                    engineered_features = feature_engineer.get_feature_names()
                    
                    print(f"Engineered features from fit_transform: {engineered_features}")
                    print(f"Columns in transformed data: {X_temp.columns.tolist()}")
                    
                    # Combine selected and engineered features
                    all_features = list(st.session_state['selected_features']) + engineered_features
                    
                    print(f"All features for model: {all_features}")
                    
                    # Initialize model with all features
                    model = ReferralPredictor(
                        selected_features=all_features,
                        feature_engineer=feature_engineer,
                        confidence_level=confidence_level,
                        model_params={
                            'iterations': iterations,
                            'learning_rate': learning_rate,
                            'depth': depth
                        }
                    )
                    
                    # Prepare data for training
                    X = data_for_training.copy()
                    y = X['qualified_referrals']
                    
                    # Train model
                    try:
                        model.fit(X, y)
                        st.success('Model trained successfully!')
                        
                        # Store model in session state
                        st.session_state['model'] = model
                        st.session_state['selected_features'] = st.session_state['selected_features']
                        st.session_state['model_trained'] = True
                        st.session_state['last_training_time'] = datetime.datetime.now()
                        
                    except Exception as e:
                        st.error(f'Error training model: {str(e)}')
                        st.write('Traceback:')
                        st.code(traceback.format_exc())
                    
                except Exception as e:
                    st.error(f"Error training model: {str(e)}")
                    st.code(traceback.format_exc())
    else:
        st.sidebar.success("Model already trained!")
        selected_features = st.session_state['selected_features']
        
        # Add option to retrain
        if st.sidebar.button("Retrain Model"):
            st.session_state['model_trained'] = False
            st.session_state['model'] = None
            st.rerun()  # Use st.rerun() instead of st.experimental_rerun()

    # Create two columns for visualizations
    col1, col2 = st.columns(2)

    with col1:
        st.write("### Model Performance")
        
        if st.session_state['model'] is not None:
            # Make predictions
            predictions, _, _ = st.session_state['model'].predict(data_for_training[list(st.session_state['selected_features'])])
            metrics = st.session_state['model'].evaluate(data_for_training[list(st.session_state['selected_features'])], data_for_training['qualified_referrals'])
            
            # Display metrics
            metric_cols = st.columns(3)
            with metric_cols[0]:
                st.metric("R²", f"{metrics.get('r2', 0):.3f}")
            with metric_cols[1]:
                st.metric("MAE", f"{metrics.get('mae', 0):.1f}")
            with metric_cols[2]:
                st.metric("RMSE", f"{metrics.get('rmse', 0):.1f}")
            
            # Create visualization data
            viz_data = pd.DataFrame({
                'Date': dates,
                'Actual': data_for_training['qualified_referrals'],
                'Predicted': predictions,
                'Type': 'Historical'
            })
            
            # Aggregate by date
            viz_data_agg = viz_data.groupby('Date').agg({
                'Actual': 'sum',
                'Predicted': 'sum',
                'Type': 'first'
            }).reset_index()
            
            # Create base chart
            base = alt.Chart(viz_data_agg).encode(
                x=alt.X('Date:T', title='Date')
            )
            
            # Create a selection for highlighting on hover
            hover = alt.selection_single(
                fields=['Date'],
                nearest=True,
                on='mouseover',
                empty='none',
            )
            
            # Add points for hover interaction
            points = base.mark_circle().encode(
                x='Date:T',
                y=alt.Y('Predicted:Q', title='Number of Referrals'),
                opacity=alt.value(0),
                tooltip=[
                    alt.Tooltip('Date:T', title='Date'),
                    alt.Tooltip('Actual:Q', title='Actual Referrals', format=','),
                    alt.Tooltip('Predicted:Q', title='Predicted Referrals', format=',')
                ]
            ).add_selection(hover)
            
            # Draw the actual values line
            line_actual = base.mark_line(color='#1f77b4', strokeWidth=2).encode(
                y=alt.Y('Actual:Q', title='Number of Referrals'),
                tooltip=['Date:T', alt.Tooltip('Actual:Q', title='Actual Referrals', format=',')]
            )
            
            # Draw the predictions line
            line_predicted = base.mark_line(color='#2ca02c', strokeWidth=2).encode(
                y=alt.Y('Predicted:Q'),
                tooltip=['Date:T', alt.Tooltip('Predicted:Q', title='Predicted Referrals', format=',')]
            )
            
            # Add a rule mark to highlight on hover
            rule = base.mark_rule(color='gray').encode(
                x='Date:T'
            ).transform_filter(hover)
            
            # Combine all the layers
            chart = alt.layer(line_actual, line_predicted, points, rule).properties(
                width=600,
                height=400
            ).interactive()
            
            # Display the chart
            st.altair_chart(chart, use_container_width=True)

    with col2:
        st.write("### Feature Importance")
        if st.session_state['model'] is not None:
            # Get feature importance
            feature_importance = st.session_state['model'].get_feature_importance()
            
            # Create feature importance DataFrame
            importance_data = pd.DataFrame({
                'Feature': feature_importance['feature'].values,
                'Importance': feature_importance['importance'].values
            }).sort_values('Importance', ascending=True)
            
            # Create feature importance chart
            importance_chart = alt.Chart(importance_data).mark_bar().encode(
                y=alt.Y('Feature:N', sort='-x', title=None),
                x=alt.X('Importance:Q', title='Feature Importance'),
                tooltip=['Feature', alt.Tooltip('Importance:Q', format='.2f')]
            ).properties(
                width=400,
                height=min(400, len(importance_data) * 25)
            )
            
            st.altair_chart(importance_chart, use_container_width=True)

if __name__ == "__main__":
    run()
