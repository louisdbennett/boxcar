from boxcar.classes.simulation import Simulation
from boxcar.classes.taxi import Taxi

def execute_taxi_arrival(sim:Simulation):
    # get the taxi id we'll use to track it through the system
    sim.number_total_taxis += 1

    # generate the starting location of the taxi and get its id
    location = sim.distributions["location"]()
    taxi_number = sim.number_total_taxis

    print(f'taxi {taxi_number} arrives at {location}')

    sim.taxis[taxi_number] = Taxi(taxi_number, location)

    # todo: add picking up closest idle passengers if any exist
    # if taxi picks up someone it doesn't go into idle_taxis

    departure_time = sim.current_time + sim.distributions["taxi-departure"]()
    # pass taxi number through to departure event so we can remove the correct taxi
    sim.add_event(
        departure_time, 
        "taxi-departure", 
        event_data = {"taxi_number": taxi_number}
    )

    arrival_time = sim.current_time + sim.distributions["taxi-arrival"]()
    sim.add_event(arrival_time, "taxi-arrival")

def execute_taxi_departure(sim:Simulation, taxi_number):
    print(f'taxi {taxi_number} departs')
    taxi = sim.taxis.get(taxi_number)

    # if the taxi is currently idle then remove it
    # otherwise schedule if going offline, and then check this at the end of a drop off event
    if taxi.idle:
        sim.taxis.pop(taxi_number)
    else:
        taxi.go_offline()

def execute_termination(sim:Simulation):
    print('simulation terminates')
