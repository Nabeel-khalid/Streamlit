# Import necessary libraries
import pandas as pd
import altair as alt

# Define hourly rates for each role (in USD)
hourly_rates = {
    'Developer': 50,
    'Product Manager': 60,
    'Designer': 45,
    'Growth Expert': 55,
    'Data Scientist': 65,
    'QA Engineer': 40
}

# Define the number of weeks in each timeframe
timeframes = {
    'Week': 1,
    'Month': 4,
    'Quarter': 13,
    'Year': 52
}

# Function to calculate costs
def calculate_costs(team):
    costs = {}
    for timeframe, weeks in timeframes.items():
        total_cost = 0
        for role, details in team.items():
            num_people = details['count']
            weekly_hours = details['hours']
            rate = hourly_rates.get(role, 0)
            total_cost += num_people * weekly_hours * rate * weeks
        costs[timeframe] = total_cost
    return costs

# Streamlit UI
streamlit.title("Team Cost Calculator")

# Sidebar for defining new roles and adjusting hourly rates
streamlit.sidebar.header("Manage Roles and Hourly Rates")
new_role = streamlit.sidebar.text_input("Add New Role")
new_rate = streamlit.sidebar.number_input("Hourly Rate for New Role", min_value=0, value=0, step=1)
if streamlit.sidebar.button("Add Role"):
    if new_role and new_rate > 0:
        hourly_rates[new_role] = new_rate

# Allow updating of existing hourly rates
streamlit.sidebar.subheader("Adjust Hourly Rates")
for role in list(hourly_rates.keys()):
    new_rate = streamlit.sidebar.number_input(f"Hourly Rate for {role}", min_value=0, value=hourly_rates[role], step=1)
    hourly_rates[role] = new_rate

# User input for team configuration (in two columns)
streamlit.write("Enter the number of professionals and average weekly hours for each role:")
col1, col2 = streamlit.columns(2)
team = {}
for role in hourly_rates.keys():
    with col1:
        count = streamlit.number_input(f"Number of {role}s", min_value=0, value=0, step=1, key=f"{role}_count")
    with col2:
        hours = streamlit.number_input(f"Average weekly hours per {role}", min_value=0.0, value=0.0, step=0.1, key=f"{role}_hours")
    team[role] = {'count': count, 'hours': hours}

# User input for financial impact
streamlit.header("Financial Impact")
revenue = streamlit.number_input("Revenue (USD)", min_value=0, value=0, step=1000)

# Historical EBITA data (example value)
historical_ebita = 5000

taxes = streamlit.number_input("Taxes (USD, included in EBITA)", min_value=0, value=0, step=100)
ebita = streamlit.number_input(f"EBITA (USD, historical value: ${historical_ebita})", min_value=0, value=historical_ebita, step=100)
net_positive = revenue - ebita

# User input for Year-on-Year projections
streamlit.header("Year-on-Year Financial Projections")
years = streamlit.slider("Select number of years for projection", min_value=5, max_value=10, value=5)
new_clients_per_year = streamlit.number_input("Net New Clients per Year", min_value=0, value=0, step=1)
average_client_revenue = streamlit.number_input("Average Revenue per New Client (USD)", min_value=0, value=10000, step=1000)
client_costs = streamlit.number_input("Estimated Costs per Client (USD)", min_value=0, value=5000, step=100)

# Calculate year-on-year projections
yoy_data = []
current_revenue = revenue
current_net_positive = net_positive
for year in range(1, years + 1):
    new_revenue = new_clients_per_year * average_client_revenue
    new_costs = new_clients_per_year * client_costs
    current_revenue += new_revenue
    current_net_positive += (new_revenue - new_costs - ebita)
    yoy_data.append({
        'Year': f'Year {year}',
        'Net Positive': current_net_positive
    })

# Convert data to DataFrame for plotting
yoy_df = pd.DataFrame(yoy_data)

# Plot the Year-on-Year financial projection using Altair
yoy_chart = alt.Chart(yoy_df).mark_line(point=True).encode(
    x='Year',
    y='Net Positive',
    tooltip=['Year', 'Net Positive']
).properties(
    title='Year-on-Year Net Positive Financial Impact'
)

# Add variance as an area chart
yoy_chart += alt.Chart(yoy_df).mark_area(opacity=0.3).encode(
    x='Year',
    y='Net Positive'
)

streamlit.altair_chart(yoy_chart, use_container_width=True)

# Calculate costs
if streamlit.button("Calculate Costs"):
    costs = calculate_costs(team)
    streamlit.write("## Cost Breakdown:")
    for timeframe, cost in costs.items():
        streamlit.write(f"{timeframe}: ${cost:,.2f}")
    
    # Create a DataFrame for plotting
    cost_df = pd.DataFrame(list(costs.items()), columns=['Timeframe', 'Cost'])
    
    # Plot the cost breakdown using Altair
    cost_chart = alt.Chart(cost_df).mark_bar().encode(
        x='Timeframe',
        y='Cost',
        tooltip=['Timeframe', 'Cost']
    ).properties(
        title='Cost Breakdown by Timeframe'
    )
    streamlit.altair_chart(cost_chart, use_container_width=True)

    # Show net positive financial impact
    streamlit.write("## Net Positive Financial Impact")
    streamlit.write(f"Net Positive: ${net_positive:,.2f}")

    # Create a YOY graph for financial impact
    financial_df = pd.DataFrame({
        'Category': ['Revenue', 'Taxes', 'EBITA', 'Net Positive'],
        'Value': [revenue, taxes, ebita, net_positive]
    })
    yoy_chart = alt.Chart(financial_df).mark_bar().encode(
        x='Category',
        y='Value',
        tooltip=['Category', 'Value']
    ).properties(
        title='Year Over Year Financial Impact'
    )
    streamlit.altair_chart(yoy_chart, use_container_width=True)

# Instructions to run the app
# Save this code to a file (e.g., `team_cost_calculator.py`) and run it using the command `streamlit run team_cost_calculator.py`.
