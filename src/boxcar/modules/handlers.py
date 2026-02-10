from boxcar.classes.simulation import Simulation

def execute_taxi_arrival(sim:Simulation):
    # generate the location of the taxi and track it in idle_taxis
    location = sim.distributions["taxi-arrival"]()
    sim.idle_taxis.append(location)
    
    # todo: add picking up closest idle passengers if any exist
    # if taxi picks up someone it doesn't go into idle_taxis

    departure_time = sim.current_time + sim.distributions["taxi-departure"]()
    sim.add_event(departure_time, "taxi-departure")

    # todo: schedule the next taxi arrival

def execute_termination(sim:Simulation):
    print('terminating simulation')
