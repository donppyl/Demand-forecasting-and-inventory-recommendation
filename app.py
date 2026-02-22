
import streamlit as st
import plotly.express as px
import pandas as pd

from database import get_daily_sales
from forecasting import forecast_demand
from inventory import calculate_inventory_metrics

st.set_page_config(page_title="Demand Forecasting & Inventory System")

st.title("Demand Forecasting & Inventory Recommendation System")

st.sidebar.header("System Parameters")
lead_time = st.sidebar.slider("Lead Time (days)", 1, 30, 7)
service_level = st.sidebar.slider("Service Level Z-Score", 1.0, 3.0, 1.65)

df = get_daily_sales()

st.subheader("Historical Demand")
fig = px.line(df, x="day_num", y="total_sales")
st.plotly_chart(fig)

st.subheader("Forecast (Next 30 Days)")
forecast_values = forecast_demand(df)

forecast_df = pd.DataFrame({
    "future_day": range(len(df), len(df) + 30),
    "forecast_sales": forecast_values
})

fig2 = px.line(forecast_df, x="future_day", y="forecast_sales")
st.plotly_chart(fig2)

st.subheader("Inventory Recommendations")

metrics = calculate_inventory_metrics(df, lead_time, service_level)

st.metric("Average Daily Demand", round(metrics["average_demand"], 2))
st.metric("Safety Stock", round(metrics["safety_stock"], 2))
st.metric("Reorder Point", round(metrics["reorder_point"], 2))
st.metric("EOQ (Recommended Order Qty)", round(metrics["eoq"], 2))

st.caption("Built by Don P | Industrial Engineer | Python + SQL + Forecasting")
