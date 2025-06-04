# EXAMPLE - recreation of figure 1 from the Impact of Information in Distributed Submodular Maximization paper

import networkx as nx
from scenario import Scenario
from algorithms import distributed_greedy, limited_information_greedy_with_sharing_rule
from informationSharing import generalized_distributed_greedy_rule, highest_marginal_contribution_rule
from visualize import visualize_assignment_comparison

G = nx.DiGraph()
G.add_edges_from([(1, 3), (1, 4), (2, 3)])

target_values = {
    1: 2, 
    2: 1, 
    3: 4, 
    4: 2, 
    5: 1
}

action_sets = {
    1: [1, 3],
    2: [2, 3],
    3: [3, 4, 5],
    4: [3, 4, 5]
}

scenario = Scenario(G, action_sets, target_values, type="figure1")

dist_greedy = distributed_greedy(scenario)
gen_dist_greedy = limited_information_greedy_with_sharing_rule(scenario, generalized_distributed_greedy_rule)
high_marginal = limited_information_greedy_with_sharing_rule(scenario, highest_marginal_contribution_rule)

visualize_assignment_comparison(
    scenario, 
    [dist_greedy, gen_dist_greedy, high_marginal], 
    assignment_titles=["Distributed Greedy", "Generalized Distributed Greedy (Self Sharing)", "Highest Marginal Contribution Sharing"],
    figure_directory="examples/ex_out"
)