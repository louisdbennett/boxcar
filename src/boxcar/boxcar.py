from boxcar.classes.simulation import Simulation
from boxcar.classes.generate import Distributions
from boxcar.classes.handlers import Handlers
# from boxcar.get_results import save_results
# from boxcar.get_plots import plot_taxi_path
# from boxcar.get_plots import get_histos


CONFIGS = {
    "rider_choice_rule": ["closest", "shortest", "longest"],
    "allow_reassign_enroute": [False, True],
    "reassign_policy": ["closest"],
}

def boxcar():
    first = True
    distributions = Distributions(None)
    handlers = Handlers(None)

    cfg = {
        "rider_choice_rule": "closest",
        "allow_reallocation": True
    }

    # for trial in range(200):
    #     for rider_choice_rule in CONFIGS["rider_choice_rule"]:
    #             cfg = {
    #                 "rider_choice_rule": rider_choice_rule,
    #             }
    #             print(f"Running config: {cfg['rider_choice_rule']}")
    #             distributions = Distributions(None)
    #             handlers = Handlers(None)
                
                
    #             sim = Simulation(distributions, handlers, verbose=True, batch_length=0.1)
    #             sim.config = cfg
    #             distributions.simulation = sim
    #             handlers.simulation = sim
                
                
    #             sim.run()
    #             row = save_results(sim, cfg, csv_path="outputs/results.csv",run_name=trial, rewrite=first)
    #             #high_id = row["highest_earning_taxi_id"]
    #             #low_id  = row["lowest_earning_taxi_id"]
    #             #plot_taxi_path(sim.taxis[high_id], filename=f"high_{cfg['rider_choice_rule']}.png")
    #             #plot_taxi_path(sim.taxis[low_id], filename=f"low_{cfg['rider_choice_rule']}.png")



    #             first = False

    sim = Simulation(distributions, handlers, verbose=True, simulation_length=4)
    sim.config = cfg
    distributions.simulation = sim
    handlers.simulation = sim
                
                
    sim.run()
    # get_histos()


boxcar()