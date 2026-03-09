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
        rider.update_service_status(service_status='assigned')
        

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
        taxi = taxis[taxi_number]
        if sim.verbose:
            print(
                f"taxi {taxi_number} is the closest out of {len(taxis)} ({round(dist, 2)} away) and is assigned"
            )

        # update the rider to be in service so they don't go offline
        rider = sim.riders[rider_number]
        rider.update_service_status(service_status='assigned')

        # update the taxi to no longer be idle
        taxi.update_idle_status(idle_status=False)

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
            event_data={"rider_number": rider_number, "taxi_number": taxi_number},
        )

        # also add the pickup time to the rider
        rider.pickup_time = journey_time

def execute_taxi_arrival(sim: Simulation):
    # get the taxi id we'll use to track it through the system
    sim.number_taxis += 1
    # generate the starting location of the taxi and get its id
    location = sim.distributions["taxi-location"]()

    taxi_number = sim.number_taxis
    if sim.verbose:
        print(f"{round(sim.current_time, 2)}: taxi {taxi_number} arrives at ({round(location[0], 1)},{round(location[1], 1)})")

    # add the taxi to the simulation
    sim.taxis[taxi_number] = Taxi(taxi_number, location, sim.current_time)
    departure_time = sim.current_time + sim.distributions["taxi-departure"]()
    # pass taxi number through to departure event so we can remove the correct taxi
    sim.add_event(
        departure_time, "taxi-departure", event_data={"taxi_number": taxi_number}
    )

    arrival_time = sim.current_time + sim.distributions["taxi-arrival"]()
    sim.add_event(arrival_time, "taxi-arrival")
    taxi = sim.taxis[taxi_number]

    if "batch_length" in sim.config:
        # batching can wait for batch-end
        pass
    else:
        if sim.config["rider_choice_rule"] == "closest" and sim.config.get("matching_strategy") == "allow_rellocation":
            reallocate(sim)
        else:
            find_rider(sim, taxi)

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

    # generate the starting point and destination of the ride
    rider_number = sim.number_riders
    location, destination = sim.distributions["rider-location"]()

    if sim.verbose:
        print(
            f"{round(sim.current_time, 2)}: rider {rider_number} arrives at ({round(location[0], 1)}, {round(location[1], 1)}) wanting to go to ({round(destination[0], 1)}, {round(destination[1], 1)})"
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

    if "batch_length" in sim.config:
        if not sim.batching:
                sim.change_batching_status(True)
                sim.add_event(sim.current_time + sim.config["batch_length"], 'batch-end')
    else:
        if sim.config["rider_choice_rule"] == 'closest' and sim.config["matching_strategy"]=='allow_rellocation':
            reallocate(sim)
        else:
            find_taxi(sim, rider)

def execute_rider_cancellation(sim: Simulation, rider_number):
    rider = sim.riders.get(rider_number)

    # if the rider has already had a service completion or is currently in service then no need to do anything
    if (not rider.at_destination) and (rider.in_service == "waiting"):
        if sim.verbose:
            print(f"{round(sim.current_time, 2)}: rider {rider_number} cancels and departs")
        rider.cancel_ride()

def execute_rider_pickup(sim: Simulation, rider_number, taxi_number):
    if sim.verbose:
        print(f"{round(sim.current_time, 2)}: taxi {taxi_number} picking up rider {rider_number}")

    rider = sim.riders.get(rider_number)
    taxi = sim.taxis.get(taxi_number)

    if rider_number == sim.taxis.get(taxi_number).passenger_id or sim.taxis.get(taxi_number).passenger_id == None:
        # pickup the rider
        rider.update_service_status('in_taxi')

        dist = ((rider.location[0] - rider.destination[0]) ** 2 + (rider.location[1] - rider.destination[1]) ** 2) ** (1/2)
        
        taxi.start_en_route(False)
        # could change these to being after the trip? 
        # was more convenient here because we have the distance
        # add the distance of the journey to the taxis total distance
        dist_taxi_to_rider = ((rider.location[0] - taxi.origin_loc[0]) ** 2 + (rider.location[1] - taxi.origin_loc[1]) ** 2) ** (1/2)
        
        taxi.distance_covered += dist
        # separate metric for rerouting distance

        if sim.config["rider_choice_rule"] == 'closest' and sim.config["matching_strategy"]=='allow_rellocation': 
            taxi.distance_covered += dist_taxi_to_rider

        # ignore below two
        taxi.distance_covered_reassign += dist
        taxi.distance_covered_reassign += dist_taxi_to_rider

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
    
    # remove the rider
    taxi.remove_rider()
    taxi.start_en_route(False)
    taxi.set_origin_location(rider.destination)
    taxi.set_destination_location(rider.destination)
    taxi.set_origin_time(sim.current_time)
    taxi.set_destination_time(sim.current_time)


    taxi.end_segment(t_end=sim.current_time)

    # if a rider is staying online then get them to pick up the closest rider
    # otherwise get them to log off
    if taxi.going_offline:
        taxi.go_offline(sim.current_time)
    else:
        taxi.update_idle_status(idle_status=True)
        taxi.update_location(rider.destination)

        if "batch_length" in sim.config:
            if not sim.batching:
                sim.change_batching_status(True)
                sim.add_event(sim.current_time + sim.config["batch_length"], 'batch-end')
        else:

            if sim.config["rider_choice_rule"] == 'closest' and sim.config["matching_strategy"]=='allow_rellocation':
                reallocate(sim)
            else:
                find_rider(sim, taxi)

def execute_batch_end(sim: Simulation):
    ### finds available riders n drivers
    riders = sim.get_waiting_riders()
    taxis = sim.get_idle_taxis()
    
    # if one list is empty close batch
    if riders and taxis:      
        ## locates these riders n drivers 
        rider_locs = utils.get_locations(riders)
        taxi_locs = utils.get_locations(taxis)
        dist = cdist(taxi_locs[:, :2], rider_locs[:, :2], metric="euclidean")

        ### copy of dist mtx as it will be destroyed
        ### BEGIN HUNGARIAN ALGO
        cost = dist.copy()

        # combos of best row and col assignment
        row_ind, col_ind = linear_sum_assignment(cost)
        # driver, rider, distance
        assigned_pairs = [(taxi_locs[r,2], rider_locs[c,2], dist[r,c]) for r,c in zip(row_ind,col_ind)]
        
        ### END HUNGARIAN ALGO

        for pair in assigned_pairs:
            taxi = taxis.get(pair[0])
            rider = riders.get(pair[1])
            
            taxi.update_idle_status(False)
            rider.update_service_status(service_status='assigned')

            if sim.verbose:
                print(
                    f"taxi {pair[0]} and rider {pair[1]} are paired ({round(pair[2], 2)} away)"
                )

            journey_time = sim.current_time + sim.distributions["journey"](pair[2])

            sim.add_event(
                journey_time,
                "pickup",
                event_data={"rider_number": pair[1], "taxi_number": pair[0]},
            )

            # also add the pickup time to the rider
            rider.pickup_time = journey_time

    sim.change_batching_status(False)
    print("batch end!")

def reallocate(sim: Simulation):
    All_riders = sim.get_waiting_riders(['waiting', 'assigned'])
    All_drivers = sim.get_enroute_or_idle_taxis()

    if All_riders and All_drivers:
        print('begin reallocate!!')

        Assig_drivers = sim.get_enroute_taxis()
        Existing_pairs = utils.get_assigned_passengers(Assig_drivers)
               
        # print(f'rider locs = {rider_locs}')
        driver_locs = utils.get_moving_locations(All_drivers, sim.current_time)
        
        # print(f'driver locs = {driver_locs}')
        # establish distance matrix 
        # print(f'the distance is {dist}')
        dist = cdist(driver_locs[:, :2], rider_locs[:, :2], metric="euclidean")
        ##
        cost = dist.copy()

        # convert existing assignments to indices
        #x, y = driver_locs[driver_locs[:, 2] == target_num][0, :2]

        if len(Existing_pairs) != 0:
            # print(f'Existing pairings = {Existing_pairs}') 

            d_arr = np.array(driver_locs)
            r_arr = np.array(rider_locs)
            
            pair_ids = {p[0] for p in Existing_pairs}
            paired_driver_idx = [i for i, (_, _, id_) in enumerate(driver_locs) if id_ in pair_ids]

            pair_ids = {p[1] for p in Existing_pairs}
            paired_rider_idx = [i for i, (_, _, id_) in enumerate(rider_locs) if id_ in pair_ids]

            existing_idx = list(zip(paired_driver_idx, paired_rider_idx))
            # print(f'the existing index {existing_idx}')

            for d_i, r_i in existing_idx:
                current_cost = dist[d_i, r_i]
                # driver constraint (row)
                worse_for_driver = dist[d_i, :] >= current_cost
                cost[d_i, worse_for_driver] = np.inf

                # rider constraint (column)
                worse_for_rider = dist[:, r_i] >= current_cost
                cost[worse_for_rider, r_i] = np.inf

                # keep original assignment feasible
                cost[d_i, r_i] = current_cost

            # print(f'dist matrix ={dist}')
            # print(f'cost matrix = {cost}')

        row_ind, col_ind = linear_sum_assignment(cost)
        assigned_pairs = [(driver_locs[r,2], rider_locs[c,2], dist[r,c]) for r,c in zip(row_ind,col_ind)] 
        
        # if len(Existing_pairs) != 0:
        #     for i in assigned_pairs_no_dist:
        #         #if i in Existing_pairs:
        #         print(f'i in pairs {i}')
        #         if i in Existing_pairs:
        #             print('yes')
        #     print(f'Existing paris {Existing_pairs} vs assigned pairs {assigned_pairs}')

        ### return only the pairs that are made new

        # tidying up and setting all to correct status
        for pair in assigned_pairs:
            # drivers: set idle to false and en route to true
            driver = All_drivers.get(pair[0])
            rider = All_riders.get(pair[1])

            moved_start = tuple(driver_locs[driver_locs[:, 2] == pair[0]][0, :2])

            driver.update_idle_status(False)
            driver.start_en_route(True)
            driver.set_origin_time(sim.current_time)
            driver.set_origin_location(moved_start)
            driver.update_location(moved_start)  # keep taxi location consistent with current moving position

            journey_time = sim.current_time + sim.distributions["journey"](pair[2])
            
            rider.update_service_status(service_status='assigned')
            rider.pickup_time = journey_time
            # set_new_start_and_end(self,current_time, dest_time, orig_loc, dest_loc,rider_no)                
            
            # print(sim.event_calendar)

            # only schedule if the driver is not currently picking up the rider
            if driver.passenger_id != pair[1]:
                print(f"assigning taxi {pair[0]} to rider {pair[1]}")

                # close the currently active empty segment before rerouting
                if getattr(driver, "path", None):
                    last_seg = driver.path[-1]
                    if last_seg.get("t_end") is None and not last_seg.get("has_rider", False):
                        driver.end_segment(t_end=sim.current_time)

                sim.add_event(
                    journey_time,
                    "pickup",
                    event_data={"rider_number": pair[1], "taxi_number": pair[0]},
                )
                
                driver.set_destination_time(journey_time)
                driver.set_destination_location(All_riders.get(pair[1]).location)
                driver.add_rider(pair[1])

                # start a new empty segment from the current moved location to the reassigned rider
                driver.start_segment(
                    t_start=sim.current_time,
                    start=moved_start,
                    end=rider.location,
                    has_rider=False
                )

            ## adding time to journey up to this point
            taxi_start_to_here = (
                (moved_start[0] - rider.location[0])**2 +
                (moved_start[1] - rider.location[1])**2
                )**0.5

            if sim.config["rider_choice_rule"] == 'closest' and sim.config["matching_strategy"]=='allow_rellocation': 
                driver.distance_covered += taxi_start_to_here
            # ignore this one
            driver.distance_covered_reassign += taxi_start_to_here
            # this one ok
            driver.set_origin_location(moved_start)

            #set from loc, to loc, from when, to when, passenger in taxi
            

            ## setting rider to in service and driver en route
            



def execute_termination(sim: Simulation):
    if sim.verbose:
        print(f'{round(sim.current_time, 2)}: terminating simulation')
