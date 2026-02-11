from boxcar.classes.Simulation import Simulation
import boxcar.modules.handlers as hf
from typing import Any

class Handlers:
    def __init__(self, simulation: Simulation):
        self.simulation = simulation

    def handle_taxi_arrival(self, event_data: Any):
        hf.execute_taxi_arrival(self.simulation)

    def handle_taxi_departure(self, event_data: Any):
        hf.execute_taxi_departure(self.simulation, event_data["taxi_number"])

    def handle_termination(self, event_data: Any):
        hf.execute_termination(self.simulation)
