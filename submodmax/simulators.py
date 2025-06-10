import os
from typing import Callable, Any
from submodmax.objects.scenario import Scenario
from submodmax.objects.assignment import Assignment
from submodmax.objects.scenario_collection import ScenarioCollection
from submodmax.visualize import visualize_best_worst_scenarios
from submodmax.utils.statistics_utils import export_stat_dict_to_csv, print_stats
from submodmax.globals import DEFAULT_OUT_DIR

def algorithms_versus_scenarios(
    scenario_builders: list[Callable[..., Scenario]], 
    scenario_builder_params: list[list[Any]],
    scenario_type_titles: list[str],
    algorithms: list[Callable[..., Assignment]], 
    algorithm_params: list[list[Any]],
    algorithm_titles: list[str],
    runs_per_scenario: int = 1000,
    create_visuals = False,
    out_directory = DEFAULT_OUT_DIR
):
    """
    A simulation that runs multiple algorithms on multiple scenario types, collecting statistics and optionally creating visualizations.

    Args:
        scenario_builders (list[Callable[..., Scenario]]): List of functions that create scenarios.
        scenario_builder_params (list[list[Any]]): Parameters for each scenario builder function.
        scenario_type_titles (list[str]): Titles for each scenario type.
        algorithms (list[Callable[..., Assignment]]): List of algorithm functions to run on the scenarios.
        algorithm_params (list[list[Any]]): Parameters for each algorithm function.
        algorithm_titles (list[str]): Titles for each algorithm.
        runs_per_scenario (int): Number of runs per scenario type. Default is 1000.
        create_visuals (bool): Whether to create visualizations of the results. Default is False.
        out_directory (str): Directory to save output files and visualizations. Default is DEFAULT_OUT_DIR.
    
    Returns:
        ScenarioCollection: A collection of scenarios with their assignments and statistics.
    """
    scenario_type_count = len(scenario_builders)
    algorithm_count = len(algorithms)
    sc = ScenarioCollection()

    results_file_path = os.path.join(out_directory, "sim_results.txt")
    with open(results_file_path, "w") as f:
        print(f"Measuring performance of {algorithm_count} algorithms across {scenario_type_count} scenario types with {runs_per_scenario} scenarios per scenario type.", file=f)
        
        for stype_index in range(scenario_type_count):
            print(f"Running algorithms on scenario type {scenario_type_titles[stype_index]}...", end="")
            for run in range(runs_per_scenario):
                S = scenario_builders[stype_index](*scenario_builder_params[stype_index])
                S.assign_type(scenario_type_titles[stype_index])
                S.assign_number(run + 1)
                sc.add_scenario(S)
                
                for alg_index in range(algorithm_count):
                    alg_title = algorithm_titles[alg_index]
                    alg_assignment = algorithms[alg_index](S, *algorithm_params[alg_index])
                    S.add_assignment(alg_title, alg_assignment)
            print(f"  done!")
        
        v_dict, e_dict = sc.generate_statistics()
        export_stat_dict_to_csv(v_dict, "value_stats.csv", out_directory)
        export_stat_dict_to_csv(e_dict, "efficiency_stats.csv", out_directory)
        print("\nAverage Efficiency of Algorithms across Scenario Types", file=f)
        print_stats(e_dict, 'mean', f)
        
        if create_visuals:
            fig_dir = os.path.join(out_directory, "figures")
            print(f"\nCreating visualizations in [{fig_dir}]...", end="")
            for stype in sc.get_stypes():
                scenarios = sc.get_scenarios_by_stype(stype).values()
                for alg_title in algorithm_titles:
                    visualize_best_worst_scenarios(scenarios, alg_title, f"{alg_title} on {stype}", figure_directory=fig_dir, arc_rads_scale=0.3)
            print(f"  done!\n")
    return sc
