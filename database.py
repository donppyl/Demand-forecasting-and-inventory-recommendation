
import sqlite3
import pandas as pd
import os
from sklearn.datasets import load_diabetes
import numpy as np

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

def get_daily_sales():
    initialize_database()
    conn = sqlite3.connect(DB_NAME)

    query = """
    SELECT day_num, total_sales
    FROM sales_data
    ORDER BY day_num
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df
