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

st.set_page_config(page_title="Digital Factory Dashboard", layout="wide")

st.title("Digital Factory Dashboard")
st.caption("Demand Forecasting + Inventory + OEE + Cycle Time Analytics")

@st.cache_resource
def _init_db():
    initialize_line_tables()

_init_db()

tab1, tab2 = st.tabs(["Demand & Inventory", "Line Performance (OEE + CT)"])

with tab1:
    lead_time = st.slider("Lead Time (days)", 1, 30, 7)
    service_level = st.slider("Service Level (Z-Score)", 1.0, 3.0, 1.65)
    forecast_days = st.slider("Forecast Horizon (days)", 7, 90, 30)

    df = get_daily_sales()

    fig_hist = px.line(df, x="day_num", y="total_sales")
    st.plotly_chart(fig_hist, use_container_width=True)

    forecast_values = forecast_demand(df, forecast_days=forecast_days)
    forecast_df = pd.DataFrame({
        "future_day": range(len(df), len(df) + forecast_days),
        "forecast_sales": forecast_values
    })

    fig_forecast = px.line(forecast_df, x="future_day", y="forecast_sales")
    st.plotly_chart(fig_forecast, use_container_width=True)

    metrics = calculate_inventory_metrics(df, lead_time=lead_time, service_level_z=service_level)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Average Daily Demand", f"{metrics['average_demand']:.2f}")
    c2.metric("Safety Stock", f"{metrics['safety_stock']:.2f}")
    c3.metric("Reorder Point", f"{metrics['reorder_point']:.2f}")
    c4.metric("EOQ", f"{metrics['eoq']:.2f}")

with tab2:
    line_name = "EV Supercharger Final Assembly"

    oee_raw = get_oee_daily(line_name)
    oee_df = compute_oee(oee_raw)

    units_df = get_units(line_name)
    units_df["timestamp"] = pd.to_datetime(units_df["timestamp"])
    units_df = units_df.sort_values("timestamp")

    latest = oee_df.iloc[-1]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Availability", f"{latest['availability']*100:.1f}%")
    c2.metric("Performance", f"{latest['performance']*100:.1f}%")
    c3.metric("Quality", f"{latest['quality']*100:.1f}%")
    c4.metric("OEE", f"{latest['oee']*100:.1f}%")

    fig_oee = px.line(oee_df, x="date", y=["availability", "performance", "quality", "oee"])
    st.plotly_chart(fig_oee, use_container_width=True)

    fig_ct = px.histogram(units_df, x="cycle_time_sec", nbins=40)
    st.plotly_chart(fig_ct, use_container_width=True)

    roll_window = st.slider("Rolling Window (units)", 10, 300, 50)
    units_df["ct_roll"] = units_df["cycle_time_sec"].rolling(roll_window).mean()

    fig_trend = px.line(units_df, x="timestamp", y=["cycle_time_sec", "ct_roll"])
    st.plotly_chart(fig_trend, use_container_width=True)

    pass_rate = units_df["passed"].mean() if "passed" in units_df.columns else None
    if pass_rate is not None:
        st.metric("First Pass Yield (simulated)", f"{pass_rate*100:.1f}%")
