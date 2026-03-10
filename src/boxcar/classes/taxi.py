from typing import Tuple, List, Dict, Any, Optional

class Taxi:
    """Track an individual taxi and its state throughout the simulation."""

    # this class tracks taxis through the system so we can remove the correct taxis as they go offline
    def __init__(self, number:int, location:Tuple, time:float):
        """Initialise a taxi with its id, starting location, and online time."""
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
        
    def schedule_offline(self):
        """Mark the taxi to go offline after its current job."""
        self.going_offline = True

    def update_idle_status(self, idle_status=True):
        """Set whether the taxi is idle."""
        self.idle = idle_status

    def update_location(self, location):
        """Update the taxi's current location."""
        self.location = location

    def go_offline(self, time):
        """Take the taxi offline and record its offline time."""
        self.online = False
        self.time_offline = time

    def start_segment(self, t_start: float, start: Tuple, end: Tuple, has_rider: bool):
        """Start recording a new movement segment."""
        self._active_segment = {
            "has_rider": has_rider,
            "t_start": t_start,
            "t_end": None,
            "start": start,
            "end": end,
        }

    def end_segment(self, t_end: float):
        """Close the current movement segment and save it."""
        if self._active_segment is None:
            return
        self._active_segment["t_end"] = t_end
        self.path.append(self._active_segment)
        self._active_segment = None

    def start_en_route(self,TF):
        """Set whether the taxi is currently en route."""
        self.en_route = TF
    
    def set_new_start_and_end(self,current_time, dest_time, orig_loc, dest_loc,rider_no):
        """Update trip timing, locations, and assigned rider together."""
        self.origin_time = current_time
        self.destination_time = dest_time
        self.origin_loc = orig_loc
        self.destination_loc = dest_loc
        self.passenger_id = rider_no

    def remove_rider(self):
        """Clear the current rider assignment."""
        self.passenger_id = None

    def set_origin_time(self,org_time):
        """Set the start time of the current leg."""
        self.origin_time = org_time

    def set_destination_time(self,dest_time):
        """Set the end time of the current leg."""
        self.destination_time = dest_time

    def set_origin_location(self,org_loc):
        """Set the origin location of the current leg."""
        self.origin_loc = org_loc    

    def set_destination_location(self,des_loc):
        """Set the destination location of the current leg."""
        self.destination_loc = des_loc   

    def add_rider(self,rider_no):
        """Assign a rider to the taxi."""
        self.passenger_id = rider_no