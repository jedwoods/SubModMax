from typing import Callable, Any
from submodmax.objects.scenario import Scenario
from submodmax.objects.assignment import Assignment
from submodmax.utils.assignment_utils import score_assignment
from submodmax.information_sharing_rules import RULE_NAMES

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
    choices = {}
    assignment_val = 0
    optimal_val = scenario.get_optimal_value()

    for agent in range(1, agent_count + 1):
        best_option = None
        bo_val = -1
        for option in action_sets[agent]:
            if functional_target_values[option] > bo_val:
                best_option = option
                bo_val = functional_target_values[option]
        choices[agent] = best_option
        assignment_val += bo_val
        functional_target_values[best_option] = 0
    
    eff = assignment_val / optimal_val if optimal_val != 0 else 1.0
    return Assignment(choices, assignment_val, eff, "Distributed Greedy", None)

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
    
    G = scenario.get_graph_copy()
    action_sets = scenario.get_action_set()
    target_values = scenario.get_target_values()
    optimal_value = scenario.get_optimal_value()

    agent_count = len(G)
    knowledge_dict = {agent: {a: UNKNOWN for a in range(1, agent_count + 1)} for agent in range(1, agent_count + 1)}
    choices = {}
    for agent in range(1, agent_count + 1):
        # Greedy selection based on limited information available to agent
        best_option = action_sets[agent][0] if action_sets[agent] else None
        bo_val = 0
        for target_option in action_sets[agent]:
            if target_option not in knowledge_dict[agent].values() and target_values[target_option] > bo_val: 
                best_option = target_option
                bo_val = target_values[target_option]
        choices[agent] = best_option
        knowledge_dict[agent][agent] = best_option
        
        # Pass information based on rule
        agent_passed, agent_passed_choice = rule(G, knowledge_dict[agent], target_values, agent)
        for neighbor in G.successors(agent):
            knowledge_dict[neighbor][agent_passed] = agent_passed_choice
    
    assignment = Assignment(choices, algorithm_used="Greedy with Info Sharing")
    score = score_assignment(assignment, target_values)
    assignment.set_value(score)
    assignment.set_efficiency(score / optimal_value if optimal_value != 0 else 1.0)
    assignment.set_rule_used(RULE_NAMES[rule])
    return assignment