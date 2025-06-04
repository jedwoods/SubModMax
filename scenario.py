import networkx as nx
import itertools
from assignment import Assignment

class Scenario:
    def __init__(
        self, 
        G: nx.DiGraph, 
        action_sets: dict[int, list[int]], 
        target_values: dict[int, int],
        nbr: int = None, 
        type: str = None
    ):
        self.G = G
        self.action_sets = action_sets
        self.target_values = target_values
        self.nbr = nbr
        self.type = type
        self.assignments = {}
        self.brute_force_optimal_solution()

    def assign_number(self, nbr: int):
        self.nbr = nbr

    def assign_type(self, type: str):
        self.type = type

    def brute_force_optimal_solution(self):
        """
        Computes the optimal assignment of agents to targets by generating all possible assignments and scoring them.
        """
        
        basf = None
        basf_val = 0
        # Generate all possible assignments
        keys = list(self.action_sets.keys())
        possibilities = [
            Assignment(dict(zip(keys, values))) for values in itertools.product(*self.action_sets.values())
        ]

        from helpers import score_assignment
        for assignment in possibilities:
            sol_val = score_assignment(assignment, self.target_values)
            if sol_val > basf_val:
                basf = assignment
                basf_val = sol_val
        
        self.optimal_assignment = basf
        self.optimal_assignment.set_value(basf_val)
    
    def add_assignment(self, algorithm_title: str, assignment: Assignment):
        if self.optimal_assignment:
            assignment.set_efficiency(round(assignment.get_value() / self.optimal_assignment.get_value(), 3))
        self.assignments[algorithm_title] = assignment

    def get_graph_copy(self) -> nx.DiGraph: return self.G.copy()
    def get_action_set(self) -> dict[int, list[int]]: return self.action_sets
    def get_target_values(self) -> dict[int, int]: return self.target_values
    def get_nbr(self) -> int: return self.nbr
    def get_type(self) -> float: return self.type
    def get_assignment_by_algorithm(self, algorithm_title: str) -> Assignment: return self.assignments.get(algorithm_title, None)
    def get_optimal_assignment(self) -> Assignment: return self.optimal_assignment
    def get_optimal_value(self) -> int: return self.optimal_assignment.get_value()
    
    def __str__(self):
        nbr = self.nbr if self.nbr is not None else "?"
        type = self.type if self.type is not None else "?"
        return f"S{nbr} {type}"
    
    def __repr__(self):
        return str(self)