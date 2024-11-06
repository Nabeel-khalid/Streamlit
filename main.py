# Import necessary libraries
import streamlit as st
import pandas as pd
import altair as alt

# Define the roles and their rates
hourly_rates = {
    "Management": {
        "Onshore FTE": 263,
        "Offshore FTE": 131,
        "Onshore Professional Services": 394,
        "Offshore Professional Services": 197,
    },
    "Product Manager": {
        "Onshore FTE": 140,
        "Offshore FTE": 105,
        "Onshore Professional Services": 175,
        "Offshore Professional Services": 123,
    },
    "Product Specialists": {
        "Onshore FTE": 140,
        "Offshore FTE": 88,
        "Onshore Professional Services": 175,
        "Offshore Professional Services": 123,
    },
    "Core Dev, Data Science & Infra": {
        "Onshore FTE": 175,
        "Offshore FTE": 123,
        "Onshore Professional Services": 228,
        "Offshore Professional Services": 140,
    },
    "QA": {
        "Onshore FTE": 140,
        "Offshore FTE": 88,
        "Onshore Professional Services": 175,
        "Offshore Professional Services": 123,
    },
    "UX Designers": {
        "Onshore FTE": 175,
        "Offshore FTE": 123,
        "Onshore Professional Services": 228,
        "Offshore Professional Services": 140,
    },
    "Scrum Masters": {
        "Onshore FTE": 140,
        "Offshore FTE": 105,
        "Onshore Professional Services": 175,
        "Offshore Professional Services": 123,
    },
}

# Define the number of weeks in each timeframe
timeframes = {"Week": 1, "Month": 4, "Quarter": 13, "Year": 52}

# Function to calculate costs
def calculate_costs(team):
    costs = {}
    for timeframe, weeks in timeframes.items():
        total_cost = 0
        for role, details in team.items():
            num_people = details["count"]
            weekly_hours = details["hours"]
            resource_type = details["resource_type"]
            rate = hourly_rates.get(role, {}).get(resource_type, 0)
            total_cost += num_people * weekly_hours * rate * weeks
        costs[timeframe] = total_cost
    return costs

# Streamlit UI
st.title("Team Cost Calculator")

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
            step=1,
        )
        hourly_rates[role][resource_type] = new_rate

# User input for team configuration
st.write(
    "Enter the number of professionals, average weekly hours, and resource type for each role:"
)

team = {}

cols = st.columns(2)
for i, role in enumerate(hourly_rates.keys()):
    with cols[i % 2]:
        st.subheader(role)
        count = st.number_input(
            f"Number of {role}s", min_value=0, value=0, step=1, key=f"{role}_count"
        )
        hours = st.number_input(
            f"Average weekly hours per {role}",
            min_value=0.0,
            value=0.0,
            step=0.1,
            key=f"{role}_hours",
        )
        resource_type = st.selectbox(
            f"Resource Type for {role}",
            options=[
                "Onshore FTE",
                "Offshore FTE",
                "Onshore Professional Services",
                "Offshore Professional Services",
            ],
            key=f"{role}_resource_type",
        )
        team[role] = {"count": count, "hours": hours, "resource_type": resource_type}

# User input for financial impact
st.header("Financial Impact")
revenue = st.number_input("Revenue (USD)", min_value=0, value=0, step=1000)
historical_ebita = 5000
taxes = st.number_input("Taxes (USD, included in EBITA)", min_value=0, value=0, step=100)
ebita = st.number_input(
    f"EBITA (USD, historical value: ${historical_ebita})",
    min_value=0,
    value=historical_ebita,
    step=100,
)
net_positive = revenue - ebita - taxes

# User input for additional costs
st.header("Additional Costs")
marketing_costs = st.number_input("Marketing Costs (USD)", min_value=0, value=0, step=100)
operational_costs = st.number_input("Operational Costs (USD)", min_value=0, value=0, step=100)
office_rent = st.number_input("Office Rent (USD)", min_value=0, value=0, step=100)
insurance_costs = st.number_input("Insurance Costs (USD)", min_value=0, value=0, step=100)
other_costs = st.number_input("Other Miscellaneous Costs (USD)", min_value=0, value=0, step=100)

total_additional_costs = marketing_costs + operational_costs + office_rent + insurance_costs + other_costs
net_positive -= total_additional_costs

# User input for Year-on-Year projections
st.header("Year-on-Year Financial Projections")
years = st.slider(
    "Select number of years for projection", min_value=5, max_value=10, value=5
)
new_clients_per_year = st.number_input(
    "Net New Clients per Year", min_value=0, value=0, step=1
)
average_client_revenue = st.number_input(
    "Average Revenue per New Client (USD)", min_value=0, value=10000, step=1000
)
client_costs = st.number_input(
    "Estimated Costs per Client (USD)", min_value=0, value=5000, step=100
)

# Calculate year-on-year projections
yoy_data = []
current_revenue = revenue
current_net_positive = net_positive
for year in range(1, years + 1):
    new_revenue = new_clients_per_year * average_client_revenue
    new_costs = new_clients_per_year * client_costs
    current_revenue += new_revenue
    current_net_positive += new_revenue - new_costs - ebita - total_additional_costs
    yoy_data.append({"Year": f"Year {year}", "Net Positive": current_net_positive})

# Convert data to DataFrame for plotting
yoy_df = pd.DataFrame(yoy_data)

# Plot the Year-on-Year financial projection using Altair
yoy_chart = (
    alt.Chart(yoy_df)
    .mark_line(point=True)
    .encode(x="Year", y="Net Positive", tooltip=["Year", "Net Positive"])
    .properties(title="Year-on-Year Net Positive Financial Impact")
)

# Add variance as an area chart
yoy_chart += alt.Chart(yoy_df).mark_area(opacity=0.3).encode(x="Year", y="Net Positive")

st.altair_chart(yoy_chart, use_container_width=True)

# Calculate costs
if st.button("Calculate Costs"):
    costs = calculate_costs(team)
    st.write("## Cost Breakdown:")
    for timeframe, cost in costs.items():
        st.write(f"{timeframe}: ${cost:,.2f}")
    # Create a DataFrame for plotting
    cost_df = pd.DataFrame(list(costs.items()), columns=["Timeframe", "Cost"])
    # Plot the cost breakdown using Altair
    cost_chart = (
        alt.Chart(cost_df)
        .mark_bar()
        .encode(x="Timeframe", y="Cost", tooltip=["Timeframe", "Cost"])
        .properties(title="Cost Breakdown by Timeframe")
    )
    st.altair_chart(cost_chart, use_container_width=True)
    # Show net positive financial impact
    st.write("## Net Positive Financial Impact")
    st.write(f"Net Positive: ${net_positive:,.2f}")
    # Create a YOY graph for financial impact
    financial_df = pd.DataFrame(
        {
            "Category": ["Revenue", "Taxes", "EBITA", "Additional Costs", "Net Positive"],
            "Value": [revenue, taxes, ebita, total_additional_costs, net_positive],
        }
    )
    yoy_chart = (
        alt.Chart(financial_df)
        .mark_bar()
        .encode(x="Category", y="Value", tooltip=["Category", "Value"])
        .properties(title="Year Over Year Financial Impact")
    )
    st.altair_chart(yoy_chart, use_container_width=True)

    # Option to save the cost breakdown as a CSV
    if st.button("Download Cost Breakdown as CSV"):
        cost_df.to_csv("cost_breakdown.csv", index=False)
        st.write("Cost breakdown saved as 'cost_breakdown.csv'.")

# Instructions to run the app
# Save this code to a file (e.g., `team_cost_calculator.py`) and run it using the command `streamlit run team_cost_calculator.py`.
