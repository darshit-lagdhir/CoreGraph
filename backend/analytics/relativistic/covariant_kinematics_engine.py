class CovariantKinematicsEngine:
    def __init__(self, limit=3810000):
        # 24-byte struct: [NodeID(8), ProperTime(8), LorentzFactor(8)]
        self.kinematic_buffer = bytearray(limit * 24)
        self.epsilon = 1e-12

    def compute_world_line_kinematics(self):
        pass
