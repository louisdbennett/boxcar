from boxcar.classes.simulation import Simulation
from boxcar.classes.generate import Distributions
from boxcar.classes.handlers import Handlers
from boxcar.get_results import save_results
from boxcar.get_plots import plot_taxi_path
from boxcar.get_plots import get_histos
from boxcar.test_hypothesis import test_all_configs


# Configurations to test
CONFIGS = {
    "rider_choice_rule": ["closest", "shortest", "longest"],
    "matching_strategy": [None, 'allow_relocation', 'batching'],
    'batch_length': [0.01, 0.05, 0.075, 0.1, 0.2]
}


def boxcar():
    # Rewrite CSV only on the first run
    first = True

    # Repeat full experiment 200 times
    for trial in range(200):
        for cr in CONFIGS['rider_choice_rule']:
            # Only closest is combined with relocation/batching
            if cr == 'closest':
                for ms in CONFIGS['matching_strategy']:
                    if ms == 'batching':
                        for bl in CONFIGS['batch_length']:
                            cfg = {
                                'rider_choice_rule': cr,
                                'matching_strategy': ms,
                                'batch_length': bl
                            }

                            distributions = Distributions(None)
                            handlers = Handlers(None)

                            sim = Simulation(cfg, distributions, handlers, verbose=True)
                            distributions.simulation = sim
                            handlers.simulation = sim

                            sim.run()

                            row = save_results(sim, cfg, csv_path="outputs/results.csv", rewrite=first)
                            first = False
                    else:
                        cfg = {
                            'rider_choice_rule': cr,
                            'matching_strategy': ms,
                        }

                        distributions = Distributions(None)
                        handlers = Handlers(None)

                        sim = Simulation(cfg, distributions, handlers, verbose=True)
                        distributions.simulation = sim
                        handlers.simulation = sim

                        sim.run()

                        row = save_results(sim, cfg, csv_path="outputs/results.csv", rewrite=first)
                        first = False
            else:
                # shortest and longest run without matching strategy
                cfg = {
                    'rider_choice_rule': cr,
                }

                distributions = Distributions(None)
                handlers = Handlers(None)

                sim = Simulation(cfg, distributions, handlers, verbose=True)
                distributions.simulation = sim
                handlers.simulation = sim

                sim.run()

                row = save_results(sim, cfg, csv_path="outputs/results.csv", rewrite=first)
                first = False

    # Compare all configs against the baseline
    test_all_configs(
        csv_path="outputs/results.csv",
        baseline_cfg="cr=closest, ms=None, bl=None",
        out_csv="outputs/hypothesis_tests_all_vs_baseline.csv",
        alpha=0.05
    )

    # Create histograms from results
    get_histos()


boxcar()