# Import necessary libraries
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import random
import json
from datetime import datetime, date, timedelta

# Streamlit UI
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

# Function to calculate costs for a team per year
def calculate_team_cost_per_year(team_roles, start_date, end_date):
    total_cost = 0
    cost_per_year = {}
    # Convert start_date and end_date to pd.Timestamp
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    duration_days = (end_date - start_date).days + 1  # Include end date
    duration_weeks = duration_days / 7

    # Generate a list of dates from start to end
    date_range = pd.date_range(start=start_date, end=end_date)
    years = date_range.year.unique()

    for year in years:
        # Calculate the overlapping days in this year
        year_start = pd.Timestamp(f"{year}-01-01")
        year_end = pd.Timestamp(f"{year}-12-31")

        # Adjust the start and end dates for the overlap
        overlap_start = max(start_date, year_start)
        overlap_end = min(end_date, year_end)
        overlap_days = (overlap_end - overlap_start).days + 1

        overlap_weeks = overlap_days / 7

        yearly_cost = 0
        for role_info in team_roles:
            role = role_info['role']
            count = role_info['count']
            hours_per_week = role_info['hours']
            resource_type = role_info['resource_type']
            rate = hourly_rates.get(role, {}).get(resource_type, 0)
            yearly_cost += count * hours_per_week * rate * overlap_weeks

        cost_per_year[year] = yearly_cost

    return cost_per_year

# Function to calculate cost breakdown by role
def calculate_role_costs(team_roles, start_date, end_date):
    # Convert start_date and end_date to pd.Timestamp
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    duration_days = (end_date - start_date).days + 1  # Include end date
    duration_weeks = duration_days / 7

    role_costs = {}
    for role_info in team_roles:
        role = role_info['role']
        count = role_info['count']
        hours_per_week = role_info['hours']
        resource_type = role_info['resource_type']
        rate = hourly_rates.get(role, {}).get(resource_type, 0)
        cost = count * hours_per_week * rate * duration_weeks
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
            count = random.randint(1, 5)
            hours = random.choice([20, 30, 40])
            team_roles.append({
                'role': role,
                'count': count,
                'hours': hours,
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

# Sidebar for adjusting hourly rates and data import/export
with st.sidebar:
    st.header("Settings")
    with st.sidebar.expander("Adjust Hourly Rates"):
        for role in hourly_rates.keys():
            with st.sidebar.expander(f"{role} Rates"):
                for resource_type in hourly_rates[role]:
                    current_rate = hourly_rates[role][resource_type]
                    new_rate = st.number_input(
                        f"{resource_type} ({role})",
                        min_value=0,
                        value=int(current_rate),
                        step=1,
                        key=f"{role}_{resource_type}"
                    )
                    hourly_rates[role][resource_type] = new_rate

    st.header("Data Import/Export")

    # Export Teams
    if st.button('Export Teams'):
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
                for role_info in team_copy['team_roles']:
                    role_info_copy = role_info.copy()
                    team_roles_copy.append(role_info_copy)
                team_copy['team_roles'] = team_roles_copy
                teams_copy.append(team_copy)

            teams_json = json.dumps(teams_copy, indent=4)
            st.download_button('Download Teams Data', data=teams_json, file_name='teams_data.json', mime='application/json')
        else:
            st.info("No teams to export.")

    # Import Teams
    uploaded_file = st.file_uploader("Upload Teams Data", type=['json'])
    if uploaded_file is not None:
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

        st.session_state.teams = teams_data
        st.success("Teams data uploaded successfully.")

    # Reset Teams
    if st.button('Reset All Teams'):
        st.session_state.teams = []
        st.success("All teams have been reset.")

    # Generate Demo Teams
    if st.button('Generate Demo Teams'):
        st.session_state.teams = generate_demo_teams()
        st.success("Demo teams have been generated.")

    # Save Session
    if st.button('Save Session'):
        session_data = {
            'teams': st.session_state.teams,
            'hourly_rates': hourly_rates
        }
        session_json = json.dumps(session_data, indent=4)
        st.download_button('Download Session Data', data=session_json, file_name='session_data.json', mime='application/json')
        st.success("Session data saved successfully.")

# Initialize session state for teams
if 'teams' not in st.session_state:
    st.session_state.teams = []

# Function to add a new team
def add_team():
    st.session_state.teams.append({
        'team_name': '',
        'team_description': '',
        'start_date': date.today(),
        'end_date': date.today() + timedelta(days=30),
        'duration_weeks': 0,
        'team_roles': [],
        'cost_per_year': {},
        'total_team_cost': 0
    })

# Add Team Button
if st.button("Add New Team"):
    add_team()

# Display existing teams and allow editing
if st.session_state.teams:
    team_tabs = st.tabs([team['team_name'] or f"Team {idx+1}" for idx, team in enumerate(st.session_state.teams)])
    for idx, (team, team_tab) in enumerate(zip(st.session_state.teams, team_tabs)):
        with team_tab:
            # Collapsible Sections
            with st.expander("Team Details", expanded=True):
                # Team Name and Description
                team['team_name'] = st.text_input(f"Team Name", value=team['team_name'], key=f"team_{idx}_name")
                team['team_description'] = st.text_area(f"Team Description", value=team['team_description'], key=f"team_{idx}_description")

            with st.expander("Team Duration", expanded=True):
                # Team Duration
                col1, col2 = st.columns(2)
                with col1:
                    team['start_date'] = st.date_input(f"Start Date", value=team['start_date'], key=f"team_{idx}_start_date")
                with col2:
                    team['end_date'] = st.date_input(f"End Date", value=team['end_date'], key=f"team_{idx}_end_date")

                if team['end_date'] and team['start_date']:
                    if team['end_date'] <= team['start_date']:
                        st.error("End date must be after start date.")
                        team['duration_weeks'] = 0
                    else:
                        duration_days = (team['end_date'] - team['start_date']).days + 1
                        team['duration_weeks'] = duration_days / 7

            with st.expander("Roles in Team", expanded=True):
                # Define Roles in Team
                num_roles = st.number_input(f"Number of Different Roles", min_value=1, value=len(team['team_roles']) if team['team_roles'] else 1, step=1, key=f"team_{idx}_num_roles")

                # Ensure team_roles list matches num_roles
                while len(team['team_roles']) < num_roles:
                    team['team_roles'].append({'role': '', 'count': 0, 'hours': 0, 'resource_type': ''})
                while len(team['team_roles']) > num_roles:
                    team['team_roles'].pop()

                for j in range(int(num_roles)):
                    st.write(f"**Role {j+1}**")
                    role_info = team['team_roles'][j]
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        role_info['role'] = st.selectbox(
                            f"Role",
                            options=list(hourly_rates.keys()),
                            index=list(hourly_rates.keys()).index(role_info['role']) if role_info['role'] in hourly_rates else 0,
                            key=f"team_{idx}_role_{j}"
                        )
                    with col2:
                        resource_types = list(hourly_rates.get(role_info['role'], {}).keys())
                        if resource_types:
                            role_info['resource_type'] = st.selectbox(
                                f"Resource Type",
                                options=resource_types,
                                index=resource_types.index(role_info['resource_type']) if role_info['resource_type'] in resource_types else 0,
                                key=f"team_{idx}_role_{j}_resource_type"
                            )
                        else:
                            st.error(f"No resource types available for {role_info['role']}")
                    with col3:
                        role_info['count'] = st.number_input(
                            f"Count",
                            min_value=0,
                            value=int(role_info['count']),
                            step=1,
                            key=f"team_{idx}_role_{j}_count"
                        )
                    with col4:
                        role_info['hours'] = st.number_input(
                            f"Weekly Hours",
                            min_value=0.0,
                            value=float(role_info['hours']),
                            step=0.1,
                            key=f"team_{idx}_role_{j}_hours"
                        )

            # Delete Team Button
            if st.button('Delete Team', key=f'delete_team_{idx}'):
                del st.session_state.teams[idx]
                st.experimental_rerun()
else:
    st.write("No teams defined yet.")

# Generate Gantt Chart and Cost Summaries
if st.button("Generate Gantt Chart and Cost Summary"):
    teams = st.session_state.teams
    if not teams:
        st.error("Please define at least one team.")
    else:
        # Calculate costs and prepare data
        gantt_data = []
        all_years = set()
        for team in teams:
            if not team['start_date'] or not team['end_date'] or not team['team_roles']:
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
            team_name = team['team_name'] or f"Team {teams.index(team)+1}"
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

            # Add interactive pie chart on hover
            selection = alt.selection_single(fields=['Team'], nearest=True, on='mouseover', empty='none')

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
                color=alt.Color('Role:N', legend=alt.Legend(title="Roles")),
                tooltip=[alt.Tooltip('Role:N'), alt.Tooltip('Cost:Q', format='$,.2f')]
            ).properties(
                width=200,
                height=200
            )

            gantt_chart = alt.layer(bars).add_selection(selection)

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

# Instructions to run the app
# Save this code to a file (e.g., `team_cost_calculator.py`) and run it using the command `streamlit run team_cost_calculator.py`.
