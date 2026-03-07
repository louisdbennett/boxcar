from typing import Tuple, List, Dict, Any, Optional

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
        self.path: List[Dict[str, Any]] = []
        self._active_segment: Optional[Dict[str, Any]] = None
    def schedule_offline(self):
        self.going_offline = True

    def update_idle_status(self, idle_status=True):
        self.idle = idle_status

    def update_location(self, location):
        self.location = location

    def go_offline(self):
        self.online = False

    def start_segment(self, t_start: float, start: Tuple, end: Tuple, has_rider: bool):
        self._active_segment = {
            "has_rider": has_rider,
            "t_start": t_start,
            "t_end": None,
            "start": start,
            "end": end,
        }

    def end_segment(self, t_end: float):
        if self._active_segment is None:
            return
        self._active_segment["t_end"] = t_end
        self.path.append(self._active_segment)
        self._active_segment = None