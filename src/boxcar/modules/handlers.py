from boxcar.classes.rider import Rider
from boxcar.classes.simulation import Simulation
from boxcar.classes.taxi import Taxi
import boxcar.modules.utils as utils


def execute_taxi_arrival(sim: Simulation):
    # get the taxi id we'll use to track it through the system
    sim.number_total_taxis += 1

    # generate the starting location of the taxi and get its id
    location = sim.distributions["location"]()
    taxi_number = sim.number_total_taxis

    print(f"taxi {taxi_number} arrives")

    sim.taxis[taxi_number] = Taxi(taxi_number, location)

    # todo: add picking up closest idle passengers if any exist
    # if taxi picks up someone it doesn't go into idle_taxis

    departure_time = sim.current_time + sim.distributions["taxi-departure"]()
    # pass taxi number through to departure event so we can remove the correct taxi
    sim.add_event(
        departure_time, "taxi-departure", event_data={"taxi_number": taxi_number}
    )

    arrival_time = sim.current_time + sim.distributions["taxi-arrival"]()
    sim.add_event(arrival_time, "taxi-arrival")


def execute_taxi_departure(sim: Simulation, taxi_number):
    print(f"taxi {taxi_number} departs")
    taxi = sim.taxis.get(taxi_number)

    # if the taxi is currently idle then remove it
    # otherwise schedule if going offline, and then check this at the end of a drop off event
    if taxi.idle:
        sim.taxis.pop(taxi_number)
    else:
        taxi.go_offline()


def execute_rider_arrival(sim: Simulation):
    # get the rider id we'll use to track it through the system
    sim.number_riders += 1

    rider_number = sim.number_riders
    location = sim.distributions["location"]()

    # generate the destination of the ride
    destination = sim.distributions["location"]()

    print(f"rider {rider_number} arrives at {location}")

    sim.riders[rider_number] = Rider(rider_number, location, destination)

    cancellation_time = sim.current_time + sim.distributions["rider-cancellation"]()
    # pass rider number through to cancellation event
    sim.add_event(
        cancellation_time,
        "rider-cancellation",
        event_data={"rider_number": rider_number}
    )

    # schedule the next rider to arrives
    arrival_time = sim.current_time + sim.distributions["rider-arrival"]()
    sim.add_event(arrival_time, "rider-arrival")

    # check all online taxis and assign the closest
    taxis = sim.get_idle_taxis()
    if taxis:
        taxi_number, dist = utils.find_closest(location, utils.get_taxi_locations(taxis))
        print(f"taxi {taxi_number} is the closest ({dist} away) and is assigned the job")

        # update the rider to be in service so they don't go offline
        sim.riders[rider_number].update_service_status(service_status=True)

        # update the taxi to no longer be idle
        taxis[taxi_number].update_idle_status(idle_status=False)

        # schedule arrival of taxi to pick up passenger depending on the distance and add to EC
        journey_time = sim.current_time + sim.distributions["journey"](dist)
        sim.add_event(
            journey_time,
            "pickup",
            event_data={"rider_number": rider_number, "taxi_number": taxi_number}
        )


def execute_rider_cancellation(sim: Simulation, rider_number):
    rider = sim.riders.get(rider_number)

    # if the rider has already had a service completion or is currently in service then no need to do anything
    if not rider.at_destination and not rider.in_service:
        print(f"rider {rider_number} cancels and departs")
        rider.cancel_ride()

def execute_rider_pickup(sim: Simulation, rider_number, taxi_number):
    print(f"taxi {taxi_number} picking up rider {rider_number}")

def execute_termination(sim: Simulation):
    print("simulation terminates")
