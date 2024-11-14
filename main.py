# team_cost_calculator.py

# Import necessary libraries
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import random
import json
from datetime import datetime, date, timedelta
import calendar

# Set Streamlit page configuration
st.set_page_config(page_title="Team Cost Calculator", layout="wide")
st.title("Team Cost Calculator with Gantt Chart and Yearly Cost Summary")

# Define the roles and their rates
hourly_rates = {
    'Management': {
        'Onshore FTE': 263,
        'Offshore FTE': 131,
        'Onshore Professional Services': 394,
        'Offshore Professional Services': 197
    },
    'Product Manager': {
        'Onshore FTE': 140,
        'Offshore FTE': 105,
        'Onshore Professional Services': 175,
        'Offshore Professional Services': 123
    },
    'Product Specialists': {
        'Onshore FTE': 140,
        'Offshore FTE': 88,
        'Onshore Professional Services': 175,
        'Offshore Professional Services': 123
    },
    'Core Dev, Data Science & Infra': {
        'Onshore FTE': 175,
        'Offshore FTE': 123,
        'Onshore Professional Services': 228,
        'Offshore Professional Services': 140
    },
    'QA': {
        'Onshore FTE': 140,
        'Offshore FTE': 88,
        'Onshore Professional Services': 175,
        'Offshore Professional Services': 123
    },
    'UX Designers': {
        'Onshore FTE': 175,
        'Offshore FTE': 123,
        'Onshore Professional Services': 228,
        'Offshore Professional Services': 140
    },
    'Scrum Masters': {
        'Onshore FTE': 140,
        'Offshore FTE': 105,
        'Onshore Professional Services': 175,
        'Offshore Professional Services': 123
    }
}

# Function to calculate costs for a team per year based on yearly FTE salaries
def calculate_team_cost_per_year(team_roles, start_date, end_date):
    cost_per_year = {}
    
    # Convert start_date and end_date to pd.Timestamp
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    # Generate a list of years covered by the date range
    years = pd.date_range(start=start_date, end=end_date).year.unique()

    for year in years:
        # Define start and end of the year to calculate partial or full year overlap
        year_start = pd.Timestamp(f"{year}-01-01")
        year_end = pd.Timestamp(f"{year}-12-31")

        # Calculate overlapping period within the year
        overlap_start = max(start_date, year_start)
        overlap_end = min(end_date, year_end)
        overlap_days = (overlap_end - overlap_start).days + 1
        overlap_fraction = overlap_days / 365.25  # Fraction of the year

        # Calculate the cost for each role in this year
        yearly_cost = 0
        for role_info in team_roles:
            role = role_info['role']
            count = role_info['count']  # FTE value
            resource_type = role_info['resource_type']
            yearly_salary = hourly_rates.get(role, {}).get(resource_type, 0) * 1000  # Assuming hourly_rates represents yearly salaries

            # Calculate cost as FTE count times the salary, adjusted for partial year
            yearly_cost += count * yearly_salary * overlap_fraction

        cost_per_year[year] = yearly_cost

    return cost_per_year

# Function to calculate cost breakdown by role
def calculate_role_costs(team_roles, start_date, end_date):
    # Convert start_date and end_date to pd.Timestamp
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    duration_days = (end_date - start_date).days + 1  # Include end date
    duration_fraction = duration_days / 365.25  # Fraction of a year

    role_costs = {}
    for role_info in team_roles:
        role = role_info['role']
        count = role_info['count']
        resource_type = role_info['resource_type']
        yearly_salary = hourly_rates.get(role, {}).get(resource_type, 0) * 1000  # Assuming rates are per 1000 units

        # Calculate cost as FTE count times the salary, adjusted for partial year
        cost = count * yearly_salary * duration_fraction
        role_key = f"{role} ({resource_type})"
        role_costs[role_key] = cost

    return role_costs

# Function to generate demo teams
def generate_demo_teams():
    demo_teams = []
    team_names = ['Alpha', 'Beta', 'Gamma', 'Delta']
    for i in range(4):
        start_date = date.today() + timedelta(days=random.randint(0, 90))
        end_date = start_date + timedelta(days=random.randint(90, 180))
        num_roles = random.randint(1, 4)
        team_roles = []
        for _ in range(num_roles):
            role = random.choice(list(hourly_rates.keys()))
            resource_type = random.choice(list(hourly_rates[role].keys()))
            count = random.uniform(0.5, 5.0)
            count = round(count * 2) / 2  # Round to nearest 0.5
            team_roles.append({
                'role': role,
                'count': count,
                'resource_type': resource_type
            })
        demo_teams.append({
            'team_name': f"Team {team_names[i]}",
            'team_description': f"Description for Team {team_names[i]}",
            'start_date': start_date,
            'end_date': end_date,
            'duration_weeks': 0,
            'team_roles': team_roles,
            'cost_per_year': {},
            'total_team_cost': 0
        })
    return demo_teams

# Initialize session state for teams
if 'teams' not in st.session_state:
    st.session_state.teams = []

# Sidebar for adjusting hourly rates and data import/export
with st.sidebar:
    st.header("Settings")
    
    # Adjust Hourly Rates
    with st.expander("Adjust Hourly Rates"):
        for role in hourly_rates.keys():
            st.subheader(f"{role} Rates")
            for resource_type in hourly_rates[role]:
                current_rate = hourly_rates[role][resource_type]
                new_rate = st.number_input(
                    f"{resource_type} ({role})",
                    min_value=0,
                    value=int(current_rate),
                    step=1,
                    key=f"{role}_{resource_type}_adjust"
                )
                hourly_rates[role][resource_type] = new_rate

    st.header("Data Import/Export")

    # Export Teams
    if st.button('Export Teams', key='export_teams'):
        if st.session_state.get('teams'):
            # Prepare data for export
            teams_copy = []
            for team in st.session_state.teams:
                team_copy = team.copy()
                # Convert datetime.date objects to strings
                if isinstance(team_copy['start_date'], date):
                    team_copy['start_date'] = team_copy['start_date'].isoformat()
                if isinstance(team_copy['end_date'], date):
                    team_copy['end_date'] = team_copy['end_date'].isoformat()
                team_roles_copy = []
                for role_info in team_copy.get('team_roles', []):
                    role_info_copy = role_info.copy()
                    team_roles_copy.append(role_info_copy)
                team_copy['team_roles'] = team_roles_copy
                teams_copy.append(team_copy)

            teams_json = json.dumps(teams_copy, indent=4)
            st.download_button(
                'Download Teams Data',
                data=teams_json,
                file_name='teams_data.json',
                mime='application/json'
            )
        else:
            st.info("No teams to export.")

    # Import Teams
    uploaded_file = st.file_uploader("Upload Teams Data", type=['json'], key='upload_teams')
    if uploaded_file is not None:
        try:
            teams_json = uploaded_file.read().decode('utf-8')
            teams_data = json.loads(teams_json)

            # Convert date strings back to datetime.date objects
            for team in teams_data:
                if 'start_date' in team and team['start_date']:
                    team['start_date'] = datetime.fromisoformat(team['start_date']).date()
                else:
                    team['start_date'] = None

                if 'end_date' in team and team['end_date']:
                    team['end_date'] = datetime.fromisoformat(team['end_date']).date()
                else:
                    team['end_date'] = None

                # Ensure 'team_roles' is initialized
                if 'team_roles' not in team or team['team_roles'] is None:
                    team['team_roles'] = []

            st.session_state.teams = teams_data
            st.success("Teams data uploaded successfully.")
        except Exception as e:
            st.error(f"Error uploading teams data: {e}")

    # Reset Teams
    if st.button('Reset All Teams', key='reset_all_teams'):
        st.session_state.teams = []
        st.success("All teams have been reset.")

    # Generate Demo Teams
    if st.button('Generate Demo Teams', key='generate_demo_teams'):
        st.session_state.teams = generate_demo_teams()
        st.success("Demo teams have been generated.")

# Function to add a new team
def add_team():
    st.session_state.teams.append({
        'team_name': '',
        'team_description': '',
        'start_date': date.today(),
        'end_date': date.today() + timedelta(days=30),
        'duration_weeks': 0,
        'team_roles': [],  # Ensure team_roles is initialized as an empty list
        'cost_per_year': {},
        'total_team_cost': 0
    })

# Add Team Button
if st.button("Add New Team", key="add_new_team"):
    add_team()

# Display existing teams and allow editing
if st.session_state.teams:
    teams = st.session_state.teams  # For convenience
    team_names = [team['team_name'] or f"Team {idx+1}" for idx, team in enumerate(teams)]
    team_tabs = st.tabs(team_names)
    for idx, (team, team_tab) in enumerate(zip(teams, team_tabs)):
        with team_tab:
            # Team Details Section
            with st.expander("Team Details", expanded=True):
                team['team_name'] = st.text_input(
                    "Team Name",
                    value=team['team_name'],
                    key=f"team_{idx}_name"
                )
                team['team_description'] = st.text_area(
                    "Team Description",
                    value=team['team_description'],
                    key=f"team_{idx}_description"
                )

            # Team Duration Section
            with st.expander("Team Duration", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    start_year = st.selectbox(
                        "Start Year",
                        options=range(2020, 2031),
                        index=0,
                        key=f"team_{idx}_start_year"
                    )
                    start_month = st.selectbox(
                        "Start Month",
                        options=list(calendar.month_name)[1:],  # Exclude empty string at index 0
                        index=0,
                        key=f"team_{idx}_start_month"
                    )
                    try:
                        team['start_date'] = datetime(
                            start_year,
                            list(calendar.month_name).index(start_month),
                            1
                        ).date()
                    except Exception as e:
                        st.error(f"Invalid start date: {e}")
                        team['duration_weeks'] = 0

                with col2:
                    end_year = st.selectbox(
                        "End Year",
                        options=range(2020, 2031),
                        index=10,  # Default to 2030
                        key=f"team_{idx}_end_year"
                    )
                    end_month = st.selectbox(
                        "End Month",
                        options=list(calendar.month_name)[1:],  # Exclude empty string at index 0
                        index=11,
                        key=f"team_{idx}_end_month"
                    )
                    try:
                        team['end_date'] = datetime(
                            end_year,
                            list(calendar.month_name).index(end_month),
                            1
                        ).date()
                    except Exception as e:
                        st.error(f"Invalid end date: {e}")
                        team['duration_weeks'] = 0

                    # Calculate duration in weeks
                    if team['end_date'] and team['start_date']:
                        if team['end_date'] <= team['start_date']:
                            st.error("End date must be after start date.")
                            team['duration_weeks'] = 0
                        else:
                            duration_days = (team['end_date'] - team['start_date']).days + 1
                            team['duration_weeks'] = round(duration_days / 7, 2)

            # Roles in Team Section
            with st.expander("Roles in Team", expanded=True):
                # Define Roles in Team
                team_roles = team.get('team_roles', [])
                num_roles = st.number_input(
                    "Number of Different Roles",
                    min_value=1,
                    value=len(team_roles) if team_roles else 1,
                    step=1,
                    key=f"team_{idx}_num_roles"
                )

                # Adjust the team_roles list to match num_roles
                while len(team_roles) < num_roles:
                    team_roles.append({'role': '', 'count': 1.0, 'resource_type': ''})
                while len(team_roles) > num_roles:
                    team_roles.pop()

                team['team_roles'] = team_roles  # Update the team dict

                for j in range(int(num_roles)):
                    st.write(f"**Role {j+1}**")
                    role_info = team_roles[j]
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        role_info['role'] = st.selectbox(
                            "Role",
                            options=list(hourly_rates.keys()),
                            index=list(hourly_rates.keys()).index(role_info['role']) if role_info['role'] in hourly_rates else 0,
                            key=f"team_{idx}_role_{j}_role_select"
                        )

                    with col2:
                        resource_types = list(hourly_rates.get(role_info['role'], {}).keys())
                        if resource_types:
                            role_info['resource_type'] = st.selectbox(
                                "Resource Type",
                                options=resource_types,
                                index=resource_types.index(role_info['resource_type']) if role_info['resource_type'] in resource_types else 0,
                                key=f"team_{idx}_role_{j}_resource_type_select"
                            )
                        else:
                            st.error(f"No resource types available for {role_info['role']}")

                    with col3:
                        role_info['count'] = st.number_input(
                            "FTE Count",
                            min_value=0.0,
                            value=float(role_info.get('count', 1.0)),
                            step=0.5,
                            format="%.1f",
                            key=f"team_{idx}_role_{j}_fte_input"
                        )

            # Delete Team Button
            if st.button('Delete Team', key=f'delete_team_{idx}'):
                del st.session_state.teams[idx]
                st.experimental_rerun()
else:
    st.write("No teams defined yet.")

# Generate Gantt Chart and Cost Summaries
if st.button("Generate Gantt Chart and Cost Summary", key="generate_gantt_cost_summary"):
    teams = st.session_state.teams
    if not teams:
        st.error("Please define at least one team.")
    else:
        # [Your existing code for generating charts and summaries goes here]
        # This remains unchanged from your original script.
        pass  # Replace this with the rest of your code

# The rest of your application code (Summary Dashboard, Heatmap, Interactive Dashboard, What-If Analysis) remains unchanged.
