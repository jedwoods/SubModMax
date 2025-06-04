import tabulate
import csv
from scenario import Scenario
from helpers import calc_stats

class ScenarioCollection:
    def __init__(self):
        self.sc = {}
        self.stypes = []
    
    def add_scenario(self, scenario: Scenario):
        stype = scenario.get_type()
        if stype not in self.sc:
            self.sc[stype] = {}
            self.stypes.append(stype)
        self.sc[stype][scenario.nbr] = scenario
    
    def get_scenarios_by_stype(self, stype: str) -> dict[int, Scenario]:
        return self.sc.get(stype, {})
    
    def get_stypes(self) -> list[str]: return self.stypes
    
    def summarize_results(self, export_stats: bool = False) -> dict[str, dict[str, dict[str, float]]]:
        """
        Returns a dictionary containing statistics for the values and efficiencies of each algorithm-scenario combination and prints a 
        table containing average values and efficiencies for each algorithm across all scenario types.
        Assumes every scenario type is run with every algorithm.
        """
        stat_dict = {}
        for stype, scenarios in self.sc.items():
            # Assume all scenarios are run with the same set of algorithms.
            first_scenario = next(iter(scenarios.values()))
            algorithms = list(first_scenario.assignments.keys())
            if stype not in stat_dict:
                stat_dict[stype] = {}
            for scenario in scenarios.values():
                for algorithm in algorithms:
                    assignment = scenario.assignments[algorithm]
                    if algorithm not in stat_dict[stype]:
                        stat_dict[stype][algorithm] = {
                            "values": [],
                            "efficiencies": []
                        }
                    stat_dict[stype][algorithm]["values"].append(assignment.get_value())
                    stat_dict[stype][algorithm]["efficiencies"].append(assignment.get_efficiency())
            # Compute stats for each algorithm
            for algorithm in algorithms:
                stat_dict[stype][algorithm]["values"] = calc_stats(stat_dict[stype][algorithm]["values"])
                stat_dict[stype][algorithm]["efficiencies"] = calc_stats(stat_dict[stype][algorithm]["efficiencies"])

        # Prepare table data
        scenario_types = list(stat_dict.keys())
        algorithms = list(stat_dict[scenario_types[0]].keys())

        # Build value table
        value_table = []
        for stype in scenario_types:
            row = [stype]
            for alg in algorithms:
                avg_val = stat_dict[stype][alg]["values"]["mean"]
                row.append(round(avg_val, 3))
            value_table.append(row)

        # Build efficiency table
        efficiency_table = []
        for stype in scenario_types:
            row = [stype]
            for alg in algorithms:
                avg_eff = stat_dict[stype][alg]["efficiencies"]["mean"]
                row.append(round(avg_eff, 3))
            efficiency_table.append(row)

        headers = ["Scenario Type"] + algorithms
        print("\nAverage Solution Value:\n")
        print(tabulate.tabulate(value_table, headers=headers, tablefmt="simple"))
        print("\n\nAverage Solution Efficiency:\n")
        print(tabulate.tabulate(efficiency_table, headers=headers, tablefmt="simple"))

        if export_stats:
            rows = []

            for scenario, strategies in stat_dict.items():
                for strategy, metrics in strategies.items():
                    for metric_type, stats in metrics.items():
                        row = {
                            'Scenario': scenario,
                            'Strategy': strategy,
                            'Metric Type': metric_type
                        }
                        row.update(stats)
                        rows.append(row)

            # Write to CSV
            fieldnames = ['Scenario', 'Strategy', 'Metric Type', 'min', 'max', 'median', 'mean', 'std_dev']

            with open('stat_dict.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

        return stat_dict
        
    def __str__(self):
        return f"ScenarioCollection with {len(self.stypes)} scenario type(s)."
    
    def __repr__(self):
        return str(self)