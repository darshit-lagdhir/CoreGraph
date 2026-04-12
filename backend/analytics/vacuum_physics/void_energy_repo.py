class VoidEnergyRepository:
    def __init__(self, node_limit: int):
        self.node_limit = node_limit
        self._zero_point_matrix = bytearray(node_limit * 8)

    def assert_zero_drift(self) -> bool:
        # Guarantee no deviation in the baseline vacuum state un-commanded
        return self._zero_point_matrix[0] == 0
