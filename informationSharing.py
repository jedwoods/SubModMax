UNKNOWN = 0
import networkx as nx
import random

def generalized_distributed_greedy_rule(G: nx.DiGraph, knowledge: dict[int, int], target_values: dict[int, int], current_agent: int) -> tuple[int, int]:
    """
    Returns the current agent and that agent's choice of target. This is the information sharing technique used
    in generalized distributed greedy algorithm.

    Args:
        knowledge (dict[int, int]): A dictionary representing the current agent's knowledge of the decisions made
            by other agents. Each key denotes an agent and its corresponding value is the current agent's knowledge of
            that agent's choice of target. A value of 0 (UNKNOWN) indicates that the current agent has no knowledge of that
            agent's choice of target.
        target_values (dict[int, int]): A dictionary mapping targets to their corresponding values.
        current_agent (int): The current agent being assessed.
    
    Returns:
        tuple: A tuple containing:
            - int: The current agent.
            - int: The target selected by the current agent. 
    """
    return current_agent, knowledge[current_agent]

def highest_marginal_contribution_rule(G: nx.DiGraph, knowledge: dict[int, int], target_values: dict[int, int], current_agent: int) -> tuple[int, int]:
    """
    Returns the agent (and that agent's choice of target) whose choice of target produced the largest marginal contribution
    to the overall score of the assignment, restricted to the knowledge of the current agent.

    Args:
        knowledge (dict[int, int]): A dictionary representing the current agent's knowledge of the decisions made
            by other agents. Each key denotes an agent and its corresponding value is the current agent's knowledge of
            that agent's choice of target. A value of 0 (UNKNOWN) indicates that the current agent has no knowledge of that
            agent's choice of target.
        target_values (dict[int, int]): A dictionary mapping targets to their corresponding values.
        current_agent (int): The current agent being assessed.
    
    Returns:
        tuple: A tuple containing:
            - int: The agent whose choice of target produces the largest marginal contribution to the assignment score based
            solely on the knowledge of the current node.
            - int: The target selected by chosen agent as described above.
    """
    agent_to_pass = current_agent
    agent_choice = knowledge[current_agent]
    agent_choice_contribution = target_values[agent_choice]
    for agent, choice in knowledge.items():
        if choice != UNKNOWN and target_values[choice] > agent_choice_contribution:
            agent_to_pass = agent
            agent_choice = choice
    return agent_to_pass, agent_choice


def most_upstream_agent_rule(G: nx.DiGraph, knowledge: dict[int, int], target_values: dict[int, int], current_agent: int) -> tuple[int, int]:
    """
    Passes information about the agent with the smallest index (most upstream) among those known.
    If there are ties, chooses the agent with the highest target value.
    """
    known_agents = [a for a, t in knowledge.items() if t != UNKNOWN]
    if not known_agents:
        return current_agent, knowledge[current_agent]
    # Find the smallest index (most upstream)
    upstream_agent = min(known_agents)
    # If multiple agents have the same smallest index, pick the one with the highest target value
    best_choice = knowledge[upstream_agent]
    for a in known_agents:
        if a == upstream_agent and target_values[knowledge[a]] > target_values[best_choice]:
            best_choice = knowledge[a]
    return upstream_agent, best_choice

def least_likely_known_rule(G: nx.DiGraph, knowledge: dict[int, int], target_values: dict[int, int], current_agent: int) -> tuple[int, int]:
    """
    Passes information about the agent whose decision is least likely to be known by the current agent's outgoing neighbors.
    If there are ties, chooses the agent with the highest target value.
    """
    known_agents = [a for a, t in knowledge.items() if t != UNKNOWN]
    if not known_agents:
        return current_agent, knowledge[current_agent]

    max_novelty = -1
    best_agent = current_agent
    best_choice = knowledge[current_agent]
    best_value = target_values[best_choice] if best_choice != UNKNOWN else -1

    for a in known_agents:
        novelty = 0
        for neighbor in G.successors(current_agent):
            # If 'a' is not an in-neighbor of 'neighbor', then neighbor is unlikely to know about 'a'
            if a not in G.predecessors(neighbor):
                novelty += 1
        # Prefer higher target value in case of tie
        if novelty > max_novelty or (novelty == max_novelty and target_values[knowledge[a]] > best_value):
            max_novelty = novelty
            best_agent = a
            best_choice = knowledge[a]
            best_value = target_values[best_choice]
    return best_agent, best_choice

def random_known_agent_rule(G: nx.DiGraph, knowledge: dict[int, int], target_values: dict[int, int], current_agent: int) -> tuple[int, int]:
    """
    Randomly selects one of the known agents and passes their decision.
    If no other agent is known, passes the current agent's own decision.
    """
    known_agents = [a for a, t in knowledge.items() if t != UNKNOWN]
    if not known_agents:
        return current_agent, knowledge[current_agent]
    chosen_agent = random.choice(known_agents)
    return chosen_agent, knowledge[chosen_agent]

def rotating_known_agent_rule(G: nx.DiGraph, knowledge: dict[int, int], target_values: dict[int, int], current_agent: int) -> tuple[int, int]:
    """
    Passes information about a known agent in round-robin order based on the current agent's index.
    If no other agent is known, passes the current agent's own decision.
    """
    known_agents = sorted([a for a, t in knowledge.items() if t != UNKNOWN])
    if not known_agents:
        return current_agent, knowledge[current_agent]
    # Use current_agent's index to pick which known agent to pass
    idx = (current_agent - 1) % len(known_agents)
    chosen_agent = known_agents[idx]
    return chosen_agent, knowledge[chosen_agent]

def degree_centrality_rule(G: nx.DiGraph, knowledge: dict[int, int], target_values: dict[int, int], current_agent: int) -> tuple[int, int]:
    """
    Passes information about the known agent with the highest degree centrality.
    If there are ties, chooses the agent with the highest target value.
    """
    # Compute centrality for all nodes (can use other centrality measures if desired)
    centrality = nx.degree_centrality(G)
    known_agents = [a for a, t in knowledge.items() if t != UNKNOWN]
    if not known_agents:
        return current_agent, knowledge[current_agent]

    # Find the known agent with the highest centrality (break ties with target value)
    best_agent = known_agents[0]
    best_choice = knowledge[best_agent]
    best_centrality = centrality[best_agent]
    best_value = target_values[best_choice]

    for a in known_agents:
        c = centrality[a]
        v = target_values[knowledge[a]]
        if c > best_centrality or (c == best_centrality and v > best_value):
            best_agent = a
            best_choice = knowledge[a]
            best_centrality = c
            best_value = v

    return best_agent, best_choice

def betweenness_centrality_rule(G: nx.DiGraph, knowledge: dict[int, int], target_values: dict[int, int], current_agent: int) -> tuple[int, int]:
    """
    Passes information about the known agent with the highest betweenness centrality.
    If there are ties, chooses the agent with the highest target value.
    """
    # Compute centrality for all nodes (can use other centrality measures if desired)
    centrality = nx.betweenness_centrality(G)
    known_agents = [a for a, t in knowledge.items() if t != UNKNOWN]
    if not known_agents:
        return current_agent, knowledge[current_agent]

    # Find the known agent with the highest centrality (break ties with target value)
    best_agent = known_agents[0]
    best_choice = knowledge[best_agent]
    best_centrality = centrality[best_agent]
    best_value = target_values[best_choice]

    for a in known_agents:
        c = centrality[a]
        v = target_values[knowledge[a]]
        if c > best_centrality or (c == best_centrality and v > best_value):
            best_agent = a
            best_choice = knowledge[a]
            best_centrality = c
            best_value = v

    return best_agent, best_choice

def closeness_centrality_rule(G: nx.DiGraph, knowledge: dict[int, int], target_values: dict[int, int], current_agent: int) -> tuple[int, int]:
    """
    Passes information about the known agent with the highest closeness centrality.
    If there are ties, chooses the agent with the highest target value.
    """
    # Compute centrality for all nodes (can use other centrality measures if desired)
    centrality = nx.closeness_centrality(G)
    known_agents = [a for a, t in knowledge.items() if t != UNKNOWN]
    if not known_agents:
        return current_agent, knowledge[current_agent]

    # Find the known agent with the highest centrality (break ties with target value)
    best_agent = known_agents[0]
    best_choice = knowledge[best_agent]
    best_centrality = centrality[best_agent]
    best_value = target_values[best_choice]

    for a in known_agents:
        c = centrality[a]
        v = target_values[knowledge[a]]
        if c > best_centrality or (c == best_centrality and v > best_value):
            best_agent = a
            best_choice = knowledge[a]
            best_centrality = c
            best_value = v

    return best_agent, best_choice

