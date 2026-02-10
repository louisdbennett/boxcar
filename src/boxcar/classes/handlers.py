import boxcar.modules.handlers as hf
from typing import Any

class Handlers:
    def __init__(self, simulation):
        self.simulation = simulation

    def handle_taxi_arrival(self, event_data: Any):
        hf.execute_taxi_arrival(self.simulation)

    def handle_termination(self, event_data: Any):
        hf.execute_termination(self.simulation)


