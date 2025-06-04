# EXAMPLE - a larger graph

import networkx as nx
from algorithms import distributed_greedy, limited_information_greedy_with_sharing_rule
from informationSharing import generalized_distributed_greedy_rule, highest_marginal_contribution_rule
from scenario import Scenario
from visualize import visualize_assignment_comparison

G = nx.DiGraph()
G.add_edges_from([(1, 3), (1, 4), (1,10), (2, 3), (2, 4), (3, 7), (3, 9), (4, 5), (5, 6), (5, 7), (6, 9), (6, 10), (7, 8), (8, 9), (8, 10), (9, 10)])
target_values = {
    1: 2, 
    2: 1, 
    3: 4, 
    4: 2, 
    5: 1, 
    6: 3, 
    7: 1, 
    8: 4, 
    9: 2, 
    10: 5, 
    11: 2, 
    12: 3
}
action_sets = {
    1: [1, 3, 9, 4],
    2: [2, 3, 6, 7, 9],
    3: [3, 4, 5, 8, 11],
    4: [3, 4, 5, 1, 10, 12],
    5: [5, 6],
    6: [7, 8],
    7: [3, 4, 11],
    8: [2, 4, 6, 10],
    9: [5],
    10: [3, 10, 9, 7]

}

scenario = Scenario(G, action_sets, target_values)

dist_greedy = distributed_greedy(scenario)
gen_dist_greedy = limited_information_greedy_with_sharing_rule(scenario, generalized_distributed_greedy_rule)
high_marginal = limited_information_greedy_with_sharing_rule(scenario, highest_marginal_contribution_rule)

visualize_assignment_comparison(
    scenario,
    [dist_greedy, gen_dist_greedy, high_marginal], 
    assignment_titles=["Distributed Greedy", "Generalized Distributed Greedy (Self Sharing)", "Highest Marginal Contribution Sharing"],
    figure_directory="out",
)