from typing import Tuple
import random
from numpy.random import multivariate_normal
from numpy import all

class Distributions:
    def __init__(self, simulation):
        self.simulation = simulation

    def generate_taxi_arrival(self, alpha=7718, beta=1/1994.886) -> float:
        rate = random.gammavariate(alpha, beta)
        arrival_time = random.expovariate(rate)  
        return arrival_time

    def generate_taxi_departure(self, lower=5, upper=8) -> float:
        departure_time = random.uniform(lower, upper)
        return departure_time

    def generate_location(self) -> Tuple[float, float]:
        x = random.uniform(0, self.simulation.boundary_length)
        y = random.uniform(0, self.simulation.boundary_length)
        return (x, y)

    def generate_taxi_location(
        self,
        mu=[9.973919, 11.513314],
        Sigma=[[20.372409, -1.315436], [-1.315436, 20.123543]],
    ) -> Tuple[float, float]:
        # have to do rejection sampling to make sure people are coming online within the city
        while True:
            samp = multivariate_normal(mu, Sigma, 1)[0]
            if all((samp >= 0) & (samp <= self.simulation.boundary_length)):
                return (samp[0],samp[1])

    def generate_rider_location(
        self,
        mu=[8.359686, 12.317549, 11.229662, 13.262570],
        Sigma=[
            [30.109842, -2.751673, 1.3039711, -7.9774297],
            [-2.751673, 21.794289, -2.2380619, 3.0090637],
            [1.3039711, -2.2380619, 23.9679586, -0.2035568],
            [-7.9774297, 3.0090637, -0.2035568, 24.7523207],
        ],
    ) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        while True:
            samp = multivariate_normal(mu, Sigma, 1)[0]
            if all((samp >= 0) & (samp <= self.simulation.boundary_length)):
                return (samp[0], samp[1]), (samp[2], samp[3])

    # possibly a way to combine generate_taxi_arrival and generate_rider_arrival
    def generate_rider_arrival(self, alpha=64420, beta=1/1994.91) -> float:
        rate = random.gammavariate(alpha, beta)
        arrival_time = random.expovariate(rate)  
        return arrival_time

    def generate_rider_cancelling(self, rate=0.03480842) -> float:
        cancellation_time = random.expovariate(rate)
        return cancellation_time

    def generate_journey(self, dist) -> float:
        trip_time = dist / 20
        journey_length = random.uniform(0.8 * trip_time, 1.2 * trip_time)
        return journey_length
