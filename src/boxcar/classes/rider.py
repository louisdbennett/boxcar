from typing import Tuple

class Rider:
    def __init__(self, number: int, location: Tuple, destination: Tuple, time: float):
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
        self.location = location

    def cancel_ride(self):
        self.cancelled = True

    def update_service_status(self, service_status='waiting'):
        self.in_service = service_status
    
    def reach_destination(self):
        self.at_destination = True
