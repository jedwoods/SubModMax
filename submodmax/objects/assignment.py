class Assignment:
    def __init__(
            self, 
            assignment: dict[int, int], 
            value: float = None, 
            efficiency: float = None,
            algorithm_used: str = None,
            rule_used: str = None
    ):
        self.assignment = assignment
        self.value = value
        self.efficiency = efficiency
        self.algorithm_used = algorithm_used
        self.rule_used = rule_used
    
    def set_value(self, value: float):
        self.value = value
    
    def set_efficiency(self, efficiency: float):
        self.efficiency = efficiency
    
    def set_algorithm_used(self, algorithm_title: str):
        self.algorithm_used = algorithm_title
    
    def set_rule_used(self, rule_title: str):
        self.rule_used = rule_title
    
    def get_value(self) -> float: return self.value
    def get_efficiency(self) -> float: return self.efficiency
    def get_algorithm_used(self) -> str: return self.algorithm_used
    def get_rule_used(self) -> str: return self.rule_used
    
    def get_assignment_pairs(self) -> list[tuple[int, int]]: return self.assignment.items()
    def get_choices(self) -> list[int]: return list(self.assignment.values())

    def __lt__(self, other: 'Assignment'):
        return self.get_value() < other.get_value()