import random

def default_target_generator(agent_count: int, target_count: int) -> tuple[dict[int, list[int]], dict[int, int]]:
    """
    Generates a set of action sets and target values to be used in a scenario.

    Args:
        agent_count (int): The number of agents in the scenario.
        target_count (int): The number of targets in the scenario.
    
    Returns:
        tuple: A tuple containing:
            - dict[int, list[int]]: A dictionary mapping agents to their corresponding action sets.
            - dict[int, int]: A dictionary mapping targets to their corresponding values. 
    """
    unreachable_targets = set(range(1, target_count + 1))
    action_sets = {}
    for agent in range(1, agent_count + 1):
       targets = random.sample(range(1, target_count + 1), 2)
       action_sets[agent] = targets
       unreachable_targets.difference_update(targets)
    for target in unreachable_targets:
        action_sets[random.randint(1, agent_count)].append(target)
    target_values = {target: random.randint(1, 5) for target in range(1, target_count + 1)}
    return action_sets, target_values