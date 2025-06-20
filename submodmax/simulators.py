import os
import csv
import numpy as np
from collections import defaultdict
from typing import Callable, Any, Dict
from submodmax.objects.scenario import Scenario
from submodmax.objects.assignment import Assignment
from submodmax.visualize import visualize_best_worst_scenarios
from submodmax.globals import DEFAULT_OUT_DIR

def algorithms_versus_scenarios(
    scenario_builders: list[Callable[..., Scenario]],
    scenario_builder_params: list[list[Any]],
    scenario_type_titles: list[str],
    algorithms: list[Callable[..., Assignment]],
    algorithm_params: list[list[Any]],
    algorithm_titles: list[str],
    runs_per_scenario: int = 1000,
    create_visuals: bool = False,
    out_directory: str = DEFAULT_OUT_DIR,
):
    os.makedirs(out_directory, exist_ok=True)

    # Data accumulators
    stats = defaultdict(lambda: defaultdict(lambda: {'values': [], 'effs': [], 'assignments': []}))

    # --- RUN SIMULATIONS ---
    for stype_idx, stype in enumerate(scenario_type_titles):
        build = scenario_builders[stype_idx]
        build_params = scenario_builder_params[stype_idx]
        for run in range(runs_per_scenario):
            scenario = build(*build_params)
            scenario.assign_number(run + 1)
            for alg_idx, alg_title in enumerate(algorithm_titles):
                alg = algorithms[alg_idx]
                params = algorithm_params[alg_idx]
                assignment: Assignment = alg(scenario, *params)
                stats[stype][alg_title]['values'].append(assignment.value)
                stats[stype][alg_title]['effs'].append(assignment.efficiency)
                if create_visuals:
                    stats[stype][alg_title]['assignments'].append((scenario, assignment))

    # --- WRITE CSV STATISTICS ---
    for metric, filename in [('values', 'solution_values.csv'), ('effs', 'solution_efficiencies.csv')]:
        path = os.path.join(out_directory, filename)
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            header = ['scenario_type', 'algorithm', 'mean', 'median', 'min', 'max', 'std', 'num_runs']
            writer.writerow(header)
            for stype in scenario_type_titles:
                for alg in algorithm_titles:
                    arr = np.array(stats[stype][alg][metric])
                    if arr.size == 0:
                        continue
                    writer.writerow([
                        stype, alg,
                        f"{np.mean(arr):.3f}",
                        f"{np.median(arr):.3f}",
                        f"{np.min(arr):.3f}",
                        f"{np.max(arr):.3f}",
                        f"{np.std(arr, ddof=1):.3f}",
                        arr.size
                    ])

        print(f"Wrote {metric} stats to {path}")

    # --- CREATE VISUALIZATIONS (sorted by efficiency) ---
    if create_visuals and runs_per_scenario >= 10:
        for stype in scenario_type_titles:
            for alg in algorithm_titles:
                data = stats[stype][alg]['assignments']
                if len(data) >= 10:
                    # Sort by assignment efficiency
                    data_sorted = sorted(data, key=lambda sa: sa[1].efficiency)

                    # Worst 5: lowest to higher efficiency
                    worst_5 = data_sorted[:5]

                    # Best 5: highest to lower efficiency
                    best_5 = data_sorted[-5:][::-1]

                    visualize_best_worst_scenarios(
                        best=best_5,
                        worst=worst_5,
                        scenario_type=stype,
                        algorithm_title=alg,
                        output_dir=out_directory
                    )
    return stats 