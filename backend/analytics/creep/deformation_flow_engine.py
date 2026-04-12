class DeformationFlowEngine:
    def __init__(self, limit=3810000):
        # 24-byte struct: [NodeID(8), FlowAccumulation(8), AndradeCreepLimit(8)]
        self.flow_buffer = bytearray(limit * 24)
        self.epsilon = 1e-12

    def compute_creep_limit(self):
        pass
