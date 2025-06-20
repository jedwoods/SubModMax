# Updates in progress...

import os
from typing import Callable, Any
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
        ???
    """
    scenario_type_count = len(scenario_builders)
    algorithm_count = len(algorithms)
    stype_dict = {}
    scenario_dict = {}
    for stype_index in range(scenario_type_count):
        stype = scenario_type_titles[stype_index]
        stype_dict[stype] = {}
        scenario_dict[stype] = {}
        for run in range(runs_per_scenario):
            s = scenario_builders[stype_index](*scenario_builder_params[stype_index])
            s.assign_number(run + 1)
            stype_dict[stype][s.get_nbr()] = {}
            scenario_dict[stype][s.get_nbr()] = s
            for alg_index in range(algorithm_count):
                alg_assignment = algorithms[alg_index](s, *algorithm_params[alg_index])
                stype_dict[stype][s.get_nbr()][algorithm_titles[algorithm_titles]] = alg_assignment
