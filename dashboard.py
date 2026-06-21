import streamlit as st
import pandas as pd
import plotly.express as px

#Load Data from CSV
data = pd.read_csv("covid19dashboard.csv")

#heading of the dashboard
st.title("California COVID-19 Institutional Dashboard")
st.markdown(
    """
    This dashboard explores COVID-19 activity across reporting institutions over time.  
    The main questions are: What region was impacted the most?, Which institutions reported the highest confirmed cases?,
    How did activity change over time?, How severe were the cases of Covid-19 spread?
    """
)

# data cleaning and preprocessing
data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
numeric_cols = ["Latitude", "Longitude", "TotalConfirmed", "TotalDeaths"]
for col in numeric_cols:
    data[col] = pd.to_numeric(data[col], errors="coerce")

data = data.dropna(subset=["Date", "InstitutionName", "Latitude", "Longitude"])
data["Month"] = data["Date"].dt.to_period("M").astype(str)
data["DeathRate"] = data.apply(
    lambda r: (r["TotalDeaths"] / r["TotalConfirmed"] * 100) if r["TotalConfirmed"] > 0 else 0,
    axis=1
)

df = data


#Dashboard filters in the sidebar
st.sidebar.header("Dashboard Filters")

#adding date filter
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if start_date > end_date:
    st.sidebar.error("Start date must be before end date.")





#Tab Layout
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview", "Institution Comparison", "Time Trends", "Data Source"
])

with tab1:
    st.subheader("Geographic Distribution of COVID-19 Activity")
    st.caption("Each bubble represents an institution. Larger bubbles indicate higher values for the selected map metric.")
with tab2:
    st.subheader("Institution Comparison")
    st.caption("This section compares burden and severity across selected institutions using the most recent record in the selected date range.")
with tab3:
    st.subheader("Time Series Analysis")
    st.caption("The line chart shows how confirmed cases changed over time for the selected institutions.")
with tab4:
     st.subheader("Project Documentation")
