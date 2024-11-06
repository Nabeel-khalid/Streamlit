# Import necessary libraries
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

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

# Define the number of weeks in each timeframe
timeframes = {
    'Week': 1,
    'Month': 4,
    'Quarter': 13,
    'Year': 52
}

# Function to calculate costs for a team
def calculate_team_cost(team_roles, duration_weeks):
    total_cost = 0
    for role_info in team_roles:
        role = role_info['role']
        count = role_info['count']
        hours_per_week = role_info['hours']
        resource_type = role_info['resource_type']
        rate = hourly_rates.get(role, {}).get(resource_type, 0)
        total_cost += count * hours_per_week * rate * duration_weeks
    return total_cost

# Streamlit UI
st.title("Team Cost Calculator with Gantt Chart")

# Sidebar for adjusting hourly rates
st.sidebar.header("Adjust Hourly Rates")
for role in hourly_rates.keys():
    st.sidebar.subheader(f"{role}")
    for resource_type in hourly_rates[role]:
        current_rate = hourly_rates[role][resource_type]
        new_rate = st.sidebar.number_input(
            f"{role} - {resource_type} Rate (USD/hour)",
            min_value=0,
            value=int(current_rate),
            step=1
        )
        hourly_rates[role][resource_type] = new_rate

# Define Teams
st.header("Define Teams")

num_teams = st.number_input("Number of Teams", min_value=1, value=1, step=1)

teams = []

# Create columns for input and display
input_col, display_col = st.columns(2)

with input_col:
    for i in range(int(num_teams)):
        st.subheader(f"Team {i+1}")
        team_name = st.text_input(f"Team {i+1} Name", value=f"Team {i+1}", key=f"team_{i}_name")
        team_description = st.text_area(f"Team {i+1} Description", key=f"team_{i}_description")

        # Team duration
        st.write("Team Duration")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(f"Team {i+1} Start Date", key=f"team_{i}_start_date")
        with col2:
            end_date = st.date_input(f"Team {i+1} End Date", key=f"team_{i}_end_date")

        duration_weeks = (end_date - start_date).days / 7
        if duration_weeks <= 0:
            st.error("End date must be after start date.")
            duration_weeks = 0

        # Define roles in the team
        num_roles = st.number_input(f"Number of Different Roles in Team {i+1}", min_value=1, value=1, step=1, key=f"team_{i}_num_roles")
        team_roles = []
        for j in range(int(num_roles)):
            st.write(f"Role {j+1} in Team {i+1}")
            role = st.selectbox(
                f"Select Role for Team {i+1}, Role {j+1}",
                options=list(hourly_rates.keys()),
                key=f"team_{i}_role_{j}"
            )
            count = st.number_input(
                f"Number of {role}s",
                min_value=0,
                value=0,
                step=1,
                key=f"team_{i}_role_{j}_count"
            )
            hours = st.number_input(
                f"Average weekly hours per {role}",
                min_value=0.0,
                value=40.0,
                step=0.1,
                key=f"team_{i}_role_{j}_hours"
            )
            resource_type = st.selectbox(
                f"Resource Type for {role}",
                options=['Onshore FTE', 'Offshore FTE', 'Onshore Professional Services', 'Offshore Professional Services'],
                key=f"team_{i}_role_{j}_resource_type"
            )
            team_roles.append({
                'role': role,
                'count': count,
                'hours': hours,
                'resource_type': resource_type
            })

        # Calculate team cost
        team_cost = calculate_team_cost(team_roles, duration_weeks)

        # Store team information
        teams.append({
            'team_name': team_name,
            'team_description': team_description,
            'start_date': start_date,
            'end_date': end_date,
            'duration_weeks': duration_weeks,
            'team_roles': team_roles,
            'team_cost': team_cost
        })

        # Display the teams in the right column
        with display_col:
            st.write(f"### Team {i+1} Summary")
            st.write(f"**Name**: {team_name}")
            st.write(f"**Description**: {team_description}")
            st.write(f"**Duration**: {start_date} to {end_date} ({duration_weeks:.1f} weeks)")
            st.write(f"**Total Cost**: ${team_cost:,.2f}")
            # Create a DataFrame for roles
            roles_data = []
            for role_info in team_roles:
                roles_data.append({
                    'Role': role_info['role'],
                    'Resource Type': role_info['resource_type'],
                    'Count': role_info['count'],
                    'Weekly Hours': role_info['hours']
                })
            roles_df = pd.DataFrame(roles_data)
            st.table(roles_df)
            st.write("---")

# Generate Gantt Chart
if st.button("Generate Gantt Chart"):
    if len(teams) == 0:
        st.error("Please define at least one team.")
    else:
        # Prepare data for Gantt chart
        gantt_data = []
        for team in teams:
            roles_list = []
            for role_info in team['team_roles']:
                count = role_info['count']
                role = role_info['role']
                resource_type = role_info['resource_type']
                roles_list.append(f"{count} x {role} ({resource_type})")
            roles_str = ", ".join(roles_list)
            team_name = team['team_name']
            team_cost = team['team_cost']
            team_description = team['team_description']
            start_date = team['start_date']
            end_date = team['end_date']
            gantt_data.append({
                'Team': team_name,
                'Start': start_date,
                'End': end_date,
                'Cost': team_cost,
                'Roles': roles_str,
                'Description': team_description
            })
        gantt_df = pd.DataFrame(gantt_data)

        # Create Gantt chart using Altair
        gantt_chart = alt.Chart(gantt_df).mark_bar().encode(
            x='Start:T',
            x2='End:T',
            y=alt.Y('Team:N', sort=alt.EncodingSortField(field='Start', order='ascending')),
            color='Cost:Q',
            tooltip=['Team', 'Start', 'End', 'Cost', 'Roles', 'Description']
        ).properties(
            title='Team Gantt Chart'
        )

        st.altair_chart(gantt_chart, use_container_width=True)

        # Show total cost per team
        st.write("## Team Costs")
        for team in teams:
            team_name = team['team_name']
            team_cost = team['team_cost']
            st.write(f"**{team_name}**: ${team_cost:,.2f}")
            roles_strings = []
            for role_info in team['team_roles']:
                count = role_info['count']
                role = role_info['role']
                resource_type = role_info['resource_type']
                roles_strings.append(f"{count} x {role} ({resource_type})")
            roles_description = ', '.join(roles_strings)
            st.write(f"Roles: {roles_description}")
            st.write("---")

# The rest of your financial impact and projections code remains the same
# (You can include it here if needed)

# Instructions to run the app
# Save this code to a file (e.g., `team_cost_calculator.py`) and run it using the command `streamlit run team_cost_calculator.py`.
