import numpy as np
import numpy.typing as npt
from scipy.spatial.distance import cdist
from typing import Iterable, Tuple

def get_locations(objs) -> npt.ArrayLike:
    """Return object locations as an array of (x, y, id)."""
    return np.array([
        (obj.location[0], obj.location[1], num)
        for num, obj in objs.items()
    ])

def get_assigned_passengers(objs) -> npt.ArrayLike:
    """Return current taxi-rider assignments as (taxi_id, passenger_id)."""
    return np.array([
        (num, obj.passenger_id)
        for num, obj in objs.items()
    ])

def get_moving_locations(taxis, current_time) -> npt.ArrayLike:
    """Return current taxi positions, interpolating if they are moving."""
    results = []
    print(f"taxis: {taxis}")
    for num, obj in taxis.items():
        # If taxi is not moving, use its current stored location
        if np.array_equal(obj.origin_loc, obj.destination_loc):
            results.append((obj.origin_loc[0], obj.origin_loc[1], num))
            continue
            
        # Total travel time for current segment
        time_total = obj.destination_time - obj.origin_time
        
        if time_total == 0:
            results.append((obj.destination_loc[0], obj.destination_loc[1], num))
            continue

        # Linear interpolation between origin and destination
        progress = (current_time - obj.origin_time) / time_total
        x = obj.origin_loc[0] + (obj.destination_loc[0] - obj.origin_loc[0]) * progress
        y = obj.origin_loc[1] + (obj.destination_loc[1] - obj.origin_loc[1]) * progress
        
        print(f"{round(current_time, 2)}: taxi {num} - time:{round(time_total,2)}, x:{round(x,1)}, y:{round(y,1)}")
        print(f"taxi {num} loc_origin: {obj.origin_loc}, loc_distination {obj.destination_loc}, start_time: {obj.origin_time}")

        results.append((x, y, num))
        
    return np.array(results)

def find_closest(
    location: Tuple, 
    comparison_locations: npt.ArrayLike
) -> (int, float):
    """Return the id and distance of the closest comparison point."""
    dist = cdist(np.array([location]), comparison_locations[:, :2], metric="euclidean")
    ind = np.argmin(dist)
    return comparison_locations[:, 2][ind], np.min(dist)

def find_shortest_trip(trips: Iterable[Tuple[int, float]]) -> Tuple[int, float]:
    """Return the rider with the shortest trip."""
    return min(trips, key=lambda x: x[1])

def find_longest_trip(trips: Iterable[Tuple[int, float]]) -> Tuple[int, float]:
    """Return the rider with the longest trip."""
    return max(trips, key=lambda x: x[1])

def get_trips(riders):
    """Return a list of (rider_id, trip_distance)."""
    return [
        (
            rid,
            np.linalg.norm(np.array(r.location) - np.array(r.destination))
        )
        for rid, r in riders.items()
    ]