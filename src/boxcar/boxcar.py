from boxcar.classes.simulation import Simulation
from boxcar.classes.generate import Distributions
from boxcar.classes.handlers import Handlers

CONFIGS = {
    "rider_choice_rule": ["closest", "shortest", "longest"],
    "allow_reassign_enroute": [False, True],
    "reassign_policy": ["closest"],
}

def boxcar():
    for rider_choice_rule in CONFIGS["rider_choice_rule"]:
                cfg = {
                    "rider_choice_rule": rider_choice_rule,
                }

                distributions = Distributions(None)
                handlers = Handlers(None)
                
                
                sim = Simulation(distributions, handlers)
                sim.config = cfg
                distributions.simulation = sim
                handlers.simulation = sim

                print(f"Running config: {cfg}")
                sim.run()

boxcar()