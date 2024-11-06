# Import necessary libraries
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# Set Streamlit configuration for dark mode and custom colors
st.set_page_config(
    page_title="Team Cost Calculator",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for dark mode and turquoise highlight colors
st.markdown(
    """
    <style>
    .stApp {
        background-color: #fefefe;
        color: #999999;
    }
    .stButton > button, .stDownloadButton > button {
        background-color: #1abc9c;
        color: #ffffff;
        border-radius: 10px;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #16a085;
    }
    .st-sidebar {
        background-color: #0e1117;
    }
    .stSelectbox, .stNumberInput, .stTextInput, .stDateInput, .stTextArea {
        color: #000000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# Streamlit UI
st.title("Team Cost Calculator with Gantt Chart and Yearly Cost Summary")

# Sidebar for adjusting hourly rates
with st.sidebar:
    st.header("Adjust Hourly Rates")
    for role in hourly_rates.keys():
        with st.expander(f"{role} Rates"):
            for resource_type in hourly_rates[role]:
                current_rate = hourly_rates[role][resource_type]
                new_rate = st.number_input(
                    f"{resource_type}",
                    min_value=0,
                    value=int(current_rate),
                    step=1,
                    key=f"{role}_{resource_type}"
                )
                hourly_rates[role][resource_type] = new_rate

# Initialize session state for teams
if 'teams' not in st.session_state:
    st.session_state.teams = []

# Function to add a new team
def add_team():
    st.session_state.teams.append({
        'team_name': '',
        'team_description': '',
        'start_date': None,
        'end_date': None,
        'duration_weeks': 0,
        'team_roles': [],
        'cost_per_year': {},
        'total_team_cost': 0
    })

# Add Team Button
if st.button("Add New Team"):
    add_team()

# Add Demo Teams
if st.button("Add Demo Teams"):
    demo_teams = [
        {
            'team_name': 'Product Team',
            'team_description': 'Handles product management and development.',
            'start_date': datetime(2024, 1, 1),
            'end_date': datetime(2029, 12, 31),
            'duration_weeks': 0,
            'team_roles': [
                {'role': 'Product Manager', 'count': 2, 'hours': 40, 'resource_type': 'Onshore FTE'},
                {'role': 'UX Designers', 'count': 1, 'hours': 40, 'resource_type': 'Offshore FTE'}
            ],
            'cost_per_year': {},
            'total_team_cost': 0
        },
        {
            'team_name': 'Operations Team',
            'team_description': 'Responsible for operational tasks and management.',
            'start_date': datetime(2024, 1, 1),
            'end_date': datetime(2029, 12, 31),
            'duration_weeks': 0,
            'team_roles': [
                {'role': 'Management', 'count': 1, 'hours': 40, 'resource_type': 'Onshore FTE'},
                {'role': 'Scrum Masters', 'count': 1, 'hours': 40, 'resource_type': 'Offshore FTE'}
            ],
            'cost_per_year': {},
            'total_team_cost': 0
        },
        {
            'team_name': 'Development Team',
            'team_description': 'Handles software development and infrastructure.',
            'start_date': datetime(2024, 1, 1),
            'end_date': datetime(2029, 12, 31),
            'duration_weeks': 0,
            'team_roles': [
                {'role': 'Core Dev, Data Science & Infra', 'count': 3, 'hours': 40, 'resource_type': 'Onshore FTE'},
                {'role': 'QA', 'count': 2, 'hours': 40, 'resource_type': 'Offshore FTE'}
            ],
            'cost_per_year': {},
            'total_team_cost': 0
        },
        {
            'team_name': 'Support Team',
            'team_description': 'Provides product support and specialist knowledge.',
            'start_date': datetime(2024, 1, 1),
            'end_date': datetime(2029, 12, 31),
            'duration_weeks': 0,
            'team_roles': [
                {'role': 'Product Specialists', 'count': 2, 'hours': 40, 'resource_type': 'Onshore FTE'},
                {'role': 'QA', 'count': 1, 'hours': 40, 'resource_type': 'Offshore FTE'}
            ],
            'cost_per_year': {},
            'total_team_cost': 0
        }
    ]
    st.session_state.teams.extend(demo_teams)

# Display existing teams and allow editing
for idx, team in enumerate(st.session_state.teams):
    with st.expander(f"Team {idx+1} Details", expanded=True):
        # Team Name and Description
        team['team_name'] = st.text_input(f"Team {idx+1} Name", value=team['team_name'], key=f"team_{idx}_name")
        team['team_description'] = st.text_area(f"Team {idx+1} Description", value=team['team_description'], key=f"team_{idx}_description")

        # Team Duration
        st.write("Team Duration")
        col1, col2 = st.columns(2)
        with col1:
            team['start_date'] = st.date_input(f"Team {idx+1} Start Date", value=team['start_date'], key=f"team_{idx}_start_date")
        with col2:
            team['end_date'] = st.date_input(f"Team {idx+1} End Date", value=team['end_date'], key=f"team_{idx}_end_date")

        if team['end_date'] and team['start_date']:
            if team['end_date'] <= team['start_date']:
                st.error("End date must be after start date.")
                team['duration_weeks'] = 0
            else:
                duration_days = (team['end_date'] - team['start_date']).days + 1
                team['duration_weeks'] = duration_days / 7

        # Define Roles in Team
        st.write("### Roles in Team")
        num_roles = st.number_input(f"Number of Different Roles in Team {idx+1}", min_value=1, value=len(team['team_roles']) if team['team_roles'] else 1, step=1, key=f"team_{idx}_num_roles")

        # Ensure team_roles list matches num_roles
        while len(team['team_roles']) < num_roles:
            team['team_roles'].append({'role': '', 'count': 0, 'hours': 0, 'resource_type': ''})
        while len(team['team_roles']) > num_roles:
            team['team_roles'].pop()

        for j in range(int(num_roles)):
            st.write(f"**Role {j+1} in Team {idx+1}**")
            role_info = team['team_roles'][j]
            role_info['role'] = st.selectbox(
                f"Select Role",
                options=list(hourly_rates.keys()),
                index=list(hourly_rates.keys()).index(role_info['role']) if role_info['role'] in hourly_rates else 0,
                key=f"team_{idx}_role_{j}"
            )
            role_info['count'] = st.number_input(
                f"Number of {role_info['role']}s",
                min_value=0,
                value=int(role_info['count']),
                step=1,
                key=f"team_{idx}_role_{j}_count"
            )
            role_info['hours'] = st.number_input(
                f"Average weekly hours per {role_info['role']}",
                min_value=0.0,
                value=float(role_info['hours']),
                step=0.1,
                key=f"team_{idx}_role_{j}_hours"
            )
            resource_types = list(hourly_rates.get(role_info['role'], {}).keys())
            if resource_types:
                role_info['resource_type'] = st.selectbox(
                    f"Resource Type for {role_info['role']}",
                    options=resource_types,
                    index=resource_types.index(role_info['resource_type']) if role_info['resource_type'] in resource_types else 0,
                    key=f"team_{idx}_role_{j}_resource_type"
                )
            else:
                st.error(f"No resource types available for {role_info['role']}")

# Display Team Summaries
st.header("Current Team Structure")
if st.session_state.teams:
    for idx, team in enumerate(st.session_state.teams):
        st.subheader(f"{team['team_name'] or f'Team {idx+1}'}")
        st.write(f"**Description**: {team['team_description']}")
        if team['start_date'] and team['end_date']:
            st.write(f"**Duration**: {team['start_date']} to {team['end_date']} ({team['duration_weeks']:.1f} weeks)")
        else:
            st.write("**Duration**: Not specified")
        # Display Roles
        if team['team_roles']:
            roles_data = []
            for role_info in team['team_roles']:
                roles_data.append({
                    'Role': role_info['role'],
                    'Resource Type': role_info['resource_type'],
                    'Count': role_info['count'],
                    'Weekly Hours': role_info['hours']
                })
            roles_df = pd.DataFrame(roles_data)
            st.table(roles_df)
        else:
            st.write("No roles defined for this team.")
        st.write("---")
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
                'Description': team_description
            })

            all_years.update(team['cost_per_year'].keys())

        if not gantt_data:
            st.error("No complete teams to display.")
        else:
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

            # Add download button for detailed cost breakdown
            st.subheader("Download Detailed Cost Breakdown")
            detailed_csv = detailed_df.to_csv(index=False)
            st.download_button(
                label="Download Detailed Costs as CSV",
                data=detailed_csv,
                file_name='detailed_costs_per_team.csv',
                mime='text/csv'
            )

# Instructions to run the app
# Save this code to a file (e.g., `team_cost_calculator.py`) and run it using the command `streamlit run team_cost_calculator.py`.
