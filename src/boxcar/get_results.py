import csv
import os
from typing import Any, Dict
from boxcar.classes.simulation import Simulation

def save_results(
    sim: Simulation,
    cfg: Dict[str, Any],
    csv_path: str = "outputs/results.csv",
    run_name: str = None,
    rewrite: bool = True,
) -> None:
    taxis = list(sim.taxis.values())
    riders = list(sim.riders.values())

    total_money = sum(t.money_made for t in taxis)
    total_distance = sum(t.distance_covered for t in taxis)

    profit_total = sum((t.money_made - 0.2 * t.distance_covered) for t in taxis)
    profit_avg = profit_total / sum(1 for t in taxis)

    served = sum(1 for r in riders if getattr(r, "at_destination", False))
    cancelled = sum(1 for r in riders if getattr(r, "cancelled", False))

    online_time = (rider.online_time for rider in sim.riders.values() if rider.pickup_time)
    pickup_time = (rider.pickup_time for rider in sim.riders.values() if rider.pickup_time)
    waiting_total = sum(pickup - online for online, pickup in zip(online_time, pickup_time))

    per_hour = []
    for t in taxis:
        if t.time_offline == None:
            t_end = sim.simulation_length
            hrs = t_end - t.time_online
        elif t.time_offline: 
            hrs = t.time_offline - t.time_online
        per_hour.append((t, t.money_made / hrs))


    end_time = sim.simulation_length  # hours

    free_times = []
    for t in taxis:
        t_off = getattr(t, "time_offline")
        t_on = getattr(t, "time_online")

        shift_end = getattr(t, "time_offline")

        if t_off is not None and t_off > t_on:
            t_end = min(t_off, end_time)
        elif shift_end is not None and shift_end > t_on:
            t_end = min(shift_end, end_time)
        else:
            t_end = end_time

        online = t_end - t_on
        if online <= 0:
            continue

        busy = sum(
            (seg["t_end"] - seg["t_start"])
            for seg in getattr(t, "path", [])
            if seg.get("t_start") is not None and seg.get("t_end") is not None
        )

        free_times.append( online - busy)

    avg_free_time = sum(free_times) / len(free_times)

    high_taxi, high_rate = max(per_hour, key=lambda x: x[1])
    low_taxi, low_rate = min(per_hour, key=lambda x: x[1])
    highest_id, highest_norm = high_taxi.number, high_rate
    lowest_id, lowest_norm = low_taxi.number, low_rate

    row: Dict[str, Any] = {
        "run_name": run_name,
        "cfg": f"cr={cfg.get('rider_choice_rule')}, ms={cfg.get('matching_strategy')}, bl={cfg.get('batch_length', cfg.get('batch_length'))}",
        "Total money_made": total_money,
        "Total distance driven": total_distance,
        "Average profit": profit_avg,
        "Customers served": served,
        "Customers cancelled": cancelled,
        "Waiting time": waiting_total,
        'Average free time': avg_free_time,
        "Highest earning taxi id": highest_id,
        "Highest earning taxi per hour": highest_norm,
        "Lowest earning taxi id": lowest_id,
        "Lowest earning taxi per hour": lowest_norm,
    }

    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)

    mode = "w" if rewrite else "a"
    file_exists = os.path.exists(csv_path)

    with open(csv_path, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))

        if rewrite or not file_exists:
            writer.writeheader()

        writer.writerow(row)
    return row
    '''with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)'''