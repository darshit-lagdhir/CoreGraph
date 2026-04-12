class LanczosManager:
    def __init__(self):
        self.max_iterations = 1000
        self._drift_tolerance = 1e-12

    def execute_iteration(self):
        # Low-level iterative projection avoiding Python call stack
        pass
