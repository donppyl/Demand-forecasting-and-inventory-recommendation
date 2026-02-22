import sqlite3
import pandas as pd
import os
from sklearn.datasets import load_diabetes
import numpy as np
from line_simulator import simulate_line_data

DB_NAME = "operations.db"

def initialize_database():
    if not os.path.exists(DB_NAME):
        data = load_diabetes()
        df = pd.DataFrame(data=data.data, columns=data.feature_names)
        np.random.seed(42)
        df["total_sales"] = (df["bmi"] * 100 + np.random.normal(0, 10, len(df))).astype(int)
        df["day_num"] = range(1, len(df)+1)
        conn = sqlite3.connect(DB_NAME)
        df[["day_num", "total_sales"]].to_sql("sales_data", conn, if_exists="replace", index=False)
        conn.close()

def initialize_line_tables():
    conn = sqlite3.connect(DB_NAME)
    equipment_df, units_df = simulate_line_data(days=45)
    equipment_df.to_sql("equipment_events", conn, if_exists="replace", index=False)
    units_df.to_sql("production_units", conn, if_exists="replace", index=False)
    conn.close()

def get_daily_sales():
    initialize_database()
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT day_num, total_sales FROM sales_data ORDER BY day_num", conn)
    conn.close()
    return df

def get_oee_daily(line):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM equipment_events WHERE line = ?", conn, params=(line,))
    conn.close()
    return df

def get_units(line):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM production_units WHERE line = ?", conn, params=(line,))
    conn.close()
    return df
