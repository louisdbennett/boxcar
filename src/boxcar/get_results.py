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

    profit_total = sum((t.money_made - t.distance_covered) for t in taxis)
    profit_avg = profit_total/sum(1 for t in taxis)

    served = sum(1 for r in riders if getattr(r, "at_destination", False))
    cancelled = sum(1 for r in riders if getattr(r, "cancelled", False))

    online_time = (rider.online_time for rider in sim.riders.values() if rider.pickup_time)
    pickup_time = (rider.pickup_time for rider in sim.riders.values() if rider.pickup_time)
    waiting_total = sum(pickup - online for online, pickup in zip(online_time, pickup_time))

    per_hour = []
    for t in taxis:
        hrs = t.time_offline - t.time_online
        if hrs is None or hrs <= 0:
            continue
        per_hour.append((t, t.money_made / hrs))


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