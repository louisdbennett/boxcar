from boxcar.classes.simulation import Simulation
from boxcar.classes.generate import Distributions
from boxcar.classes.handlers import Handlers
from boxcar.get_results import save_results

CONFIGS = {
    "rider_choice_rule": ["closest", "shortest", "longest"],
    "allow_reassign_enroute": [False, True],
    "reassign_policy": ["closest"],
}

def boxcar():
    first = True
    for rider_choice_rule in CONFIGS["rider_choice_rule"]:
                cfg = {
                    "rider_choice_rule": rider_choice_rule,
                }
                print(f"Running config: {cfg}")
                distributions = Distributions(None)
                handlers = Handlers(None)
                
                
                sim = Simulation(distributions, handlers, verbose=True, batch_length=0.1)
                sim.config = cfg
                distributions.simulation = sim
                handlers.simulation = sim

                
                sim.run()
                save_results(sim, cfg, csv_path="outputs/results.csv", rewrite=first)
                first = False
boxcar()