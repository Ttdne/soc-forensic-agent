class PlanningState:
    def __init__(self, max_depth: int = 3):
        self.current_depth = 0
        self.steps = []
        self.max_depth = max_depth

    def increment_depth(self):
        self.current_depth += 1

    def is_max_depth(self):
        return self.current_depth >= self.max_depth

    def add_step(self, agent_name: str, input_data: dict, output_data: dict):
        self.steps.append({
            "depth": self.current_depth,
            "agent": agent_name,
            "input": input_data,
            "output": output_data,
        })

    def get_trace(self):
        return self.steps
