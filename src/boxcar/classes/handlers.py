from boxcar.classes.simulation import Simulation
import boxcar.modules.handlers as hf
from typing import Any

class Handlers:
    """Class that connects simulation events to handler functions."""

    def __init__(self, simulation: Simulation):
        """Store reference to the simulation so handlers can modify it."""
        self.simulation = simulation

    def handle_taxi_arrival(self, event_data: Any):
        """Handle a taxi arrival event."""
        hf.execute_taxi_arrival(self.simulation)

    def handle_taxi_departure(self, event_data: Any):
        """Handle a taxi departure event."""
        hf.execute_taxi_departure(self.simulation, event_data["taxi_number"])

    def handle_rider_arrival(self, event_data: Any):
        """Handle a rider arrival event."""
        hf.execute_rider_arrival(self.simulation)

    def handle_rider_cancellation(self, event_data: Any):
        """Handle a rider cancellation event."""
        hf.execute_rider_cancellation(self.simulation, event_data["rider_number"])

    def handle_rider_pickup(self, event_data: Any):
        """Handle a rider pickup event."""
        hf.execute_rider_pickup(self.simulation, event_data["rider_number"], event_data["taxi_number"])

    def handle_rider_dropoff(self, event_data: Any):
        """Handle a rider dropoff event."""
        hf.execute_rider_dropoff(self.simulation, event_data["rider_number"], event_data["taxi_number"])

    def handle_termination(self, event_data: Any):
        """Handle simulation termination."""
        hf.execute_termination(self.simulation)

    def handle_batch_end(self, event_data: Any):
        """Handle the end of a batching period."""
        hf.execute_batch_end(self.simulation)