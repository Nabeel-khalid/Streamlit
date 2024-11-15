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

# Define the roles and their yearly salaries
yearly_salaries = {
    'Management': {
        'Onshore FTE': 263000,
        'Offshore FTE': 131000,
        'Onshore Professional Services': 394000,
        'Offshore Professional Services': 197000
    },
    'Product Manager': {
        'Onshore FTE': 140000,
        'Offshore FTE': 105000,
        'Onshore Professional Services': 175000,
        'Offshore Professional Services': 123000
    },
    'Product Specialists': {
        'Onshore FTE': 140000,
        'Offshore FTE': 88000,
        'Onshore Professional Services': 175000,
        'Offshore Professional Services': 123000
    },
    'Core Dev, Data Science & Infra': {
        'Onshore FTE': 175000,
        'Offshore FTE': 123000,
        'Onshore Professional Services': 228000,
        'Offshore Professional Services': 140000
    },
    'QA': {
        'Onshore FTE': 140000,
        'Offshore FTE': 88000,
        'Onshore Professional Services': 175000,
        'Offshore Professional Services': 123000
    },
    'UX Designers': {
        'Onshore FTE': 175000,
        'Offshore FTE': 123000,
        'Onshore Professional Services': 228000,
        'Offshore Professional Services': 140000
    },
    'Scrum Masters': {
        'Onshore FTE': 140000,
        'Offshore FTE': 105000,
        'Onshore Professional Services': 175000,
        'Offshore Professional Services': 123000
    }
}

# Function to calculate costs for a team per year based on yearly salaries
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

            # Validate role and resource_type
            if not role or not resource_type:
                continue  # Skip if role or resource_type is empty

            yearly_salary = yearly_salaries.get(role, {}).get(resource_type, None)
            if yearly_salary is None:
                continue  # Skip if no matching salary found

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

        # Validate role and resource_type
        if not role or not resource_type:
            continue  # Skip if role or resource_type is empty

        yearly_salary = yearly_salaries.get(role, {}).get(resource_type, None)
        if yearly_salary is None:
            continue  # Skip if no matching salary found

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
        start_year = date.today().year + random.randint(0, 2)
        start_month = random.randint(1, 12)
        start_date = datetime(start_year, start_month, 1).date()
        end_year = start_year + random.randint(0, 2)
        end_month = random.randint(start_month, 12) if end_year == start_year else random.randint(1, 12)
        end_date = datetime(end_year, end_month, 1).date()
        num_roles = random.randint(1, 4)
        team_roles = []
        for _ in range(num_roles):
            role = random.choice(list(yearly_salaries.keys()))
            resource_type = random.choice(list(yearly_salaries[role].keys()))
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
            'start_year': start_year,
            'start_month': start_month,
            'end_year': end_year,
            'end_month': end_month,
            'duration_weeks': 0,
            'team_roles': team_roles,
            'cost_per_year': {},
            'total_team_cost': 0
        })
    return demo_teams

# Initialize session state for teams
if 'teams' not in st.session_state:
    st.session_state.teams = []

# Function to load teams from local storage
def load_teams_from_storage():
    stored_teams_json = st.session_state.get('stored_teams', '[]')
    try:
        teams_data = json.loads(stored_teams_json)
        st.session_state.teams = teams_data
    except Exception as e:
        st.error(f"Error loading teams from storage: {e}")

# Function to save teams to local storage
def save_teams_to_storage():
    st.session_state.stored_teams = json.dumps(st.session_state.teams)

# Load teams when the app starts
load_teams_from_storage()

# Sidebar for adjusting yearly salaries and data import/export
with st.sidebar:
    st.header("Settings")
    
    # Adjust Yearly Salaries
    with st.expander("Adjust Yearly Salaries"):
        for role in yearly_salaries.keys():
            st.subheader(f"{role} Salaries")
            for resource_type in yearly_salaries[role]:
                current_salary = yearly_salaries[role][resource_type]
                new_salary = st.number_input(
                    f"{resource_type} ({role})",
                    min_value=0,
                    value=int(current_salary),
                    step=1000,
                    key=f"{role}_{resource_type}_adjust"
                )
                yearly_salaries[role][resource_type] = new_salary

    st.header("Data Import/Export")

    # Export Teams
    if st.button('Export Teams', key='export_teams'):
        if st.session_state.get('teams'):
            # Prepare data for export
            teams_copy = st.session_state.teams.copy()

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

            # Ensure 'team_roles' is initialized
            for team in teams_data:
                if 'team_roles' not in team or team['team_roles'] is None:
                    team['team_roles'] = []

                # Reset calculated fields
                team['cost_per_year'] = {}
                team['total_team_cost'] = 0

            st.session_state.teams = teams_data
            save_teams_to_storage()
            st.success("Teams data uploaded successfully.")
        except Exception as e:
            st.error(f"Error uploading teams data: {e}")

    # Reset Teams
    if st.button('Reset All Teams', key='reset_all_teams'):
        st.session_state.teams = []
        save_teams_to_storage()
        st.success("All teams have been reset.")

    # Generate Demo Teams
    if st.button('Generate Demo Teams', key='generate_demo_teams'):
        st.session_state.teams = generate_demo_teams()
        save_teams_to_storage()
        st.success("Demo teams have been generated.")

# Function to add a new team
def add_team():
    # Set default role and resource type
    default_role = list(yearly_salaries.keys())[0]
    default_resource_type = list(yearly_salaries[default_role].keys())[0]
    st.session_state.teams.append({
        'team_name': '',
        'team_description': '',
        'start_year': date.today().year,
        'start_month': date.today().month,
        'end_year': date.today().year,
        'end_month': date.today().month,
        'duration_weeks': 0,
        'team_roles': [{'role': default_role, 'count': 1.0, 'resource_type': default_resource_type}],
        'cost_per_year': {},
        'total_team_cost': 0
    })
    save_teams_to_storage()

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
                        index=team.get('start_year', date.today().year) - 2020,
                        key=f"team_{idx}_start_year"
                    )
                    start_month = st.selectbox(
                        "Start Month",
                        options=list(calendar.month_name)[1:],  # Exclude empty string at index 0
                        index=team.get('start_month', date.today().month) - 1,
                        key=f"team_{idx}_start_month"
                    )
                    try:
                        team['start_year'] = start_year
                        team['start_month'] = list(calendar.month_name).index(start_month)
                        team['start_date'] = datetime(
                            start_year,
                            team['start_month'],
                            1
                        ).date()
                    except Exception as e:
                        st.error(f"Invalid start date: {e}")
                        team['duration_weeks'] = 0

                with col2:
                    end_year = st.selectbox(
                        "End Year",
                        options=range(2020, 2031),
                        index=team.get('end_year', date.today().year) - 2020,
                        key=f"team_{idx}_end_year"
                    )
                    end_month = st.selectbox(
                        "End Month",
                        options=list(calendar.month_name)[1:],  # Exclude empty string at index 0
                        index=team.get('end_month', date.today().month) - 1,
                        key=f"team_{idx}_end_month"
                    )
                    try:
                        team['end_year'] = end_year
                        team['end_month'] = list(calendar.month_name).index(end_month)
                        team['end_date'] = datetime(
                            end_year,
                            team['end_month'],
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
                    # Set default role and resource_type to valid values
                    default_role = list(yearly_salaries.keys())[0]
                    default_resource_type = list(yearly_salaries[default_role].keys())[0]
                    team_roles.append({'role': default_role, 'count': 1.0, 'resource_type': default_resource_type})
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
                            options=list(yearly_salaries.keys()),
                            index=list(yearly_salaries.keys()).index(role_info['role']) if role_info['role'] in yearly_salaries else 0,
                            key=f"team_{idx}_role_{j}_role_select"
                        )

                    with col2:
                        resource_types = list(yearly_salaries.get(role_info['role'], {}).keys())
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
                save_teams_to_storage()
                st.experimental_rerun()

    # Save teams when any input changes
    save_teams_to_storage()
else:
    st.write("No teams defined yet.")

# Generate Gantt Chart and Cost Summaries
if st.button("Generate Gantt Chart and Cost Summary", key="generate_gantt_cost_summary"):
    teams = st.session_state.teams
    if not teams:
        st.error("Please define at least one team.")
    else:
        # Calculate costs and prepare data
        gantt_data = []
        all_years = set()
        for team in teams:
            if not team.get('start_date') or not team.get('end_date') or not team.get('team_roles'):
                st.warning(f"Team '{team['team_name'] or 'Unnamed'}' is incomplete and will be skipped.")
                continue

            # Calculate team cost per year
            team['cost_per_year'] = calculate_team_cost_per_year(team['team_roles'], team['start_date'], team['end_date'])
            team['total_team_cost'] = sum(team['cost_per_year'].values())

            # Calculate role costs for pie chart
            team['role_costs'] = calculate_role_costs(team['team_roles'], team['start_date'], team['end_date'])

            # Prepare data for Gantt chart
            roles_list = []
            for role_info in team['team_roles']:
                count = role_info['count']
                role = role_info['role']
                resource_type = role_info['resource_type']
                roles_list.append(f"{count} x {role} ({resource_type})")
            roles_str = ", ".join(roles_list)
            team_name = team['team_name'] or f"Team {idx+1}"
            team_cost = team['total_team_cost']
            team_description = team['team_description']
            start_date = pd.Timestamp(team['start_date'])
            end_date = pd.Timestamp(team['end_date'])
            gantt_data.append({
                'Team': team_name,
                'Start': start_date,
                'End': end_date,
                'Cost': team_cost,
                'Roles': roles_str,
                'Description': team_description,
                'Role Costs': team['role_costs']
            })

            all_years.update(team['cost_per_year'].keys())

        if not gantt_data:
            st.error("No complete teams to display.")
        else:
            gantt_df = pd.DataFrame(gantt_data)

            # Create Gantt chart using Altair
            base = alt.Chart(gantt_df).encode(
                x='Start:T',
                x2='End:T',
                y=alt.Y('Team:N', sort=alt.EncodingSortField(field='Start', order='ascending')),
                color=alt.Color('Cost:Q', scale=alt.Scale(scheme='blues')),
            )

            bars = base.mark_bar().encode(
                tooltip=[
                    'Team', 'Start', 'End',
                    alt.Tooltip('Cost:Q', format='$,.2f'),
                    'Roles', 'Description'
                ]
            )

            # Modify selection
            selection = alt.selection_single(
                fields=['Team'],
                on='mouseover',
                nearest=False,
                empty='none',
                clear='mouseout'
            )

            gantt_chart = bars.add_selection(selection)

            # Data transformation for pie chart
            pie_data = []
            for idx, row in gantt_df.iterrows():
                team_name = row['Team']
                role_costs = row['Role Costs']
                for role, cost in role_costs.items():
                    pie_data.append({
                        'Team': team_name,
                        'Role': role,
                        'Cost': cost
                    })
            pie_df = pd.DataFrame(pie_data)

            pie_chart = alt.Chart(pie_df).transform_filter(
                selection
            ).mark_arc().encode(
                theta=alt.Theta('Cost:Q', stack=True),
                color=alt.Color('Role:N', legend=alt.Legend(title="Roles", orient="bottom")),
                tooltip=[alt.Tooltip('Role:N'), alt.Tooltip('Cost:Q', format='$,.2f')]
            ).properties(
                width=300,
                height=300
            )

            combined_chart = alt.hconcat(
                gantt_chart.properties(title='Team Gantt Chart').interactive(),
                pie_chart.properties(title='Team Cost Composition')
            )

            st.altair_chart(combined_chart, use_container_width=True)

            # Yearly Cost Summary
            st.header("Yearly Cost Summary")
            all_years = sorted(all_years)
            yearly_costs = []
            for year in all_years:
                total_cost = 0
                for team in teams:
                    team_cost = team['cost_per_year'].get(year, 0)
                    total_cost += team_cost
                yearly_costs.append({'Year': year, 'Cost': total_cost})

            yearly_costs_df = pd.DataFrame(yearly_costs)

            # Display the summary table
            st.subheader("Total Costs per Year")
            st.table(yearly_costs_df.style.format({'Cost': '${:,.2f}'}))

            # Bar chart of yearly costs
            cost_bar_chart = alt.Chart(yearly_costs_df).mark_bar().encode(
                x='Year:O',
                y='Cost:Q',
                tooltip=['Year', alt.Tooltip('Cost:Q', format=",.2f")]
            ).properties(
                title='Total Costs per Year'
            )

            st.altair_chart(cost_bar_chart, use_container_width=True)

            # Detailed breakdown per team per year
            st.subheader("Detailed Costs per Team per Year")
            detailed_data = []
            for team in teams:
                team_name = team['team_name'] or f"Team {teams.index(team)+1}"
                for year, cost in team['cost_per_year'].items():
                    detailed_data.append({
                        'Team': team_name,
                        'Year': year,
                        'Cost': cost
                    })
            detailed_df = pd.DataFrame(detailed_data)

            # Pivot table to show teams as rows and years as columns
            pivot_df = detailed_df.pivot(index='Team', columns='Year', values='Cost').fillna(0)
            pivot_df = pivot_df.reset_index()
            st.table(pivot_df.style.format({col: '${:,.2f}' for col in pivot_df.columns if col != 'Team'}))

            # Stacked bar chart per team per year
            stacked_bar_chart = alt.Chart(detailed_df).mark_bar().encode(
                x='Year:O',
                y='Cost:Q',
                color='Team:N',
                tooltip=['Team', 'Year', alt.Tooltip('Cost:Q', format=",.2f")]
            ).properties(
                title='Costs per Team per Year'
            )

            st.altair_chart(stacked_bar_chart, use_container_width=True)
# The rest of your application code (Summary Dashboard, Heatmap, Interactive Dashboard, What-If Analysis) remains unchanged.

# Summary Dashboard with Metrics
st.header("Summary Dashboard")

if st.session_state.teams:
    teams = st.session_state.teams  # For convenience

    total_cost_all_teams = sum(team.get('total_team_cost', 0) for team in teams)
    average_fte_per_team = round(np.mean([sum(role['count'] for role in team.get('team_roles', []) if role.get('count')) for team in teams]), 2)
    highest_cost_team = max(teams, key=lambda x: x.get('total_team_cost', 0))
    highest_cost_team_name = highest_cost_team['team_name'] or f"Team {teams.index(highest_cost_team)+1}"
    highest_cost = highest_cost_team.get('total_team_cost', 0)

    total_fte_all_teams = round(sum([sum(role['count'] for role in team.get('team_roles', []) if role.get('count')) for team in teams]), 2)
    total_roles = sum([len(team.get('team_roles', [])) for team in teams])

    # Create columns for metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Cost All Teams", f"${total_cost_all_teams:,.2f}")
    with col2:
        st.metric("Average FTE per Team", f"{average_fte_per_team:.2f}")
    with col3:
        st.metric("Highest Cost Team", f"{highest_cost_team_name} (${highest_cost:,.2f})")
    with col4:
        st.metric("Total FTE All Teams", f"{total_fte_all_teams:.2f}")
    with col5:
        st.metric("Total Number of Roles", f"{total_roles}")
else:
    st.info("No teams available to display summary metrics.")

# The rest of your application code (Heatmap, Interactive Dashboard, What-If Analysis) remains unchanged.
