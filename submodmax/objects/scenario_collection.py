from submodmax.objects.scenario import Scenario
from submodmax.utils.statistics_utils import calc_stats

class ScenarioCollection:
    def __init__(self):
        self.sc = {}
        self.stypes = []
        self.stored_value_stats = None
        self.stored_efficiency_stats = None
    
    def add_scenario(self, scenario: Scenario):
        stype = scenario.get_type()
        if stype not in self.sc:
            self.sc[stype] = {}
            self.stypes.append(stype)
        self.sc[stype][scenario.nbr] = scenario
    
    def get_scenarios_by_stype(self, stype: str) -> dict[int, Scenario]:
        return self.sc.get(stype, {})
    
    def get_stypes(self) -> list[str]: return self.stypes
    
    def generate_statistics(self) -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, dict[str, dict[str, float]]]]:
        """
        Returns two dictionaries containing statistics. The first is a dictionary of value statistics, 
        and the second is a dictionary of efficiency statistics.
        """
        value_stats = {}
        efficiency_stats = {}
        for stype, scenarios in self.sc.items():
            # Assume all scenarios are run with the same set of algorithms.
            first_scenario = next(iter(scenarios.values()))
            algorithms = list(first_scenario.assignments.keys())
            if stype not in value_stats:
                value_stats[stype] = {}
                efficiency_stats[stype] = {}
            for scenario in scenarios.values():
                for algorithm in algorithms:
                    assignment = scenario.assignments[algorithm]
                    if algorithm not in value_stats[stype]:
                        value_stats[stype][algorithm] = []
                        efficiency_stats[stype][algorithm] = []
                    value_stats[stype][algorithm].append(assignment.get_value())
                    efficiency_stats[stype][algorithm].append(assignment.get_efficiency())
            # Compute stats for each algorithm
            for algorithm in algorithms:
                value_stats[stype][algorithm] = calc_stats(value_stats[stype][algorithm])
                efficiency_stats[stype][algorithm] = calc_stats(efficiency_stats[stype][algorithm])

        self.stored_value_stats = value_stats
        self.stored_efficiency_stats = efficiency_stats
        return value_stats, efficiency_stats
        
    def __str__(self):
        return f"ScenarioCollection with {len(self.stypes)} scenario type(s)."
    
    def __repr__(self):
        return str(self)