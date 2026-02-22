
import numpy as np
from sklearn.linear_model import LinearRegression

def forecast_demand(df, forecast_days=30):
    df = df.copy()
    df["day_index"] = np.arange(len(df))

    X = df[["day_index"]]
    y = df["total_sales"]

    model = LinearRegression()
    model.fit(X, y)

    future_index = np.arange(len(df), len(df) + forecast_days).reshape(-1, 1)
    forecast_values = model.predict(future_index)

    return forecast_values
