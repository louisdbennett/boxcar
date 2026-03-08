from typing import Tuple, List, Dict, Any, Optional

class Taxi:
    # this class tracks taxis through the system so we can remove the correct taxis as they go offline
    def __init__(self, number:int, location:Tuple, time:float):
        self.number = number
        self.location = location
        self.idle = True
        self.online = True
        self.going_offline = False
        self.distance_covered = 0
        self.money_made = 0
        self.origin_time = 0
        self.destination_time = 0
        self.origin_loc = location
        self.destination_loc = location
        self.en_route = False
        self.passenger_id = None
        self.path: List[Dict[str, Any]] = []
        self._active_segment: Optional[Dict[str, Any]] = None
        self.distance_covered_reassign = 0
        
        self.time_online = time
        self.time_offline = None
        self.path: List[Dict[str, Any]] = []
        self._active_segment: Optional[Dict[str, Any]] = None
    
        self.distance_covered_reassign = 0
        
    def schedule_offline(self):
        self.going_offline = True

    def update_idle_status(self, idle_status=True):
        self.idle = idle_status

    def update_location(self, location):
        self.location = location

    def go_offline(self, time):
        self.online = False
        self.time_offline = time

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

    def start_en_route(self,TF):
        self.en_route = TF
    
    def set_new_start_and_end(self,current_time, dest_time, orig_loc, dest_loc,rider_no):
        self.origin_time = current_time
        self.destination_time = dest_time
        self.origin_loc = orig_loc
        self.destination_loc = dest_loc
        self.passenger_id = rider_no

    def remove_rider(self):
        self.passenger_id = None

    def set_origin_time(self,org_time):
        self.origin_time = org_time

    def set_destination_time(self,dest_time):
        self.destination_time = dest_time

    def set_origin_location(self,org_loc):
        self.origin_loc = org_loc    

    def set_destination_location(self,des_loc):
        self.destination_loc = des_loc   

    def add_rider(self,rider_no):
        self.passenger_id = rider_no


