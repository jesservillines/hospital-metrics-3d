import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from models import ReferralPredictor, FeatureEngineer  # Adjust if needed
import traceback
import os

def run():
    # Require a trained model in session
    if not st.session_state.get('model_trained', False):
        st.warning("Please train the model in the Predictive Model tab first!")
        return

    st.title("🎯 Scenario Planning")
    st.write("Simulate different scenarios and see their impact on future referrals")

    # Load data
    @st.cache_data
    def load_model_data():
        """Load and prepare the modeling dataset."""
        try:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            df = pd.read_csv(os.path.join(data_dir, "model_df_ml.csv"))
            # Convert year_month (format yyyymm) to a datetime
            df['year_month'] = pd.to_datetime(df['year_month'].astype(str), format='%Y%m')
            return df
        except Exception as e:
            st.error(f"Error in load_model_data: {str(e)}")
            st.error(f"Full traceback: {traceback.format_exc()}")
            raise

    try:
        if 'scenario_base_data' not in st.session_state:
            st.session_state['scenario_base_data'] = load_model_data()
        base_data = st.session_state['scenario_base_data']
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return

    # Separate out the date column so we have easy references
    dates = base_data['year_month']
    data_for_training = base_data.copy()

    # Make sure your state column name matches what's in your dataset
    STATE_COLUMN = 'hospital_2-letter_state_abbreviation'  # or 'hospital_2_letter_state_abbreviation'
    if STATE_COLUMN not in data_for_training.columns:
        st.error(f"State column '{STATE_COLUMN}' not found in the data. Please check the data structure.")
        return

    # Utility / Helper Functions
    def apply_scenario_to_data(scenario_dict: dict, base_df: pd.DataFrame) -> pd.DataFrame:
        """
        Given one scenario's config dictionary and the original data,
        return a new DataFrame with the scenario changes applied.
        """
        scenario_type = scenario_dict.get('type')
        facility_changes = scenario_dict.get('facility_options', {})
        facility_state = scenario_dict.get('state')
        selected_facility_name = scenario_dict.get('facility_name_to_modify')  # replaced old ID
        facility_kind = scenario_dict.get('facility_kind')  # "Competitor" or "Trauma Center"

        # Make a copy so we don't mutate the original
        scenario_df = base_df.copy()

        if scenario_type == "Add New Facility":
            # 1. Clone some row from the same state if possible
            state_mask = scenario_df[STATE_COLUMN] == facility_state
            if not state_mask.any():
                # If no row from that state, just pick the first row
                cloned_row = scenario_df.iloc[[0]].copy()
            else:
                cloned_row = scenario_df[state_mask].iloc[[0]].copy()

            # Create a "new" hospital_name to label it
            new_facility_name = f"NEW_{facility_state}_{np.random.randint(1000,9999)}"
            cloned_row['hospital_name'] = new_facility_name

            # Overwrite relevant columns if they exist in the data
            for col, val in facility_changes.items():
                if col in cloned_row.columns:
                    cloned_row[col] = val

            # If it's a competitor, we might want to do something to all rows in that state
            if facility_kind == "Competitor":
                # If you have a column like 'num_irfs_in_state', adjust below as needed
                if 'num_irfs_in_state' in scenario_df.columns:
                    scenario_df.loc[state_mask, 'num_irfs_in_state'] += 1

                # Possibly remove model system membership from all or do other logic
                if 'model_system_member' in scenario_df.columns:
                    scenario_df.loc[state_mask, 'model_system_member'] = 0

                # The new facility presumably is_competitor = 1
                if 'is_competitor' in cloned_row.columns:
                    cloned_row['is_competitor'] = 1
                if 'model_system_member' in cloned_row.columns:
                    cloned_row['model_system_member'] = 0

            else:
                # e.g. Trauma Center
                if 'is_competitor' in cloned_row.columns:
                    cloned_row['is_competitor'] = 0
                if 'model_system_member' in cloned_row.columns:
                    cloned_row['model_system_member'] = 1

            # Append the new facility
            scenario_df = pd.concat([scenario_df, cloned_row], ignore_index=True)

        elif scenario_type == "Modify Existing Facility":
            # Find the row for the existing facility by hospital_name
            mask = scenario_df['hospital_name'] == selected_facility_name
            if not mask.any():
                st.warning(f"Facility '{selected_facility_name}' not found; skipping changes.")
                return scenario_df

            # Overwrite columns with scenario changes (only if they exist)
            for col, val in facility_changes.items():
                if col in scenario_df.columns:
                    scenario_df.loc[mask, col] = val

        return scenario_df

    def predict_scenario(scenario_df: pd.DataFrame) -> pd.DataFrame:
        try:
            model = st.session_state['model']  # Our trained model
            # We must use the same selected features that were used to train
            selected_features = st.session_state['selected_features']

            # Convert selected_features (a set) to a list
            scenario_X = scenario_df[list(selected_features)]
            
            scenario_preds, _, _ = model.predict(scenario_X)

            return pd.DataFrame({
                'date': scenario_df['year_month'],
                'predicted': scenario_preds,
            })

        except Exception as e:
            st.error(f"Error predicting scenario: {str(e)}")
            st.code(traceback.format_exc())
            return pd.DataFrame()

    # Scenario Management in Session State
    if 'scenarios' not in st.session_state:
        st.session_state['scenarios'] = {}  # Key = scenario_name, Value = scenario_dict

    # Scenario Creation Form
    with st.expander("Create or Edit Scenarios", expanded=True):
        st.write("You can define multiple scenarios, each describing changes to the data. Then run them together.")

        scenario_name = st.text_input("Scenario Name", value="", placeholder="e.g. 'New Competitor in Colorado'")
        scenario_type = st.radio("Scenario Type", ["Add New Facility", "Modify Existing Facility"])

        # Choose a state
        unique_states = sorted(data_for_training[STATE_COLUMN].dropna().unique())
        selected_state = st.selectbox("Select State", unique_states)

        # For "Modify Existing Facility," pick which facility name to modify
        facility_name_to_modify = ""
        if scenario_type == "Modify Existing Facility":
            # Filter data to that state
            state_df = data_for_training[data_for_training[STATE_COLUMN] == selected_state]
            unique_fac_names = state_df['hospital_name'].unique()
            facility_name_to_modify = st.selectbox("Select Facility to Modify", unique_fac_names)

        # Example numeric changes
        st.write("Facility Options:")
        with st.form("scenario_form"):
            total_hospital_beds_val = st.number_input("Total Hospital Beds", min_value=1, value=50)
            facility_kind = st.radio("Facility Type", ["Trauma Center", "Competitor"])
            
            # Submit button
            submitted = st.form_submit_button("Add Scenario")
            
            if submitted and scenario_name:
                # Create scenario dictionary
                scenario_dict = {
                    'type': scenario_type,
                    'state': selected_state,
                    'facility_name_to_modify': facility_name_to_modify if scenario_type == "Modify Existing Facility" else None,
                    'facility_kind': facility_kind,
                    'facility_options': {
                        'total_hospital_beds': total_hospital_beds_val,
                    }
                }
                
                # Store in session state
                st.session_state['scenarios'][scenario_name] = scenario_dict
                st.success(f"Added scenario: {scenario_name}")

    # Display and Run Scenarios
    if st.session_state['scenarios']:
        st.write("### Current Scenarios")
        
        # Allow selecting which scenarios to run
        selected_scenarios = st.multiselect(
            "Select scenarios to run",
            options=list(st.session_state['scenarios'].keys()),
            default=list(st.session_state['scenarios'].keys())
        )
        
        if st.button("Run Selected Scenarios"):
            with st.spinner("Running scenarios..."):
                # Get base predictions first
                base_predictions = predict_scenario(data_for_training)
                
                # Run each selected scenario
                scenario_results = {}
                for scenario_name in selected_scenarios:
                    scenario_dict = st.session_state['scenarios'][scenario_name]
                    
                    # Apply scenario changes to data
                    scenario_data = apply_scenario_to_data(scenario_dict, data_for_training)
                    
                    # Get predictions for this scenario
                    scenario_predictions = predict_scenario(scenario_data)
                    
                    # Store results
                    scenario_results[scenario_name] = scenario_predictions
                
                # Create visualization
                if scenario_results:
                    # Prepare data for plotting
                    plot_data = []
                    
                    # Add base predictions
                    base_df = pd.DataFrame({
                        'Date': base_predictions['date'],
                        'Value': base_predictions['predicted'],
                        'Scenario': 'Baseline'
                    })
                    plot_data.append(base_df)
                    
                    # Add scenario predictions
                    for scenario_name, predictions in scenario_results.items():
                        scenario_df = pd.DataFrame({
                            'Date': predictions['date'],
                            'Value': predictions['predicted'],
                            'Scenario': scenario_name
                        })
                        plot_data.append(scenario_df)
                    
                    # Combine all data
                    all_data = pd.concat(plot_data)
                    
                    # Create chart
                    chart = alt.Chart(all_data).mark_line().encode(
                        x=alt.X('Date:T', title='Date'),
                        y=alt.Y('Value:Q', title='Predicted Referrals'),
                        color=alt.Color('Scenario:N', title='Scenario'),
                        tooltip=['Date:T', 'Value:Q', 'Scenario:N']
                    ).properties(
                        width=800,
                        height=400,
                        title='Scenario Comparison'
                    ).interactive()
                    
                    st.altair_chart(chart, use_container_width=True)
                    
                    # Calculate and display impact metrics
                    st.write("### Impact Analysis")
                    
                    impact_data = []
                    baseline_total = base_predictions['predicted'].sum()
                    
                    for scenario_name, predictions in scenario_results.items():
                        scenario_total = predictions['predicted'].sum()
                        percent_change = ((scenario_total - baseline_total) / baseline_total) * 100
                        absolute_change = scenario_total - baseline_total
                        
                        impact_data.append({
                            'Scenario': scenario_name,
                            'Total Referrals': scenario_total,
                            'Absolute Change': absolute_change,
                            'Percent Change': percent_change
                        })
                    
                    impact_df = pd.DataFrame(impact_data)
                    st.dataframe(impact_df)

if __name__ == "__main__":
    run()
