from typing import Tuple

class Taxi:
    # this class tracks taxis through the system so we can remove the correct taxis as they go offline
    def __init__(self, number:int, location:Tuple):
        self.number = number
        self.location = location
        self.idle = True
        self.online = True
        self.going_offline = False
        self.distance_covered = 0
        self.money_made = 0
        self.time_online = 0
        self.time_offline = 0
    def schedule_offline(self):
        self.going_offline = True

    def update_idle_status(self, idle_status=True):
        self.idle = idle_status

    def update_location(self, location):
        self.location = location

    def go_offline(self):
        self.online = False
