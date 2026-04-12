import heapq, struct, time
class BinaryPriorityQueue:
    def __init__(self):
        self._queue = []
        self._index = 0
    def push(self, priority: int, payload: bytes):
        heapq.heappush(self._queue, (priority, self._index, payload))
        self._index += 1
    def pop(self):
        return heapq.heappop(self._queue) if self._queue else None
