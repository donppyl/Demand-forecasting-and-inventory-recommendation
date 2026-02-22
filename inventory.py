import numpy as np

def calculate_inventory_metrics(df, lead_time=7, service_level_z=1.65):
    avg = df["total_sales"].mean()
    std = df["total_sales"].std()
    safety_stock = service_level_z * std * np.sqrt(lead_time)
    reorder_point = (avg * lead_time) + safety_stock
    annual = avg * 365
    eoq = np.sqrt((2 * annual * 50) / 2)
    return {
        "average_demand": avg,
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        "eoq": eoq
    }
