import numpy as np
import numpy.typing as npt
from scipy.spatial.distance import cdist
from typing import Tuple

def get_taxi_locations(taxis) -> npt.ArrayLike:
    return np.array([
        (taxi.location[0], taxi.location[1], num)
        for num, taxi in taxis.items()
    ])

def find_closest(
    location: Tuple, 
    comparison_locations: npt.ArrayLike
) -> (int, float):
    dist = cdist(np.array([location]), comparison_locations[:, :2], metric="euclidean")
    ind = np.argmin(dist)
    return comparison_locations[:, 2][ind], np.min(dist)