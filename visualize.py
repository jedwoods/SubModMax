import os
import matplotlib.pyplot as plt
import networkx as nx
import tabulate
from scenario import Scenario
from assignment import Assignment
from helpers import score_assignment, get_best_scenarios, get_worst_scenarios
from globals import DEFAULT_FIG_DIR, DEFAULT_ARC

def visualize_scenario(
        scenario: Scenario,
        title: str = "Visual",
        assignment: Assignment = None,
        metric: str = "score",
        metric_value: float = None, 
        ax: plt.Axes = None,
        arc_rads_scale: float = DEFAULT_ARC,
        figure_directory: str = None
) -> None:
    """
    A function that visualizes a given `scenario` (and optionally an `assignment` of agents to targets within the context of that `scenario`).

    Args:
        scenario (Scenario): The scenario to be visualized.
        title (str): The title to be used in the visualization.
        assignment (dict[int, int]): The assignment to visualized.
        metric (str): The metric to be displayed with the title ('score' or 'efficiency').
        metric_value (float): The value of the metric.
        ax (plt.Axes): The ax that the visual should be plotted on.
        arc_rads_scale (float): A scalar factor that determines how much the edges between non-adjacent
            agents should be arced.
        figure_directory (str): The directory where the figure should be saved. If None, the figure will not be saved.
    """

    G = scenario.get_graph_copy()
    action_sets = scenario.get_action_set()
    target_values = scenario.get_target_values()

    if ax is None:
        fig, ax = plt.subplots()
    
    # Agent positioning
    agent_count = len(G)
    target_count = len(target_values)
    node_size = 500 * (5 / agent_count)
    rad = arc_rads_scale * (agent_count / 5)
    pseudo_targets = {target: agent_count + target for target in range(1, target_count + 1)}
    G.add_nodes_from(pseudo_targets.values())
    pos_top = {agent: (agent - 1, 0.1) for agent in range(1, agent_count + 1)}
    pos_bottom = {pseudo_targets[i]: (i - 1, -0.2) for i in range(1, target_count + 1)}
    x_coords_top = [pos_top[agent][0] for agent in pos_top]
    center_x_top = sum(x_coords_top) / len(x_coords_top)
    shift_x = center_x_top - (len(pos_bottom) - 1) / 2 
    pos_bottom_centered = {target: (pos_bottom[target][0] + shift_x, pos_bottom[target][1]) for target in pos_bottom}
    pos = {**pos_top, **pos_bottom_centered} 

    # Draw agent graph
    nx.draw_networkx_nodes(G, pos, nodelist=range(1, agent_count + 1), ax=ax, node_color='lightblue', node_size=node_size)
    straight_edges = [(u, v) for u, v in G.edges() if abs(u - v) == 1]
    curved_edges = [(u, v) for u, v in G.edges() if abs(u - v) > 1]
    nx.draw_networkx_edges(G, pos, edgelist=straight_edges, ax=ax, edge_color='gray', arrows=True, arrowstyle='->', node_size=node_size)
    nx.draw_networkx_edges(G, pos, edgelist=curved_edges, ax=ax, connectionstyle=f'arc3,rad={-rad}', edge_color='gray', arrows=True, arrowstyle='->', node_size=node_size)

    # Draw targets and action sets
    nx.draw_networkx_nodes(G, pos, nodelist=pseudo_targets.values(), ax=ax, node_color='gold', node_size=node_size)
    action_set_edges = [(u, v + agent_count) for u, action_set in action_sets.items() for v in action_set]
    nx.draw_networkx_edges(G, pos, edgelist=action_set_edges, ax=ax, edge_color='gray', arrows=True, arrowstyle='->', node_size=node_size)

    # Draw in assignment (if applicable)
    if assignment:
        assignment_edges = [(agent, pseudo_targets[target]) for agent, target in assignment.assignment.items()]
        nx.draw_networkx_edges(G, pos, edgelist=assignment_edges, ax=ax, edge_color='red', arrows=True, arrowstyle='->', node_size=node_size)

    # Agent and target labeling
    agent_labels = {agent : agent for agent in range(1, agent_count + 1)}
    target_labels = dict(zip(pseudo_targets.values(), target_values.values()))
    labels = {**agent_labels, **target_labels}
    nx.draw_networkx_labels(G, pos, ax=ax, labels=labels)

    # Target identification
    for real_target, pseudo_target in pseudo_targets.items():
        x, y = pos[pseudo_target]
        ax.text(x, y - 0.08, rf"$t_{{{real_target}}}$", fontsize=10, ha='center', va='top')

    # Customize title
    if assignment and metric_value:
        if metric == "score":
            mod_title = rf"{title} - $f(x) = {metric_value}$"
        if metric == "efficiency":
            mod_title = rf"{title} - $\gamma(x) = {metric_value}$"
        
    ax.set_title(mod_title, pad=20)
    ax.set_ylim(-0.6, 0.4)
    ax.axis('off')

    if figure_directory:
        os.makedirs(figure_directory, exist_ok=True)
        save_path = os.path.join(figure_directory, f"{title.replace(' ','')}.png")
        plt.savefig(save_path)
        plt.close()

def visualize_assignment_comparison(
        scenario: Scenario,
        assignment_list: list[Assignment],
        assignment_titles: list[str] = None,
        figure_directory: str = None
) -> None:
    """
    A function for visualizing the comparison of different assignments on a given `scenario`.

    Args:
        scenario (Scenario): The scenario the assignments are based on.
        assignment_list (list[Assignment]): A list of the agent to target assignments to be compared.
        assignment_titles (list[str]): A list of titles to be associated with the assignments in the visuals.
        figure_directory (str): The directory where the figures should be saved. If None, the figures will not be saved.
    """

    G = scenario.get_graph_copy()
    target_values = scenario.get_target_values()

    # Compute optimal solution for comparison
    opt_assignment = scenario.get_optimal_assignment()
    opt_val = opt_assignment.get_value()

    agent_count = len(G)
    column_labels = ["Rule"] + [f"x{i}" for i in range(1, agent_count + 1)] + ["f(x)"] + ["γ(x)"]
    data = [["Optimal"] + [f"t{target}" for target in opt_assignment.get_choices()] + [opt_val] + [1.0]]

    if not assignment_titles:
        assignment_titles = [f"Assignment #{i}" for i in range(1, len(assignment_list))]

    visualize_scenario(scenario, title="Optimal", assignment=opt_assignment, metric_value=opt_val, figure_directory=figure_directory)

    for index, assignment in enumerate(assignment_list):
        assignment_val = score_assignment(assignment, target_values)
        visualize_scenario(scenario, title=assignment_titles[index], assignment=assignment, metric_value=assignment_val, figure_directory=figure_directory)
        data.append([assignment_titles[index]] + [f"t{target}" for target in assignment.get_choices()] + [assignment_val] + [round(assignment_val / opt_val, 3)])

    print("\nAssignment Comparison:\n")
    print(tabulate.tabulate(data, headers=column_labels, tablefmt="simple"))
    if figure_directory:
        print(f"\nVisualizations saved to {figure_directory}\n")

def visualize_best_worst_scenarios(
        scenarios: list[Scenario],
        algorithm: str,
        visual_title: str,
        figure_directory: str = DEFAULT_FIG_DIR,
        arc_rads_scale: float = DEFAULT_ARC
) -> None:
    """
    A visualization function to be used in conjunction with a simulation. Visualizes the five best and five worst scenarios
    for a given algorithm.

    Args:
        scenarios (list[Scenario]): A list of scenarios to be considered.
        algorithm (str): The algorithm being considered for the set of scenarios.
        visual_title (str): The title for the visualization.
        figure_directory (str): The directory where the figures will be saved.
        arc_rads_scale (float): A scalar factor that determines how much the edges between non-adjacent
            agents should be arced.
    """
    best_titles = ["Best", "2nd Best", "3rd Best", "4th Best", "5th Best"]
    worst_titles = ["Worst", "2nd Worst", "3rd Worst", "4th Worst", "5th Worst"]

    best_scenarios = get_best_scenarios(scenarios, algorithm, n=5)
    worst_scenarios = get_worst_scenarios(scenarios, algorithm, n=5)

    fig, axes = plt.subplots(2, 5, figsize=(20, 10))
    for index in range(5):
        S = best_scenarios[index]
        assignment = S.get_assignment_by_algorithm(algorithm)
        efficiency = assignment.get_efficiency()
        visualize_scenario(
            scenario=best_scenarios[index], 
            title=best_titles[index] + f"\nScenario {S.nbr}", 
            assignment=assignment,
            metric="efficiency",
            metric_value=efficiency,
            ax=axes[0][index],
            arc_rads_scale=arc_rads_scale
        )
        S = worst_scenarios[index]
        assignment = S.get_assignment_by_algorithm(algorithm)
        efficiency = assignment.get_efficiency()
        visualize_scenario(
            scenario=worst_scenarios[index], 
            title=worst_titles[index] + f"\nScenario {S.nbr}", 
            assignment=assignment,
            metric="efficiency",
            metric_value=efficiency,
            ax=axes[1][index],
            arc_rads_scale=arc_rads_scale
        )
    
    fig.suptitle(visual_title)
    fig.tight_layout()

    os.makedirs(figure_directory, exist_ok=True)
    save_path = os.path.join(figure_directory, f"bw_{visual_title.replace(' ','')}.png")
    plt.savefig(save_path)
    plt.close()
        