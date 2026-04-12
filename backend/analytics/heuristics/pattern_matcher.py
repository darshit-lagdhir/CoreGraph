from backend.analytics.graph.isomorphism_kernel import IsomorphismKernel


class PatternMatcher:
    def __init__(self, capacity=100000):
        self.kernel = IsomorphismKernel(max_depth=capacity)

    def execute_match(self, target_nodes, query_nodes):
        self.kernel.sp = 0
        self.kernel.push(0, 0, 0, 0)
        matches = 0
        while True:
            frame = self.kernel.pop()
            if not frame:
                break
            depth, q, t, state = frame
            if depth == query_nodes:
                matches += 1
                continue
            if t < target_nodes:
                self.kernel.push(depth, q, t + 1, 0)
                self.kernel.push(depth + 1, q + 1, t, 1)
        return matches
