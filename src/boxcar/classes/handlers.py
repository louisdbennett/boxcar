from boxcar.classes.simulation import Simulation
import boxcar.modules.handlers as hf
from typing import Any

class Handlers:
    def __init__(self, simulation: Simulation):
        self.simulation = simulation

    def handle_taxi_arrival(self, event_data: Any):
        hf.execute_taxi_arrival(self.simulation)

    def handle_taxi_departure(self, event_data: Any):
        hf.execute_taxi_departure(self.simulation, event_data["taxi_number"])

    def handle_rider_arrival(self, event_data: Any):
        hf.execute_rider_arrival(self.simulation)

    def handle_rider_cancellation(self, event_data: Any):
        hf.execute_rider_cancellation(self.simulation, event_data["rider_number"])

    def handle_rider_pickup(self, event_data: Any):
        hf.execute_rider_pickup(self.simulation, event_data["rider_number"], event_data["taxi_number"])

    def handle_termination(self, event_data: Any):
        hf.execute_termination(self.simulation)
