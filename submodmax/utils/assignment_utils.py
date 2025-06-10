from submodmax.objects.assignment import Assignment

def score_assignment(assignment: Assignment, target_values: dict[int, int]) -> int:
    """
    Return the score of an assignment of agents to targets.

    Args:
        assignment (Assignment): An assignment object that maps agents to their chosen targets.
        target_values (dict[int, int]): A dictionary mapping targets to their values.
    
    Returns:
        int: The score of the assignment.
    """
    score = 0
    unique_choices = set(assignment.get_choices())
    for choice in unique_choices:
        score += target_values[choice]
    return score