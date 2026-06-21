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
