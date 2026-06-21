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

institutions = sorted(df["InstitutionName"].dropna().unique())
selected_institutions = st.sidebar.multiselect(
    "Select institution(s)",
    institutions, default=institutions
)

metric_choice = st.sidebar.selectbox(
    "Map show", ["TotalConfirmed", "TotalDeaths"]
)

#Apply filters to the dataframe
filtered_df = df[
    (df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date) &
    (df["InstitutionName"].isin(selected_institutions))
].copy()

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# Use latest record per institution for institution-level KPIs and map
latest_idx = filtered_df.groupby("InstitutionName")["Date"].idxmax()
latest_df = filtered_df.loc[latest_idx].copy()


#KPI Section
st.subheader("Key Performance Indicators")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric("Total Institutions", latest_df["InstitutionName"].nunique())
kpi2.metric("Total Confirmed Cases", f"{int(latest_df['TotalConfirmed'].sum()):,}")
kpi3.metric("Total Deaths", f"{int(latest_df['TotalDeaths'].sum()):,}")



#Tab Layout
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview", "Institution Comparison", "Time Trends", "Data Source"
])

with tab1:
    st.subheader("Geographic Distribution of COVID-19 Activity")
    st.caption("Each bubble represents an institution. Larger bubbles indicate higher values for the selected map metric.")

     
    map = px.scatter_mapbox(
        latest_df,
        lat="Latitude",
        lon="Longitude",
        size=metric_choice,
        color="TotalConfirmed",
        hover_name="InstitutionName",
        hover_data={
            "TotalConfirmed": ":,",
            "TotalDeaths": ":,",
            "Latitude": False,
            "Longitude": False
        },
        zoom=4,
        height=560,
        color_continuous_scale="Reds"
    )
    map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(map, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10Institutions by Confirmed Cases")
        top_confirmed = latest_df.sort_values("TotalConfirmed", ascending=False).head(10)
        fig_bar = px.bar(
            top_confirmed,
            x="TotalConfirmed",
            y="InstitutionName",
            orientation="h",
            text="TotalConfirmed",
            labels={"TotalConfirmed": "Confirmed Cases", "InstitutionName": "Institution"},
            template="plotly_white"
        )
        fig_bar.update_layout(yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("Reported Deaths by Institution")
        top_deaths = latest_df.sort_values("TotalDeaths", ascending=False).head(10)
        fig_pie = px.pie(
            top_deaths,
            values="TotalDeaths",
            names="InstitutionName",
            hole=0.45,
            template="plotly_white"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
with tab2:
    st.subheader("Institution Comparison")
    st.caption("This section compares burden and severity across selected institutions using the most recent record in the selected date range.")

    comparison_metric = st.radio(
        "Choose comparison metric",
        ["TotalConfirmed", "TotalDeaths", "DeathRate"],
        horizontal=True
    )

    compare_df = latest_df.sort_values(comparison_metric, ascending=False)
    fig_compare = px.bar(
        compare_df,
        x="InstitutionName",
        y=comparison_metric,
        color=comparison_metric,
        text=comparison_metric,
        labels={"InstitutionName": "Institution", comparison_metric: comparison_metric.replace("Total", "Total ")},
        template="plotly_white"
    )
    fig_compare.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_compare, use_container_width=True)
with tab3:
    st.subheader("Time Series Analysis")
    st.caption("The line chart shows how confirmed cases changed over time for the selected institutions.")
    trend_level = st.selectbox("View trend by", ["Overall", "Institution"])

    if trend_level == "Overall":
        trend_df = filtered_df.groupby("Date", as_index=False)[["TotalConfirmed", "TotalDeaths"]].sum()
        fig_line = px.line(
            trend_df,
            x="Date",
            y=["TotalConfirmed", "TotalDeaths"],
            markers=False,
            template="plotly_white",
            labels={"value": "Count", "variable": "Metric"}
        )
    else:
        trend_df = filtered_df.groupby(["Date", "InstitutionName"], as_index=False)["TotalConfirmed"].sum()
        fig_line = px.line(
            trend_df,
            x="Date",
            y="TotalConfirmed",
            color="InstitutionName",
            template="plotly_white",
            labels={"TotalConfirmed": "Confirmed Cases", "InstitutionName": "Institution"}
        )
    st.plotly_chart(fig_line, use_container_width=True)
with tab4:
    st.subheader("Project Documentation")
    st.markdown("Reference: https://catalog.data.gov/dataset/cdcr-population-covid-19-tracking")
    st.markdown("Published By: California Department of Corrections and Rehabilitation")
    st.markdown("Data First Published: September 09, 2020")

    st.subheader("Dataset Preview")
    st.write(f"Rows: {len(df):,} | Columns: {len(df.columns):,} | Institutions: {df['InstitutionName'].nunique():,}")
    st.table(df.head(10))

    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Filtered Data", csv, "filtered_covid19_data.csv", "text/csv")
