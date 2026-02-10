from typing import Callable, Any, List, Dict, Tuple
from bisect import bisect_right

class Simulation:
    def __init__(
        self, 
        distributions: Any = None, 
        handlers: Any = None, 
        simulation_length: int = 24
    ):
        # fixed values
        self.boundary_length = 20
        self.simulation_length = simulation_length

        # type things that can change to throw errors
        self.event_calendar: List[Dict[str, Any]] = []
        self.distributions: Dict[str, Callable[[Any], None]] = {}
        self.event_handlers: Dict[str, Callable[[Any], None]] = {}
        self.idle_taxis: List[Tuple] = {}
        self.current_time: int = 0

        if distributions:
            print('adding distributions')
            self.register_distribution("taxi-arrival", distributions.generate_taxi_arrival)
            self.register_distribution("taxi-location", distributions.generate_taxi_location)
            self.register_distribution("taxi-departure", distributions.generate_taxi_departure)

        if handlers:
            print('adding handlers')
            self.register_event_handler("taxi-arrival", handlers.handle_taxi_arrival)
            self.register_event_handler("termination", handlers.handle_termination)

        first_arrival = self.current_time + self.distributions["taxi-arrival"]()
        self.add_event(first_arrival, "taxi-arrival", None)
        self.add_event(self.simulation_length, "termination", None)


    def add_event(self, event_time:float, event_type: str, event_data: Any = None)->None:
        event = {'time': event_time, 'type': event_type, 'data': event_data}
        index = bisect_right([e['time'] for e in self.event_calendar], event_time)
        self.event_calendar.insert(index, event)

    def register_distribution(self, random_quantity: str, handler: Callable[[Any], None]):
        self.distributions[random_quantity] = handler

    def register_event_handler(self, event_type: str, handler: Callable[[Any], None]) -> None:
        # This function allows us to dynamically add event types to the list.
        self.event_handlers[event_type] = handler

    def run(self):
        print('TEST: printing starting event calendar')
        print(self.event_calendar)
