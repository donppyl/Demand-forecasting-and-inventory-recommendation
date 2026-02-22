
import numpy as np

def calculate_inventory_metrics(df, lead_time=7, service_level_z=1.65):
    avg_demand = df["total_sales"].mean()
    demand_std = df["total_sales"].std()

    safety_stock = service_level_z * demand_std * np.sqrt(lead_time)
    reorder_point = (avg_demand * lead_time) + safety_stock

    annual_demand = avg_demand * 365
    order_cost = 50
    holding_cost = 2

    eoq = np.sqrt((2 * annual_demand * order_cost) / holding_cost)

    return {
        "average_demand": avg_demand,
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        "eoq": eoq
    }
