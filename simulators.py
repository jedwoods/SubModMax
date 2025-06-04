from typing import Callable, Any
from scenario import Scenario
from assignment import Assignment
from scenarioCollection import ScenarioCollection
from visualize import visualize_best_worst_scenarios
from globals import DEFAULT_FIG_DIR

def algorithms_versus_scenarios(
    scenario_builders: list[Callable[..., Scenario]], 
    scenario_builder_params: list[list[Any]],
    scenario_type_titles: list[str],
    algorithms: list[Callable[..., Assignment]], 
    algorithm_params: list[list[Any]],
    algorithm_titles: list[str],
    runs_per_scenario: int = 1000,
    create_visuals = False,
    figure_directory = DEFAULT_FIG_DIR
):
    scenario_type_count = len(scenario_builders)
    algorithm_count = len(algorithms)
    sc = ScenarioCollection()

    print(f"\nMeasuring performance of {algorithm_count} algorithms across {scenario_type_count} scenario types with {runs_per_scenario} scenarios per scenario type...")
    
    for stype_index in range(scenario_type_count):
        for run in range(runs_per_scenario):
            S = scenario_builders[stype_index](*scenario_builder_params[stype_index])
            S.assign_type(scenario_type_titles[stype_index])
            S.assign_number(run + 1)
            sc.add_scenario(S)
            
            for alg_index in range(algorithm_count):
                alg_title = algorithm_titles[alg_index]
                alg_assignment = algorithms[alg_index](S, *algorithm_params[alg_index])
                S.add_assignment(alg_title, alg_assignment)
    
    stat_dict = sc.summarize_results(export_stats=True)
    
    if create_visuals:
        print(f"\nCreating visualizations in {figure_directory}...\n")
        for stype in sc.get_stypes():
            scenarios = sc.get_scenarios_by_stype(stype).values()
            for alg_title in algorithm_titles:
                visualize_best_worst_scenarios(scenarios, alg_title, f"{alg_title} on {stype}", figure_directory, arc_rads_scale=0.3)
        print(f"Done!\n")
    return sc, stat_dict
