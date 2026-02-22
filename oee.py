import numpy as np

def compute_oee(df):
    planned_prod = df["planned_minutes"] - df["planned_downtime_minutes"]
    availability = df["run_minutes"] / planned_prod.clip(lower=1)
    performance = (df["ideal_cycle_sec"] * df["total_units"]) / (df["run_minutes"] * 60).replace(0, np.nan)
    quality = df["good_units"] / df["total_units"].replace(0, np.nan)
    df["availability"] = availability.clip(0,1)
    df["performance"] = performance.clip(0,1.5)
    df["quality"] = quality.clip(0,1)
    df["oee"] = (df["availability"] * df["performance"] * df["quality"]).clip(0,1)
    return df
