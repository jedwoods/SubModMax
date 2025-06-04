import heapq
import math
import numpy as np
from assignment import Assignment
from scenario import Scenario

def score_assignment(assignment: Assignment, target_values: dict[int, int]) -> int:
    """
    Return the score of an assignment of agents to targets.

    Args:
        assignment (Assignment): An assignment object that maps agents to their chosen targets.
        target_values (dict[int, int]): A dictionary mapping targets to their values.
    
    Returns:
        int: The score of the assignment.
    """
    score = 0
    unique_choices = set(assignment.get_choices())
    for choice in unique_choices:
        score += target_values[choice]
    return score

def n_largest_indices(lst, n):
    """
    Return the indices of the n largest elements in a list.

    Args:
        lst (list[int]): A list of values.
        n (int): The number of values to be returned
    
    Returns:
        list[int]: The indicies of the n largest elements (from largest to smallest by element size).
    """
    return [i for i, _ in heapq.nlargest(n, enumerate(lst), key=lambda x: x[1])]

def n_smallest_indices(lst, n):
    """
    Return the indices of the n smallest elements in a list.

    Args:
        lst (list[int]): A list of values.
        n (int): The number of values to be returned
    
    Returns:
        list[int]: The indicies of the n smallest elements (from smallest to largest by element size).
    """
    return [i for i, _ in heapq.nsmallest(n, enumerate(lst), key=lambda x: x[1])]

def count_ordered_dags(agents, edges):
    max_edges = agents * (agents - 1) // 2
    if edges > max_edges:
        return 0
    return math.comb(max_edges, edges)

def calc_stats(values: list[float]) -> dict[str, float]:
    return {
        'min': round(float(np.min(values)), 3),
        'max': round(float(np.max(values)), 3),
        'median': round(float(np.median(values)), 3),
        'mean': round(float(np.mean(values)), 3),
        'std_dev': round(float(np.std(values)), 3)
    }

def get_scenario_efficiency(scenario: Scenario, algorithm: str):
    assignment = scenario.get_assignment_by_algorithm(algorithm)
    return assignment.get_efficiency()

def get_best_scenarios(scenarios: Scenario, algorithm: str, n=5):
    return heapq.nlargest(n, scenarios, key=lambda s: get_scenario_efficiency(s, algorithm))

def get_worst_scenarios(scenarios: Scenario, algorithm: str, n=5):
    return heapq.nsmallest(n, scenarios, key=lambda s: get_scenario_efficiency(s, algorithm))