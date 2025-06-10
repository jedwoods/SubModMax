class Assignment:
    def __init__(self, assignment: dict[int, int], value: int = None, efficiency: float = None):
        self.assignment = assignment
        self.value = value
        self.efficiency = efficiency
    
    def set_value(self, value: int):
        self.value = value
    
    def set_efficiency(self, efficiency: float):
        self.efficiency = efficiency
    
    def get_value(self) -> int: return self.value if self.value else -1
    def get_efficiency(self) -> float: return self.efficiency if self.efficiency else -1.0
    def get_choices(self) -> list[int]: return list(self.assignment.values())

    def __lt__(self, other: 'Assignment'):
        return self.get_value() < other.get_value()