class ConsenusReconciler:
    def __init__(self):
        self.last_seq = -1
    def verify(self, seq: int):
        if seq <= self.last_seq:
            raise ValueError('StateDivergence')
        self.last_seq = seq
        return True
