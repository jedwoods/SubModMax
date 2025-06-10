import heapq
from submodmax.objects.scenario import Scenario

def get_scenario_efficiency(scenario: Scenario, algorithm: str):
    assignment = scenario.get_assignment_by_algorithm(algorithm)
    return assignment.get_efficiency()

def get_best_scenarios(scenarios: Scenario, algorithm: str, n=5):
    return heapq.nlargest(n, scenarios, key=lambda s: get_scenario_efficiency(s, algorithm))

def get_worst_scenarios(scenarios: Scenario, algorithm: str, n=5):
    return heapq.nsmallest(n, scenarios, key=lambda s: get_scenario_efficiency(s, algorithm))