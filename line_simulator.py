import numpy as np
import pandas as pd

def simulate_line_data(days=30, line_name="EV Supercharger Final Assembly", seed=42):
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days, freq="D")

    equipment_rows = []
    unit_rows = []
    unit_id = 1

    for d in dates:
        planned_minutes = 960
        planned_downtime = 60
        unplanned = max(0, rng.normal(55, 20))
        micro = max(0, rng.normal(25, 10))
        run_minutes = planned_minutes - planned_downtime - unplanned - micro
        run_minutes = max(60, run_minutes)

        ideal_cycle = 210
        actual_cycle = max(160, rng.normal(245, 25))
        total_units = int((run_minutes * 60) / actual_cycle)
        scrap_rate = min(0.08, max(0.01, rng.normal(0.03, 0.01)))
        good_units = int(total_units * (1 - scrap_rate))

        equipment_rows.append({
            "date": d.date().isoformat(),
            "line": line_name,
            "planned_minutes": planned_minutes,
            "planned_downtime_minutes": planned_downtime,
            "unplanned_downtime_minutes": unplanned,
            "microstop_minutes": micro,
            "run_minutes": run_minutes,
            "ideal_cycle_sec": ideal_cycle,
            "total_units": total_units,
            "good_units": good_units,
            "reject_units": total_units - good_units
        })

        base_ts = pd.Timestamp(d) + pd.Timedelta(hours=6)

        for i in range(total_units):
            ts = base_ts + pd.Timedelta(seconds=i * actual_cycle)
            line_ct = max(150, rng.normal(230, 30))
            unit_rows.append({
                "unit_id": unit_id,
                "timestamp": ts.isoformat(),
                "line": line_name,
                "cycle_time_sec": line_ct,
                "passed": 1 if i < good_units else 0
            })
            unit_id += 1

    return pd.DataFrame(equipment_rows), pd.DataFrame(unit_rows)
