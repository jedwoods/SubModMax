import networkx as nx
import itertools
from submodmax.objects.assignment import Assignment
from submodmax.utils.assignment_utils import score_assignment

class Scenario:
    def __init__(
        self, 
        G: nx.DiGraph, 
        action_sets: dict[int, list[int]], 
        target_values: dict[int, int],
        nbr: int = None
    ):
        self.G = G
        self.action_sets = action_sets
        self.target_values = target_values
        self.nbr = nbr
        self.optimal_assignment = self.brute_force_optimal_solution()
        self.optimal_value = self.optimal_assignment.get_value() if self.optimal_assignment != None else None

    def brute_force_optimal_solution(self) -> Assignment:
        """
        Computes the optimal assignment of agents to targets by generating all possible assignments and scoring them.
        """
        
        basf = None
        basf_val = -1
        keys = list(self.action_sets.keys())
        action_sets = [s[:] if s else [None] for s in self.action_sets.values()]
        possibilities = [
            Assignment(dict(zip(keys, values))) for values in itertools.product(*action_sets)
        ]

        for assignment in possibilities:
            sol_val = score_assignment(assignment, self.target_values)
            if sol_val > basf_val:
                basf = assignment
                basf_val = sol_val
        
        optimal_assignment = basf
        optimal_assignment.set_value(basf_val)
        optimal_assignment.set_efficiency(1.0)
        return optimal_assignment

    def assign_number(self, nbr: int):
        self.nbr = nbr

    def get_graph_copy(self) -> nx.DiGraph: return self.G.copy()
    def get_action_set(self) -> dict[int, list[int]]: return self.action_sets
    def get_target_values(self) -> dict[int, int]: return self.target_values
    def get_nbr(self) -> int: return self.nbr
    def get_optimal_assignment(self) -> Assignment: return self.optimal_assignment
    def get_optimal_value(self) -> int: return self.optimal_assignment.get_value()