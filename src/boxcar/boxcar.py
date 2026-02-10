from boxcar.classes.simulation import Simulation
from boxcar.classes.generate import Distributions
from boxcar.classes.handlers import Handlers

def boxcar():
    distributions = Distributions(None)
    handlers = Handlers(None)
    
    sim = Simulation(distributions, handlers)

    distributions.simulation = sim
    handlers.simulation = sim
    
    sim.run()

boxcar()