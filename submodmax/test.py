import networkx as nx
from submodmax.objects.scenario import Scenario
from submodmax.algorithms import *
from submodmax.information_sharing_rules import *
from submodmax.visualize import visualize_scenario
from submodmax.simulators import algorithms_versus_scenarios

def gen():
    G = nx.DiGraph()
    G.add_edges_from([(1, 2), (2, 3), (3, 4)])
    return Scenario(
        G,
        {1: [], 2: [1, 2], 3: [1, 3], 4: []},
        {1: 2, 2: 1, 3: 1}
    )

sc = algorithms_versus_scenarios(
    scenario_builders=[gen],
    scenario_builder_params=[[]],
    scenario_type_titles=["Near Empty"],
    algorithms=[distributed_greedy] + [greedy_with_information_sharing_rule for _ in range(11)],
    algorithm_params=[
        [],
        [generalized_distributed_greedy_rule],
        [highest_marginal_contribution_rule],
        [maximize_downstream_reach],
        [reach_and_value_rule],
        [least_likely_known_amongst_neighborhood_rule],
        [adaptive_sharing_rule],
        [most_upstream_agent_rule],
        [random_known_agent_rule],
        [degree_centrality_rule],
        [betweenness_centrality_rule],
        [closeness_centrality_rule]
    ],
    algorithm_titles=[
        "Distributed Greedy",
        "Generalized Distributed Greedy",
        "Highest Marginal Contribution",
        "Maximize Downstream Reach",
        "Reach and Value",
        "Least Likely Known Amongst Neighborhood",
        "Adaptive Sharing",
        "Most Upstream Agent",
        "Random Known Agent",
        "Degree Centrality",
        "Betweenness Centrality",
        "Closeness Centrality",
    ],
    runs_per_scenario=10,
    create_visuals=True
)