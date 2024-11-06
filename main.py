import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Title and Description
st.title("Year-on-Year Financial Modeling Calculator")
st.write("This calculator helps you model projects, revenue, EBITDA, and other metrics over multiple years.")

# Input Section
num_years = st.slider("Number of Years", 1, 10, 5)
num_projects = st.slider("Number of Projects", 1, 10, 3)

# Editable Dataframes for Yearly Projects and Metrics
data = []
for year in range(1, num_years + 1):
    yearly_data = {}
    yearly_data['Year'] = year
    for project in range(1, num_projects + 1):
        yearly_data[f'Project {project} Revenue'] = st.number_input(f"Year {year} - Project {project} Revenue", value=100000 * project, min_value=0)
        yearly_data[f'Project {project} EBITDA'] = st.number_input(f"Year {year} - Project {project} EBITDA", value=20000 * project, min_value=0)
        yearly_data[f'Project {project} Error Margin (%)'] = st.slider(f"Year {year} - Project {project} Error Margin (%)", 0, 100, 10)
    data.append(yearly_data)

# Convert Input Data into DataFrame
df = pd.DataFrame(data)

# Display Data
st.write("### Financial Data Table")
st.dataframe(df)

# Calculations for Graphs
revenue_columns = [col for col in df.columns if 'Revenue' in col]
ebitda_columns = [col for col in df.columns if 'EBITDA' in col]

total_revenue = df[revenue_columns].sum(axis=1)
total_ebitda = df[ebitda_columns].sum(axis=1)

# Plotting the Results
fig, ax = plt.subplots()
ax.plot(df['Year'], total_revenue, label='Total Revenue', marker='o')
ax.plot(df['Year'], total_ebitda, label='Total EBITDA', marker='o')
ax.set_xlabel('Year')
ax.set_ylabel('Amount')
ax.legend()

st.write("### Revenue and EBITDA Over Time")
st.pyplot(fig)

# Error Margin Adjustments
df['Revenue with Error Margin'] = total_revenue * (1 - df[[col for col in df.columns if 'Error Margin' in col]].mean(axis=1) / 100)

# Display Adjusted Revenue
df_result = df[['Year', 'Revenue with Error Margin']]
st.write("### Adjusted Revenue with Error Margin")
st.dataframe(df_result)
