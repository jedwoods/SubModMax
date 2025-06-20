import networkx as nx
import random
from typing import Callable
from submodmax.objects.scenario import Scenario
from submodmax.action_target_generators import default_target_generator
from submodmax.visualize import visualize_scenario

def generate_line_graph(
    agent_count: int, 
    target_count: int, 
    target_generator: Callable[[int, int], tuple[dict[int, int], dict[int, int]]] = default_target_generator, 
    view: bool = False
) -> Scenario:
    """
    Generates a `Scenario` whose information sharing graph is a line graph. The `action_sets` and `target_values` are provided
    by the given `target_generator` function.

    Args:
        agent_count (int): The number of agents to be present in the scenario.
        target_count (int): The number of targets to be present in the scenario.
        target_generator (Callable[[int, int], tuple[dict[int, int], dict[int, int]]]): A function that generates `action_sets` and
            `target_values` based on the `agent_count` and `target_count`.
        view (bool): Determines whether (True) or not (False) the `Scenario` will be viewed after creation.
    
    Returns:
        Scenario: the generated `Scenario`.
    """
    
    
    G = nx.DiGraph()
    G.add_edges_from([(u, u + 1) for u in range(1, agent_count)])
    action_sets, target_values = target_generator(agent_count, target_count)
    s = Scenario(G, action_sets, target_values)
    if view: visualize_scenario(s, "Scenario Visualization")
    return s

def generate_random_linearized_dag(
    agent_count: int,
    target_count: int,
    edge_count: int,
    target_generator: Callable[[int, int], tuple[dict[int, int], dict[int, int]]] = default_target_generator,
    view: bool = False
) -> Scenario:
    """
    Generates a `Scenario` whose information sharing graph is a randomly generated linearized DAG. The `action_sets` and `target_values` are provided
    by the given `target_generator` function.

    Args:
        agent_count (int): The number of agents to be present in the scenario.
        target_count (int): The number of targets to be present in the scenario.
        target_generator (Callable[[int, int], tuple[dict[int, int], dict[int, int]]]): A function that generates `action_sets` and
            `target_values` based on the `agent_count` and `target_count`.
        view (bool): Determines whether (True) or not (False) the `Scenario` will be viewed after creation.
    
    Returns:
        Scenario: the generated `Scenario`.
    """
    
    G = nx.DiGraph()
    G.add_nodes_from(range(1, agent_count + 1))
    
    possible_edges = [(u, v) for u in range(1, agent_count + 1) for v in range(u+1, agent_count + 1)]
    
    if edge_count > len(possible_edges):
        print("Too many edges requested for DAG of given size.")
        return None

    chosen_edges = random.sample(possible_edges, edge_count)
    G.add_edges_from(chosen_edges)
    action_sets, target_values = target_generator(agent_count, target_count)
    s = Scenario(G, action_sets, target_values)
    if view: visualize_scenario(s, "Scenario Visualization")
    return s

def pass_to_last(
    agent_count: int,
    target_count: int,
    target_generator: Callable[[int, int], tuple[dict[int, int], dict[int, int]]] = default_target_generator,
    view: bool = False
):
    """
    Generates a `Scenario` whose information sharing graph contains only edges connecting each agent to the final
    agent. The `action_sets` and `target_values` are provided by the given `target_generator` function.

    Args:
        agent_count (int): The number of agents to be present in the scenario.
        target_count (int): The number of targets to be present in the scenario.
        target_generator (Callable[[int, int], tuple[dict[int, int], dict[int, int]]]): A function that generates `action_sets` and
            `target_values` based on the `agent_count` and `target_count`.
        view (bool): Determines whether (True) or not (False) the `Scenario` will be viewed after creation.
    
    Returns:
        Scenario: the generated `Scenario`.
    """
    
    G = nx.DiGraph()
    G.add_edges_from([(u, agent_count) for u in range(1, agent_count)])
    action_sets, target_values = target_generator(agent_count, target_count)
    s = Scenario(G, action_sets, target_values)
    if view: visualize_scenario(s, "Scenario Visualization")
    return s

def pair_agents(
    agent_count: int,
    target_count: int,
    target_generator: Callable[[int, int], tuple[dict[int, int], dict[int, int]]] = default_target_generator,
    view: bool = False
):
    """
    Generates a `Scenario` whose information sharing graph contains an edge from every odd numbered agent to the following agent (if one exists) . The `action_sets` and `target_values` are provided by the given `target_generator` function.

    Args:
        agent_count (int): The number of agents to be present in the scenario.
        target_count (int): The number of targets to be present in the scenario.
        target_generator (Callable[[int, int], tuple[dict[int, int], dict[int, int]]]): A function that generates `action_sets` and
            `target_values` based on the `agent_count` and `target_count`.
        view (bool): Determines whether (True) or not (False) the `Scenario` will be viewed after creation.
    
    Returns:
        Scenario: the generated `Scenario`.
    """

    G = nx.DiGraph()
    G.add_nodes_from(range(1, agent_count + 1))
    G.add_edges_from([(u, u + 1) for u in range(1, agent_count, 2)])
    action_sets, target_values = target_generator(agent_count, target_count)
    s = Scenario(G, action_sets, target_values)
    if view: visualize_scenario(s, "Scenario Visualization")
    return s