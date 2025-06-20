import networkx as nx
import random
UNKNOWN = 0

def generalized_distributed_greedy_rule(
    G: nx.DiGraph, 
    knowledge: dict[int, int], 
    target_values: dict[int, int], 
    current_agent: int
) -> tuple[int, int]:
    """
    An information sharing rule that returns the current agent and that agent's choice of target. This is the information sharing technique used
    in the generalized distributed greedy algorithm.

    Args:
        G (nx.Digraph): The directed graph representing which agents share information with which other agents.
        knowledge (dict[int, int]): A dictionary representing the current agent's knowledge of the decisions made
            by other agents. Each key denotes an agent and its corresponding value is the current agent's knowledge of
            that agent's choice of target. A value of 0 (UNKNOWN) indicates that the current agent has no knowledge of that
            agent's choice of target.
        target_values (dict[int, int]): A dictionary mapping targets to their corresponding values.
        current_agent (int): The current agent being assessed.
    
    Returns:
        tuple[int, int]: a pair where the first element is the agent to be shared and the second element 
            is that agent's choice of target.
    """
    return current_agent, knowledge[current_agent]

def highest_marginal_contribution_rule(
    G: nx.DiGraph, 
    knowledge: dict[int, int], 
    target_values: dict[int, int], 
    current_agent: int
) -> tuple[int, int]:
    """
    An information sharing rule that returns the (agent, choice of target) pair that produces the largest marginal contribution to
    the overall score of an assignment, restricted to the knowledge of the current agent.

    Args:
        G (nx.Digraph): The directed graph representing which agents share information with which other agents.
        knowledge (dict[int, int]): A dictionary representing the current agent's knowledge of the decisions made
            by other agents. Each key denotes an agent and its corresponding value is the current agent's knowledge of
            that agent's choice of target. A value of 0 (UNKNOWN) indicates that the current agent has no knowledge of that
            agent's choice of target.
        target_values (dict[int, int]): A dictionary mapping targets to their corresponding values.
        current_agent (int): The current agent being assessed.
    
    Returns:
        tuple[int, int]: a pair where the first element is the agent to be shared and the second element 
            is that agent's choice of target.
    """
    agent_to_pass = current_agent
    agent_choice = knowledge[current_agent]
    agent_choice_contribution = target_values[agent_choice] if agent_choice else 0.0
    for agent, choice in knowledge.items():
        if choice != UNKNOWN and choice != None and target_values[choice] > agent_choice_contribution:
            agent_to_pass = agent
            agent_choice = choice
            agent_choice_contribution = target_values[choice]
    return agent_to_pass, agent_choice


def most_upstream_agent_rule(
    G: nx.DiGraph, 
    knowledge: dict[int, int], 
    target_values: dict[int, int], 
    current_agent: int
) -> tuple[int, int]:
    """
    An information sharing rule that returns the (agent, choice of target) pair corresponding to the most upstream agent
    that is known to the current agent. This is the agent (amongst those known) with the smallest index. If there are 
    ties, the pair with the highest target value is chosen.

    Args:
        G (nx.Digraph): The directed graph representing which agents share information with which other agents.
        knowledge (dict[int, int]): A dictionary representing the current agent's knowledge of the decisions made
            by other agents. Each key denotes an agent and its corresponding value is the current agent's knowledge of
            that agent's choice of target. A value of 0 (UNKNOWN) indicates that the current agent has no knowledge of that
            agent's choice of target.
        target_values (dict[int, int]): A dictionary mapping targets to their corresponding values.
        current_agent (int): The current agent being assessed.
    
    Returns:
        tuple[int, int]: a pair where the first element is the agent to be shared and the second element 
            is that agent's choice of target.
    """
    known_agents = [a for a, t in knowledge.items() if t != UNKNOWN]
    if not known_agents:
        return current_agent, knowledge[current_agent]
    # Find the smallest index (most upstream)
    upstream_agent = min(known_agents)
    # If multiple agents have the same smallest index, pick the one with the highest target value
    best_choice = knowledge[upstream_agent]
    for a in known_agents:
        if a == upstream_agent and knowledge[a] and target_values[knowledge[a]] > target_values[best_choice]:
            best_choice = knowledge[a]
    return upstream_agent, best_choice

def least_likely_known_amongst_neighborhood_rule(
    G: nx.DiGraph, 
    knowledge: dict[int, int], 
    target_values: dict[int, int], 
    current_agent: int
) -> tuple[int, int]:
    """
    An information sharing rule that returns the (agent, choice of target) pair that the current agent's neighbors are least 
    likely to know about. If there are ties, the pair with the highest target value is chosen.

    Args:
        G (nx.Digraph): The directed graph representing which agents share information with which other agents.
        knowledge (dict[int, int]): A dictionary representing the current agent's knowledge of the decisions made
            by other agents. Each key denotes an agent and its corresponding value is the current agent's knowledge of
            that agent's choice of target. A value of 0 (UNKNOWN) indicates that the current agent has no knowledge of that
            agent's choice of target.
        target_values (dict[int, int]): A dictionary mapping targets to their corresponding values.
        current_agent (int): The current agent being assessed.
    
    Returns:
        tuple[int, int]: a pair where the first element is the agent to be shared and the second element 
            is that agent's choice of target.
    """
    known_agents = [a for a, t in knowledge.items() if t != UNKNOWN]
    if not known_agents:
        return current_agent, knowledge[current_agent]

    max_novelty = -1
    best_agent = current_agent
    best_choice = knowledge[current_agent]
    best_value = target_values[best_choice] if best_choice else 0

    for a in known_agents:
        novelty = 0
        for neighbor in G.successors(current_agent):
            # If 'a' is not an in-neighbor of 'neighbor', then neighbor is unlikely to know about 'a'
            if a not in G.predecessors(neighbor):
                novelty += 1
        # Prefer higher target value in case of tie
        if novelty > max_novelty or (novelty == max_novelty and knowledge[a] and target_values[knowledge[a]] > best_value):
            max_novelty = novelty
            best_agent = a
            best_choice = knowledge[a]
            best_value = target_values[best_choice] if best_choice else 0
    return best_agent, best_choice

def random_known_agent_rule(
    G: nx.DiGraph, 
    knowledge: dict[int, int], 
    target_values: dict[int, int], 
    current_agent: int
) -> tuple[int, int]:
    """
    An information sharing rule that randomly selects an agent whose decision is known to the current agent and returns the
    corresponding (agent, decision) pair. If the current agent has no knowledge of any other agents' decisions, its 
    own decision is returned.

    Args:
        G (nx.Digraph): The directed graph representing which agents share information with which other agents.
        knowledge (dict[int, int]): A dictionary representing the current agent's knowledge of the decisions made
            by other agents. Each key denotes an agent and its corresponding value is the current agent's knowledge of
            that agent's choice of target. A value of 0 (UNKNOWN) indicates that the current agent has no knowledge of that
            agent's choice of target.
        target_values (dict[int, int]): A dictionary mapping targets to their corresponding values.
        current_agent (int): The current agent being assessed.
    
    Returns:
        tuple[int, int]: a pair where the first element is the agent to be shared and the second element 
            is that agent's choice of target.
    """
    known_agents = [a for a, t in knowledge.items() if t != UNKNOWN]
    if not known_agents:
        return current_agent, knowledge[current_agent]
    chosen_agent = random.choice(known_agents)
    return chosen_agent, knowledge[chosen_agent]

def degree_centrality_rule(
    G: nx.DiGraph, 
    knowledge: dict[int, int], 
    target_values: dict[int, int], 
    current_agent: int
) -> tuple[int, int]:
    """
    An information sharing rule that returns the (agent, choice of target) pair corresponding to the known agent with the 
    highest degree centrality. If there are ties, the pair with the highest target value is chosen.

    Args:
        G (nx.Digraph): The directed graph representing which agents share information with which other agents.
        knowledge (dict[int, int]): A dictionary representing the current agent's knowledge of the decisions made
            by other agents. Each key denotes an agent and its corresponding value is the current agent's knowledge of
            that agent's choice of target. A value of 0 (UNKNOWN) indicates that the current agent has no knowledge of that
            agent's choice of target.
        target_values (dict[int, int]): A dictionary mapping targets to their corresponding values.
        current_agent (int): The current agent being assessed.
    
    Returns:
        tuple[int, int]: a pair where the first element is the agent to be shared and the second element 
            is that agent's choice of target.
    """
    # Compute centrality for all nodes
    centrality = nx.degree_centrality(G)
    known_agents = [a for a, t in knowledge.items() if t != UNKNOWN]
    if not known_agents:
        return current_agent, knowledge[current_agent]

    # Find the known agent with the highest centrality (break ties with target value)
    best_agent = known_agents[0]
    best_choice = knowledge[best_agent]
    best_centrality = centrality[best_agent]
    best_value = target_values[best_choice] if best_choice else 0

    for a in known_agents:
        c = centrality[a]
        v = target_values[knowledge[a]] if knowledge[a] else 0
        if c > best_centrality or (c == best_centrality and v > best_value):
            best_agent = a
            best_choice = knowledge[a]
            best_centrality = c
            best_value = v

    return best_agent, best_choice

def betweenness_centrality_rule(
    G: nx.DiGraph, 
    knowledge: dict[int, int], 
    target_values: dict[int, int], 
    current_agent: int
) -> tuple[int, int]:
    """
    An information sharing rule that returns the (agent, choice of target) pair corresponding to the known agent with the 
    highest betweeness centrality. If there are ties, the pair with the highest target value is chosen.

    Args:
        G (nx.Digraph): The directed graph representing which agents share information with which other agents.
        knowledge (dict[int, int]): A dictionary representing the current agent's knowledge of the decisions made
            by other agents. Each key denotes an agent and its corresponding value is the current agent's knowledge of
            that agent's choice of target. A value of 0 (UNKNOWN) indicates that the current agent has no knowledge of that
            agent's choice of target.
        target_values (dict[int, int]): A dictionary mapping targets to their corresponding values.
        current_agent (int): The current agent being assessed.
    
    Returns:
        tuple[int, int]: a pair where the first element is the agent to be shared and the second element 
            is that agent's choice of target.
    """
    # Compute centrality for all nodes
    centrality = nx.betweenness_centrality(G)
    known_agents = [a for a, t in knowledge.items() if t != UNKNOWN]
    if not known_agents:
        return current_agent, knowledge[current_agent]

    # Find the known agent with the highest centrality (break ties with target value)
    best_agent = known_agents[0]
    best_choice = knowledge[best_agent]
    best_centrality = centrality[best_agent]
    best_value = target_values[best_choice] if best_choice else 0

    for a in known_agents:
        c = centrality[a]
        v = target_values[knowledge[a]] if knowledge[a] else 0
        if c > best_centrality or (c == best_centrality and v > best_value):
            best_agent = a
            best_choice = knowledge[a]
            best_centrality = c
            best_value = v

    return best_agent, best_choice

def closeness_centrality_rule(
    G: nx.DiGraph, 
    knowledge: dict[int, int], 
    target_values: dict[int, int], 
    current_agent: int
) -> tuple[int, int]:
    """
    An information sharing rule that returns the (agent, choice of target) pair corresponding to the known agent with the 
    highest closeness centrality. If there are ties, the pair with the highest target value is chosen.

    Args:
        G (nx.Digraph): The directed graph representing which agents share information with which other agents.
        knowledge (dict[int, int]): A dictionary representing the current agent's knowledge of the decisions made
            by other agents. Each key denotes an agent and its corresponding value is the current agent's knowledge of
            that agent's choice of target. A value of 0 (UNKNOWN) indicates that the current agent has no knowledge of that
            agent's choice of target.
        target_values (dict[int, int]): A dictionary mapping targets to their corresponding values.
        current_agent (int): The current agent being assessed.
    
    Returns:
        tuple[int, int]: a pair where the first element is the agent to be shared and the second element 
            is that agent's choice of target.
    """
    # Compute centrality for all nodes
    centrality = nx.closeness_centrality(G)
    known_agents = [a for a, t in knowledge.items() if t != UNKNOWN]
    if not known_agents:
        return current_agent, knowledge[current_agent]

    # Find the known agent with the highest centrality (break ties with target value)
    best_agent = known_agents[0]
    best_choice = knowledge[best_agent]
    best_centrality = centrality[best_agent]
    best_value = target_values[best_choice] if best_choice else 0

    for a in known_agents:
        c = centrality[a]
        v = target_values[knowledge[a]] if knowledge[a] else 0
        if c > best_centrality or (c == best_centrality and v > best_value):
            best_agent = a
            best_choice = knowledge[a]
            best_centrality = c
            best_value = v

    return best_agent, best_choice

def maximize_downstream_reach(
    G: nx.DiGraph,
    knowledge: dict[int, int],
    target_values: dict[int, int],
    current_agent: int
) -> tuple[int, int]:
    """
    An information sharing rule that returns the (agent, choice of target) pair amongst the current agent's knowledge that maximizes the downstream 
    reach of the source agent.

    Args:
        G (nx.Digraph): The directed graph representing which agents share information with which other agents.
        knowledge (dict[int, int]): A dictionary representing the current agent's knowledge of the decisions made
            by other agents. Each key denotes an agent and its corresponding value is the current agent's knowledge of
            that agent's choice of target. A value of 0 (UNKNOWN) indicates that the current agent has no knowledge of that
            agent's choice of target.
        target_values (dict[int, int]): A dictionary mapping targets to their corresponding values.
        current_agent (int): The current agent being assessed.
    
    Returns:
        tuple[int, int]: a pair where the first element is the agent to be shared and the second element 
            is that agent's choice of target.
    """

    # Extract known decisions (agent -> target) where target ≠ 0
    known_decisions = [(agent, target) for agent, target in knowledge.items() if target != 0]

    if not known_decisions:
        return (-1, -1)  # No decision to share

    # Select the (agent, target) pair whose source agent has max downstream reach
    best_decision = None
    max_reach = -1

    for agent, target in known_decisions:
        reach = len(nx.descendants(G, agent))
        if reach > max_reach:
            max_reach = reach
            best_decision = (agent, target)

    return best_decision if best_decision else (-1, -1)

def reach_and_value_rule(
    info_graph: nx.DiGraph,
    knowledge: dict[int, int],
    target_values: dict[int, int],
    current_agent: int
) -> tuple[int, int]:
    """
    An information sharing rule that returns the (agent, choice of target) pair that maximizes the product of the agent's reach and
    value of the corresponding choice of target (within the knowledge of the current agent).

    Args:
        G (nx.Digraph): The directed graph representing which agents share information with which other agents.
        knowledge (dict[int, int]): A dictionary representing the current agent's knowledge of the decisions made
            by other agents. Each key denotes an agent and its corresponding value is the current agent's knowledge of
            that agent's choice of target. A value of 0 (UNKNOWN) indicates that the current agent has no knowledge of that
            agent's choice of target.
        target_values (dict[int, int]): A dictionary mapping targets to their corresponding values.
        current_agent (int): The current agent being assessed.
    
    Returns:
        tuple[int, int]: a pair where the first element is the agent to be shared and the second element 
            is that agent's choice of target.
    """

    # Filter for known agent decisions
    known_decisions = [(agent, target) for agent, target in knowledge.items() if target != 0]
    if not known_decisions:
        return (-1, -1)

    best_score = -1
    best_decision = (-1, -1)

    for agent, target in known_decisions:
        value = target_values.get(target, 0)
        reach = len(nx.descendants(info_graph, agent))  # How many agents that agent can reach
        score = value * reach

        if score > best_score:
            best_score = score
            best_decision = (agent, target)

    return best_decision if best_decision != (-1, -1) else known_decisions[0]

def adaptive_sharing_rule(
    G: nx.DiGraph,
    knowledge: dict[int, int],
    target_values: dict[int, int],
    current_agent: int
) -> tuple[int, int]:
    num_known = sum(1 for t in knowledge.values() if t != 0)
    num_agents = G.number_of_nodes()
    progress = num_known / num_agents

    if progress < 0.3:
        # Early: propagate high-value or high-centrality agents
        return degree_centrality_rule(G, knowledge, target_values, current_agent)
    elif progress < 0.7:
        # Mid: strategic spreading to maximize novelty or reach
        return least_likely_known_amongst_neighborhood_rule(G, knowledge, target_values, current_agent)
    else:
        # Late: fallback to marginal contribution or greedy coverage
        return highest_marginal_contribution_rule(G, knowledge, target_values, current_agent)

RULE_NAMES = {
    generalized_distributed_greedy_rule: "Generalized Distributed",
    highest_marginal_contribution_rule: "Highest Marginal Contribution",
    most_upstream_agent_rule: "Most Upstream Agent",
    least_likely_known_amongst_neighborhood_rule: "Least Likely Known",
    random_known_agent_rule: "Random",
    degree_centrality_rule: "Degree Centrality",
    betweenness_centrality_rule: "Betweenness Centrality",
    closeness_centrality_rule: "Closeness Centrality",
    maximize_downstream_reach: "Maximize Downstream Reach",
    reach_and_value_rule: "Reach and Value",
    adaptive_sharing_rule: "Adaptive Sharing"
}