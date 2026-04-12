class BinaryAnomalyDetector:
    def __init__(self, threshold: float = 4.0):
        self.threshold = threshold
    def detect(self, entropy_val: float) -> bool:
        return entropy_val > self.threshold
