class Assignment:
    def __init__(self, assignment: dict[int, int], value: int = None, efficiency: float = None):
        self.assignment = assignment
        self.value = value
        self.efficiency = efficiency
    
    def set_value(self, value: int):
        self.value = value
    
    def set_efficiency(self, efficiency: float):
        self.efficiency = efficiency
    
    def get_value(self) -> int: return self.value if self.value != None else -1
    def get_efficiency(self) -> float: return self.efficiency if self.efficiency != None else -1.0
    def get_assignment_pairs(self) -> list[tuple[int, int]]: return self.assignment.items()
    def get_choices(self) -> list[int]: return list(self.assignment.values())

    def __lt__(self, other: 'Assignment'):
        return self.get_value() < other.get_value()