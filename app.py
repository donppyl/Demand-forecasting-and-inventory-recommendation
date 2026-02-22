import streamlit as st
import plotly.express as px
import pandas as pd

from database import (
    get_daily_sales,
    get_oee_daily,
    get_units,
    initialize_line_tables,
)
from forecasting import forecast_demand
from inventory import calculate_inventory_metrics
from oee import compute_oee

st.set_page_config(page_title="Digital Factory Dashboard")
st.title("Digital Factory Dashboard")
st.caption("Demand Forecasting + Inventory + OEE + Cycle Time Analytics")

initialize_line_tables()

tab1, tab2 = st.tabs(["Demand & Inventory", "Line Performance (OEE + CT)"])

with tab1:
    st.header("Demand & Inventory")
    lead_time = st.slider("Lead Time (days)", 1, 30, 7)
    service_level = st.slider("Service Level Z-Score", 1.0, 3.0, 1.65)
    df = get_daily_sales()

    fig = px.line(df, x="day_num", y="total_sales")
    st.plotly_chart(fig, use_container_width=True)

    forecast_values = forecast_demand(df)
    forecast_df = pd.DataFrame({
        "future_day": range(len(df), len(df) + 30),
        "forecast_sales": forecast_values
    })

    fig2 = px.line(forecast_df, x="future_day", y="forecast_sales")
    st.plotly_chart(fig2, use_container_width=True)

    metrics = calculate_inventory_metrics(df, lead_time, service_level)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg Daily Demand", round(metrics["average_demand"], 2))
    c2.metric("Safety Stock", round(metrics["safety_stock"], 2))
    c3.metric("Reorder Point", round(metrics["reorder_point"], 2))
    c4.metric("EOQ", round(metrics["eoq"], 2))

with tab2:
    st.header("EV Supercharger Line Performance")
    line_name = "EV Supercharger Final Assembly"
    oee_df = compute_oee(get_oee_daily(line_name))
    units_df = get_units(line_name)

    fig_oee = px.line(
        oee_df,
        x="date",
        y=["availability", "performance", "quality", "oee"],
        title="OEE Trend"
    )
    st.plotly_chart(fig_oee, use_container_width=True)

    latest = oee_df.iloc[-1]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Availability", f"{latest['availability']*100:.1f}%")
    c2.metric("Performance", f"{latest['performance']*100:.1f}%")
    c3.metric("Quality", f"{latest['quality']*100:.1f}%")
    c4.metric("OEE", f"{latest['oee']*100:.1f}%")

    st.subheader("Cycle Time Distribution")
    fig_ct = px.histogram(units_df, x="cycle_time_sec", nbins=40)
    st.plotly_chart(fig_ct, use_container_width=True)

    units_df["timestamp"] = pd.to_datetime(units_df["timestamp"])
    units_df = units_df.sort_values("timestamp")
    units_df["ct_roll"] = units_df["cycle_time_sec"].rolling(50).mean()

    fig_trend = px.line(units_df, x="timestamp", y=["cycle_time_sec", "ct_roll"])
    st.plotly_chart(fig_trend, use_container_width=True)
