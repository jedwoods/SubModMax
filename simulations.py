from simulators import algorithms_versus_scenarios
from algorithms import distributed_greedy, limited_information_greedy_with_sharing_rule
from informationSharing import *
from scenarioBuilders import generate_line_graph, generate_random_linearized_dag, pass_to_last, pair_agents

# sc, stat_dict = algorithms_versus_scenarios(
#     scenario_builders=[generate_line_graph, generate_random_linearized_dag, pass_to_last, pair_agents],
#     scenario_builder_params=[[4, 5], [4, 5, 3], [4, 5], [4, 5]],
#     scenario_type_titles=["Line Graph", "Random Linearized DAG", "Pass to Last", "Pair Agents"],
#     algorithms=[distributed_greedy, limited_information_greedy_with_sharing_rule, limited_information_greedy_with_sharing_rule],
#     algorithm_params=[
#         [],
#         [generalized_distributed_greedy_rule],
#         [highest_marginal_contribution_rule]
#     ],
#     algorithm_titles=["Distributed Greedy", "Generalized Distributed Greedy", "Highest Marginal Contribution"],
#     runs_per_scenario=1000,
#     create_visuals=True
# )

sc, stat_dict = algorithms_versus_scenarios(
    scenario_builders=[generate_line_graph, generate_random_linearized_dag, pass_to_last, pair_agents],
    scenario_builder_params=[[4, 5], [4, 5, 3], [4, 5], [4, 5]],
    scenario_type_titles=["Line Graph", "Random Linearized DAG", "Pass to Last", "Pair Agents"],
    algorithms=[limited_information_greedy_with_sharing_rule for _ in range(8)],
    algorithm_params=[
        [highest_marginal_contribution_rule],
        [most_upstream_agent_rule],
        [least_likely_known_rule],
        [random_known_agent_rule],
        [rotating_known_agent_rule],
        [degree_centrality_rule],
        [betweenness_centrality_rule],
        [closeness_centrality_rule]
    ],
    algorithm_titles=[
        "Highest Marginal Contribution",
        "Most Upstream Agent",
        "Least Likely Known",
        "Random Known Agent",
        "Rotating Known Agent",
        "Degree Centrality",
        "Betweenness Centrality",
        "Closeness Centrality"
    ],
    runs_per_scenario=1000,
    create_visuals=True
)