from typing import Tuple

class Taxi:
    # this class tracks taxis through the system so we can remove the correct taxis as they go offline
    def __init__(self, number:int, location:Tuple):
        self.number = number
        self.location = location
        self.idle = True
        self.going_offline = False

    def go_offline(self):
        self.going_offline = True

    def update_idle_status(self, idle_status=True):
        self.idle = idle_status

    def update_location(self, location):
        self.location = location
