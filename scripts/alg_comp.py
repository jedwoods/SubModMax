from submodmax.simulators import algorithms_versus_scenarios
from submodmax.algorithms import *
from submodmax.information_sharing_rules import *
from submodmax.scenario_builders import *

# Compares performance of different information sharing strategies on different graph types.

sc = algorithms_versus_scenarios(
    scenario_builders=[generate_line_graph, generate_random_linearized_dag],
    scenario_builder_params=[[7, 10], [7, 10, 7]],
    scenario_type_titles=["Line Graph", "Random Linearized DAG"],
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
    runs_per_scenario=1000,
    create_visuals=True
)