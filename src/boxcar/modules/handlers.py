from boxcar.classes.rider import Rider
from boxcar.classes.simulation import Simulation
from boxcar.classes.taxi import Taxi
import boxcar.modules.utils as utils
import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment

def find_rider(sim: Simulation, taxi:Taxi):
    location = taxi.location
    taxi_number = taxi.number

    # picking up closest idle passengers if any exist
    riders = sim.get_waiting_riders()
    trips = utils.get_trips(riders)
    
    if riders:
        if sim.config["rider_choice_rule"] == "closest":
            rider_number, dist = utils.find_closest(location, utils.get_locations(riders))
            
        elif sim.config["rider_choice_rule"] == "shortest":
            rider_number, trip_dist = utils.find_shortest_trip(trips)

            # now assign the closest idle taxi to THAT rider
            chosen_loc = sim.riders[rider_number].location
            dist = np.linalg.norm(np.array(location) - np.array(chosen_loc))

        elif sim.config["rider_choice_rule"] == "longest":
            rider_number, trip_dist = utils.find_longest_trip(trips)

            # now assign the closest idle taxi to THAT rider
            chosen_loc = sim.riders[rider_number].location
            dist = np.linalg.norm(np.array(location) - np.array(chosen_loc))

        if sim.verbose:
            print(
                f"{round(sim.current_time, 2)} rider {rider_number} is chosen and taxi {taxi_number} assigned ({round(dist, 2)} away)"
            )
            
        # update the rider to be in service so they don't go offline
        rider = riders[rider_number]
        rider.update_service_status(service_status=True)

        # track the total distance the taxi has/will cover
        taxi.distance_covered += dist

        # update the taxi to not be in an idle state
        taxi.update_idle_status(False)

        # schedule arrival of taxi to pick up passenger depending on the distance and add to EC
        journey_time = sim.current_time + sim.distributions["journey"](dist)
        taxi.start_segment(
            t_start=sim.current_time,
            start=taxi.location,
            end=rider.location,
            has_rider=False
        )
        sim.add_event(
            journey_time,
            "pickup",
            event_data={"rider_number": rider_number, "taxi_number": taxi_number}
        )

        # also add the pickup time to the rider
        rider.pickup_time = journey_time

def find_taxi(sim: Simulation, rider:Rider):
    location = rider.location
    rider_number = rider.number

    # check all online taxis and assign the closest
    taxis = sim.get_idle_taxis()
    if taxis:
        # checking for configs
        taxi_number, dist = utils.find_closest(location, utils.get_locations(taxis))

        if sim.verbose:
            print(
                f"taxi {taxi_number} is the closest out of {len(taxis)} ({round(dist, 2)} away) and is assigned"
            )

        # update the rider to be in service so they don't go offline
        rider = sim.riders[rider_number]
        rider.update_service_status(service_status=True)

        # update the taxi to no longer be idle
        taxis[taxi_number].update_idle_status(idle_status=False)

        # schedule arrival of taxi to pick up passenger depending on the distance and add to EC
        journey_time = sim.current_time + sim.distributions["journey"](dist)
        sim.add_event(
            journey_time,
            "pickup",
            event_data={"rider_number": rider_number, "taxi_number": taxi_number},
        )

        # also add the pickup time to the rider
        rider.pickup_time = journey_time

def execute_taxi_arrival(sim: Simulation):
    # get the taxi id we'll use to track it through the system
    sim.number_taxis += 1
    # generate the starting location of the taxi and get its id
    location = sim.distributions["location"]()
    taxi_number = sim.number_taxis

    if sim.verbose:
        print(f"{round(sim.current_time, 2)}: taxi {taxi_number} arrives")

    # add the taxi to the simulation
    sim.taxis[taxi_number] = Taxi(taxi_number, location, sim.current_time)
    departure_time = sim.current_time + sim.distributions["taxi-departure"]()
    # pass taxi number through to departure event so we can remove the correct taxi
    sim.add_event(
        departure_time, "taxi-departure", event_data={"taxi_number": taxi_number}
    )

    arrival_time = sim.current_time + sim.distributions["taxi-arrival"]()
    sim.add_event(arrival_time, "taxi-arrival")

def execute_taxi_departure(sim: Simulation, taxi_number):
    if sim.verbose:
        print(f"{round(sim.current_time, 2)}: taxi {taxi_number} departs")
    
    taxi = sim.taxis.get(taxi_number)

    # if the taxi is currently idle then remove it
    # otherwise schedule if going offline, and then check this at the end of a drop off event
    if taxi.idle:
        taxi.go_offline(sim.current_time)
    else:
        taxi.schedule_offline()

def execute_rider_arrival(sim: Simulation):
    # get the rider id we'll use to track it through the system
    sim.number_riders += 1

    rider_number = sim.number_riders
    location = sim.distributions["location"]()

    # generate the destination of the ride
    destination = sim.distributions["location"]()

    if sim.verbose:
        print(
            f"{round(sim.current_time, 2)}: rider {rider_number} arrives at ({round(location[0], 1)}, {round(location[1], 1)})"
        )

    rider = Rider(rider_number, location, destination, sim.current_time)
    sim.riders[rider_number] = rider

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

    if sim.batch_length:
        if not sim.batching:
                sim.change_batching_status(True)
                sim.add_event(sim.current_time + sim.batch_length, 'batch-end')
    else:
        find_taxi(sim, rider)

def execute_rider_cancellation(sim: Simulation, rider_number):
    rider = sim.riders.get(rider_number)

    # if the rider has already had a service completion or is currently in service then no need to do anything
    if not rider.at_destination and not rider.in_service:
        if sim.verbose:
            print(f"{round(sim.current_time, 2)}: rider {rider_number} cancels and departs")
        rider.cancel_ride()

def execute_rider_pickup(sim: Simulation, rider_number, taxi_number):
    if sim.verbose:
        print(f"{round(sim.current_time, 2)}: taxi {taxi_number} picking up rider {rider_number}")

    rider = sim.riders.get(rider_number)
    taxi = sim.taxis.get(taxi_number)

    dist = ((rider.location[0] - rider.destination[0]) ** 2 + (rider.location[1] - rider.destination[1]) ** 2) ** (1/2)

    # could change these to being after the trip? 
    # was more convenient here because we have the distance
    # add the distance of the journey to the taxis total distance
    taxi.distance_covered += dist

    # add the price of the trip
    price = 3 + dist * 2
    taxi.money_made += price

    journey_time = sim.current_time + sim.distributions["journey"](dist)

    taxi.end_segment(t_end=sim.current_time)

    taxi.update_location(rider.location)

    taxi.start_segment(
        t_start=sim.current_time,
        start=rider.location,
        end=rider.destination,
        has_rider=True
    )

    sim.add_event(
        journey_time,
        "dropoff",
        event_data={"rider_number": rider_number, "taxi_number": taxi_number},
    )

def execute_rider_dropoff(sim: Simulation, rider_number, taxi_number):
    if sim.verbose:
        print(f"{round(sim.current_time, 2)}: taxi {taxi_number} dropping off rider {rider_number}")

    taxi = sim.taxis.get(taxi_number)

    # update the rider to be at their destination
    rider = sim.riders.get(rider_number)
    rider.reach_destination()
    # if a rider is staying online then get them to pick up the closest rider
    # otherwise get them to log off
    taxi.end_segment(t_end=sim.current_time)
    if taxi.going_offline:
        taxi.go_offline(sim.current_time)
    else:
        taxi.update_idle_status(idle_status=True)
        taxi.update_location(rider.destination)

        if sim.batch_length:
            if not sim.batching:
                sim.change_batching_status(True)
                sim.add_event(sim.current_time + sim.batch_length, 'batch-end')
        else:
            find_rider(sim, taxi)

def execute_batch_end(sim: Simulation):
    print("handling batch event!")
    ### finds available riders n drivers
    riders = sim.get_waiting_riders()
    drivers = sim.get_idle_taxis()
    
    # if one list is empty close batch
    if riders and drivers:      
    ## locates these riders n drivers 
        rider_locs = utils.get_locations(riders)
        driver_locs = utils.get_locations(drivers)
        dist = cdist(driver_locs[:, :2], rider_locs[:, :2], metric="euclidean")

        #print(f'Rider names {riders}')
        #print(f'Driver names {drivers}')
        #print(f'Rider locations {rider_locs[:, :2]}')
        #print(f'Driver locations {driver_locs[:, :2]}')
        #print(f'Distance matrix {dist}')        
        ### copy of dist mtx as it will be destroyed
        ### BEGIN HUNGARIAN ALGO
        cost = dist.copy()

        #print(f'Rider locations full data {rider_locs}')
        #print(f'Driver locations full data  {driver_locs}')

        #print(f'Riders in system {len(rider_locs)}')
        #print(f'Drivers in system {len(driver_locs)}')

        # combos of best row and col assignment
        row_ind, col_ind = linear_sum_assignment(cost)
        #print(f'row {row_ind} and column = {col_ind}')
        # driver, rider, distance
        assigned_pairs = [(driver_locs[r,2], rider_locs[c,2], dist[r,c]) for r,c in zip(row_ind,col_ind)]
        #print(f'Assignments: {assigned_pairs}')
        #print(f'Distances {dist}')
        #print(f'Assignments: {assigned_pairs}')
        ### END HUNGARIAN ALGO
        # # helper not needed?
        # assigned_drivers = {drivers[r] for r in row_ind}
        # assigned_riders = {riders[c] for c in col_ind}

        # unassigned_drivers = list(set(drivers) - assigned_drivers)
        # unassigned_riders = list(set(riders) - assigned_riders)

        # print("Assignments:", assigned_pairs)
        # print("Unassigned drivers:", unassigned_drivers)
        # print("Unassigned riders:", unassigned_riders)
        
        for pair in assigned_pairs:
            drivers.get(pair[0]).update_idle_status(False)
            riders.get(pair[1]).update_service_status(service_status=True)

            journey_time = sim.current_time + sim.distributions["journey"](pair[2])

            sim.add_event(
            journey_time,
            "pickup",
            event_data={"rider_number": pair[1], "taxi_number": pair[0]},
            )
    else:
        sim.change_batching_status(False)
        print("batch end - no action!")  

    sim.change_batching_status(False)
    print("batch end!")

def execute_termination(sim: Simulation):
    # distance = (taxi.distance_covered for taxi in sim.taxis.values())
    # money_made = (taxi.money_made for taxi in sim.taxis.values())
    #print('Profit:')
    #print(sum(taxi_metrics[0] - 0.2 * taxi_metrics[1] for taxi_metrics in zip(money_made, distance)))

    # online_time = (rider.online_time for rider in sim.riders.values() if rider.pickup_time)
    # pickup_time = (rider.pickup_time for rider in sim.riders.values() if rider.pickup_time)

    # #print('Rider Metrics:')
    # #print(len(list(online_time)))
    # #print(len(list(pickup_time)))
    # #print(sim.number_riders)

    # for online, pickup in zip(online_time, pickup_time):
    #     print((pickup - online) * 60)
    if sim.verbose:
        print(f'{round(sim.current_time, 2)}: terminating simulation')
