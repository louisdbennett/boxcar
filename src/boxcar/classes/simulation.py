from typing import Callable, Any, List, Dict
from bisect import bisect_right
from boxcar.classes.taxi import Taxi
from boxcar.classes.rider import Rider


class Simulation:
    def __init__(
        self, 
        config: Dict[str, Any] = {"rider_choice_rule": "closest"},
        distributions: Any = None, 
        handlers: Any = None, 
        simulation_length: int = 24,
        verbose: bool= True
    ):
        # fixed values
        self.boundary_length = 20
        self.simulation_length = simulation_length
        self.verbose = verbose
        self.config = config

        # type things that can change to throw errors
        self.event_calendar: List[Dict[str, Any]] = []
        self.distributions: Dict[str, Callable[[Any], None]] = {}
        self.event_handlers: Dict[str, Callable[[Any], None]] = {}
        self.batching = False

        # track the total number of taxis so they each get a unique id
        self.number_taxis: int = 0
        self.number_riders: int = 0
        self.taxis: Dict[int, Taxi] = {}
        self.riders: Dict[int, Rider] = {}
        self.current_time: float = 0

        if distributions:
            self.register_distribution("taxi-location", distributions.generate_taxi_location)
            self.register_distribution("taxi-arrival", distributions.generate_taxi_arrival)
            self.register_distribution("taxi-departure", distributions.generate_taxi_departure)
            self.register_distribution("rider-location", distributions.generate_rider_location)
            self.register_distribution("rider-arrival", distributions.generate_rider_arrival)
            self.register_distribution("rider-cancellation", distributions.generate_rider_cancelling)
            self.register_distribution("journey", distributions.generate_journey)

        if handlers:
            self.register_event_handler("taxi-arrival", handlers.handle_taxi_arrival)
            self.register_event_handler("taxi-departure", handlers.handle_taxi_departure)
            self.register_event_handler("termination", handlers.handle_termination)
            self.register_event_handler("rider-arrival", handlers.handle_rider_arrival)
            self.register_event_handler("rider-cancellation", handlers.handle_rider_cancellation)
            self.register_event_handler("pickup", handlers.handle_rider_pickup)
            self.register_event_handler("dropoff", handlers.handle_rider_dropoff)
            self.register_event_handler("batch-end", handlers.handle_batch_end)

        first_taxi_arrival = self.current_time + self.distributions["taxi-arrival"]()
        first_rider_arrival = self.current_time + self.distributions["rider-arrival"]()

        self.add_event(first_taxi_arrival, "taxi-arrival", None)
        self.add_event(first_rider_arrival, "rider-arrival", None)
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
        if not self.event_calendar:
            print("No more events to process.")
            return

        next_event = self.event_calendar.pop(0)
        self.current_time = next_event["time"]
        event_type = next_event["type"]
        event_data = next_event["data"]

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

    # some helper functions
    def get_idle_taxis(self) -> Dict[int, Taxi]:
        return {num: taxi for num, taxi in self.taxis.items() if taxi.idle and taxi.online}

    def get_waiting_riders(self) -> Dict[int, Rider]:
        return {num: rider for num, rider in self.riders.items() if (not rider.in_service and not rider.cancelled and not rider.at_destination)}

    def change_batching_status(self, status:bool) -> None:
        self.batching = status