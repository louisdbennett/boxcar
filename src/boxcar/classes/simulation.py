from typing import Callable, Any, List, Dict
from bisect import bisect_right
from boxcar.classes.taxi import Taxi

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
        # track the total number of taxis so they each get a unique id
        self.number_total_taxis: int = 0
        self.number_riders: int = 0
        self.taxis: Dict[int, Taxi] = {}
        self.current_time: float = 0

        if distributions:
            print('adding distributions')
            self.register_distribution("location", distributions.generate_location)
            self.register_distribution("taxi-arrival", distributions.generate_taxi_arrival)
            self.register_distribution("taxi-departure", distributions.generate_taxi_departure)

        if handlers:
            print('adding handlers')
            self.register_event_handler("taxi-arrival", handlers.handle_taxi_arrival)
            self.register_event_handler("taxi-departure", handlers.handle_taxi_departure)
            self.register_event_handler("termination", handlers.handle_termination)

        first_arrival = self.current_time + self.distributions["taxi-arrival"]()
        self.add_event(first_arrival, "taxi-arrival", None)
        self.add_event(self.simulation_length, "termination", None)

    def add_event(
        self, event_time: float, event_type: str, event_data: Any = None
    ) -> None:
        event = {'time': event_time, 'type': event_type, 'data': event_data}
        index = bisect_right([e['time'] for e in self.event_calendar], event_time)
        self.event_calendar.insert(index, event)

    def register_distribution(
        self, random_quantity: str, handler: Callable[[Any], None]
    ) -> None:
        self.distributions[random_quantity] = handler

    def register_event_handler(
        self, event_type: str, handler: Callable[[Any], None]
    ) -> None:
        # This function allows us to dynamically add event types to the list.
        self.event_handlers[event_type] = handler

    def progress_time(self) -> None:
        print("progressing time")
        if not self.event_calendar:
            print("No more events to process.")
            return

        next_event = self.event_calendar.pop(0)
        self.current_time = next_event['time']
        event_type = next_event['type']
        event_data = next_event['data']

        # perform any necessary tracking of variables here

        if event_type in self.event_handlers:
            self.event_handlers[event_type](event_data)
        else:
            raise Exception(f"No handler registered for event type: {event_type}")

    def run(self) -> None:
        terminate_simulation = 0

        while self.event_calendar:
            # check the next event to see if it is a termination
            next_event = self.event_calendar[0] 
            if next_event['type'] == "termination":
                terminate_simulation = 1
            self.progress_time()
            if terminate_simulation == 1:
                break

        if terminate_simulation == 0:
            raise Exception('No events left to process')

