from typing import Callable, Any
from submodmax.objects.scenario import Scenario
from submodmax.objects.assignment import Assignment
from submodmax.utils.assignment_utils import score_assignment
UNKNOWN = 0
 
def distributed_greedy(scenario: Scenario) -> Assignment:
    """
    Returns an assignment of agents to targets for the provided scenario detemined by the distributed
    greedy algorithm, in which each agent has a knowledge of the decision of the agents before it.

    Args:
        scenario (Scenario): The scenario to be assessed.
    
    Returns:
        Assignment: An assignment object.
    """
    action_sets = scenario.get_action_set()
    target_values = scenario.get_target_values()

    functional_target_values = target_values.copy()
    agent_count = len(action_sets)
    assignment = {}
    assignment_val = 0

    for agent in range(1, agent_count + 1):
        best_option = None
        bo_val = -1
        for option in action_sets[agent]:
            if functional_target_values[option] > bo_val:
                best_option = option
                bo_val = functional_target_values[option]
        assignment[agent] = best_option
        assignment_val += bo_val
        functional_target_values[best_option] = 0
    return Assignment(assignment, assignment_val)

def greedy_with_information_sharing_rule(
        scenario: Scenario,
        rule: Callable[[Any, dict[int, int], dict[int, int], int], tuple[int, int]]
) -> Assignment:
    """
    Returns an assignment of agents to targets for the provided scenario detemined by an information sharing rule paired with a
    greedy algorithm, in which each agent has access to the information shared by the agents before it according to a graph structure.

    Args:
        scenario (Scenario): The scenario to be assessed.
        rule (Callable): A function that defines the information that each agent shares with its neighbors.
    
    Returns:
        Assignment: An assignment object.
    """
    
    G = scenario.G
    action_sets = scenario.action_sets
    target_values = scenario.target_values

    agent_count = len(G)
    knowledge_dict = {agent: {a: UNKNOWN for a in range(1, agent_count + 1)} for agent in range(1, agent_count + 1)}
    assignment = {}
    
    for agent in range(1, agent_count + 1):
        # Greedy selection based on limited information available to agent
        best_option = action_sets[agent][0]
        bo_val = 0
        for target_option in action_sets[agent]:
            if target_option not in knowledge_dict[agent].values() and target_values[target_option] > bo_val:  # adjust data structures to avoid linear search of knowledge_dict values?
                best_option = target_option
                bo_val = target_values[target_option]
        assignment[agent] = best_option
        knowledge_dict[agent][agent] = best_option
        
        # Pass information based on rule
        agent_passed, agent_passed_choice = rule(G, knowledge_dict[agent], target_values, agent)
        for neighbor in G.successors(agent):
            knowledge_dict[neighbor][agent_passed] = agent_passed_choice
    
    assignmnet = Assignment(assignment)
    score = score_assignment(assignmnet, target_values)
    return Assignment(assignment, score)