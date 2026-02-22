import sqlite3
import pandas as pd
import os
import numpy as np
from sklearn.datasets import load_diabetes
from line_simulator import simulate_line_data

DB_PATH = os.path.join("/tmp", "operations.db")

def _connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def _table_exists(conn, table_name: str) -> bool:
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
    return conn.execute(query, (table_name,)).fetchone() is not None

def initialize_database():
    conn = _connect()
    try:
        if not _table_exists(conn, "sales_data"):
            data = load_diabetes()
            df = pd.DataFrame(data=data.data, columns=data.feature_names)
            np.random.seed(42)
            df["total_sales"] = (df["bmi"] * 100 + np.random.normal(0, 10, len(df))).astype(int)
            df["day_num"] = range(1, len(df) + 1)
            df[["day_num", "total_sales"]].to_sql("sales_data", conn, if_exists="replace", index=False)
    finally:
        conn.close()

def initialize_line_tables():
    initialize_database()
    conn = _connect()
    try:
        equipment_df, units_df = simulate_line_data(days=45)
        equipment_df.to_sql("equipment_events", conn, if_exists="replace", index=False)
        units_df.to_sql("production_units", conn, if_exists="replace", index=False)
    finally:
        conn.close()

def get_daily_sales():
    initialize_database()
    conn = _connect()
    try:
        return pd.read_sql("SELECT day_num, total_sales FROM sales_data ORDER BY day_num", conn)
    finally:
        conn.close()

def get_oee_daily(line: str):
    initialize_line_tables()
    conn = _connect()
    try:
        return pd.read_sql("SELECT * FROM equipment_events WHERE line = ? ORDER BY date", conn, params=(line,))
    finally:
        conn.close()

def get_units(line: str):
    initialize_line_tables()
    conn = _connect()
    try:
        return pd.read_sql("SELECT * FROM production_units WHERE line = ? ORDER BY timestamp", conn, params=(line,))
    finally:
        conn.close()
