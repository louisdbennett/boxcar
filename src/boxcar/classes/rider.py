from typing import Tuple

class Rider:
    """Track an individual rider and their service status."""

    def __init__(self, number: int, location: Tuple, destination: Tuple, time: float):
        """Initialise a rider with id, locations, spawn time."""
        self.number = number
        self.location = location
        self.destination = destination
        self.cancelled = False
        self.in_service = 'waiting'
        self.at_destination = False
        self.online_time = time
        self.pickup_time = False
        self.taxi_id = None

    def update_location(self, location):
        """Update the rider's current location."""
        self.location = location

    def cancel_ride(self):
        """Mark the rider as cancelled."""
        self.cancelled = True

    def update_service_status(self, service_status='waiting'):
        """Update the rider's current service state."""
        self.in_service = service_status
    
    def reach_destination(self):
        """Mark the rider as having completed the trip."""
        self.at_destination = True