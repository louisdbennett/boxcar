from typing import Tuple
import random

class Distributions:
    def __init__(self, simulation):
        self.simulation = simulation

    def generate_taxi_arrival(self, rate=3) -> float:
        arrival_time = random.expovariate(rate)  
        return arrival_time

    def generate_taxi_departure(self, lower=5, upper=8) -> float:
        departure_time = random.uniform(lower, upper)
        return departure_time

    def generate_location(self) -> Tuple[float, float]:
        x = random.uniform(0, self.simulation.boundary_length)
        y = random.uniform(0, self.simulation.boundary_length)
        return (x, y)

    # possibly a way to combine generate_taxi_arrival and generate_rider_arrival
    def generate_rider_arrival(self, rate=30) -> float:
        arrival_time = random.expovariate(rate)  
        return arrival_time

    def generate_rider_cancelling(self, rate=5) -> float:
        cancellation_time = random.expovariate(rate)
        return cancellation_time

    def generate_journey(self, dist) -> float:
        trip_time = dist / 20
        journey_length = random.uniform(0.8 * trip_time, 1.2 * trip_time)
        return journey_length
