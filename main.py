# Import necessary libraries
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

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

# Streamlit UI
st.title("Team Cost Calculator with Gantt Chart and Yearly Cost Summary")

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

# Create tabs for input and summary
tab1, tab2 = st.tabs(["Team Input", "Yearly Cost Summary"])

with tab1:
    for i in range(int(num_teams)):
        st.subheader(f"Team {i+1}")
        team_name = st.text_input(f"Team {i+1} Name", value=f"Team {i+1}", key=f"team_{i}_name")
        team_description = st.text_area(f"Team {i+1} Description", key=f"team_{i}_description")

        # Team duration with specific dates
        st.write("Team Duration")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(f"Team {i+1} Start Date", key=f"team_{i}_start_date")
        with col2:
            end_date = st.date_input(f"Team {i+1} End Date", key=f"team_{i}_end_date")

        if end_date <= start_date:
            st.error("End date must be after start date.")
            duration_weeks = 0
        else:
            duration_days = (end_date - start_date).days + 1
            duration_weeks = duration_days / 7

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
                value=1,
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

        # Calculate team cost per year
        cost_per_year = calculate_team_cost_per_year(team_roles, start_date, end_date)
        total_team_cost = sum(cost_per_year.values())

        # Store team information
        teams.append({
            'team_name': team_name,
            'team_description': team_description,
            'start_date': start_date,
            'end_date': end_date,
            'duration_weeks': duration_weeks,
            'team_roles': team_roles,
            'cost_per_year': cost_per_year,
            'total_team_cost': total_team_cost
        })

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
                team_cost = team['total_team_cost']
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
                color=alt.Color('Cost:Q', scale=alt.Scale(scheme='blues')),
                tooltip=['Team', 'Start', 'End', 'Cost', 'Roles', 'Description']
            ).properties(
                title='Team Gantt Chart'
            )

            # Add year markers to the Gantt chart
            min_date = gantt_df['Start'].min()
            max_date = gantt_df['End'].max()
            year_ticks = pd.date_range(start=min_date.replace(month=1, day=1), end=max_date, freq='YS').to_pydatetime()
            year_rule = alt.Chart(pd.DataFrame({'year': year_ticks})).mark_rule(strokeDash=[5,5], color='gray').encode(
                x='year:T'
            )

            st.altair_chart(gantt_chart + year_rule, use_container_width=True)

            # Show total cost per team
            st.write("## Team Costs")
            for team in teams:
                team_name = team['team_name']
                total_team_cost = team['total_team_cost']
                st.write(f"**{team_name}**: ${total_team_cost:,.2f}")
                roles_strings = []
                for role_info in team['team_roles']:
                    count = role_info['count']
                    role = role_info['role']
                    resource_type = role_info['resource_type']
                    roles_strings.append(f"{count} x {role} ({resource_type})")
                roles_description = ', '.join(roles_strings)
                st.write(f"Roles: {roles_description}")
                st.write("---")

with tab2:
    st.header("Yearly Cost Summary")

    if len(teams) == 0:
        st.write("No teams defined yet.")
    else:
        # Aggregate costs per year across all teams
        all_years = []
        for team in teams:
            all_years.extend(team['cost_per_year'].keys())
        all_years = sorted(set(all_years))

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
            team_name = team['team_name']
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
