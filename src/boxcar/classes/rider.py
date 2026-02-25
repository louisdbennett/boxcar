from typing import Tuple

class Rider:
    def __init__(self, number: int, location: Tuple, destination: Tuple):
        self.number = number
        self.location = location
        self.destination = destination
        self.cancelled = False
        self.in_service = False
        self.at_destination = False

    def update_location(self, location):
        self.location = location

    def cancel_ride(self):
        self.cancelled = True

    def update_service_status(self, service_status=True):
        self.in_service = service_status
    
    def reach_destination(self):
        self.at_destination = True
