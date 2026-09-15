"""
GridGuard Min-Heap / Priority Queue Data Structure
Custom wrapper around Python's heapq for priority queue operations in Dijkstra.
"""

import heapq
from typing import Any, Tuple, Optional, List


class MinHeap:
    """
    Min-Heap Priority Queue for graph algorithms.
    Stores tuples of (priority, item) or (priority, tie_breaker, item)
    and ensures O(log N) insertion and extraction.
    """
    def __init__(self):
        self._heap: List[Tuple[float, int, Any]] = []
        self._counter: int = 0  # Tie-breaker for items with equal priority

    def push(self, priority: float, item: Any) -> None:
        """
        Pushes an item with given priority into the Min-Heap.
        Complexity: O(log N)
        """
        self._counter += 1
        heapq.heappush(self._heap, (priority, self._counter, item))

    def pop(self) -> Tuple[float, Any]:
        """
        Extracts and returns the item with the minimum priority.
        Complexity: O(log N)
        """
        if not self._heap:
            raise IndexError("pop from empty MinHeap")
        priority, _, item = heapq.heappop(self._heap)
        return priority, item

    def peek(self) -> Optional[Tuple[float, Any]]:
        """Returns minimum priority element without removing it."""
        if not self._heap:
            return None
        priority, _, item = self._heap[0]
        return priority, item

    def is_empty(self) -> bool:
        """Returns True if the heap contains no elements."""
        return len(self._heap) == 0

    def size(self) -> int:
        """Returns the number of elements in the heap."""
        return len(self._heap)

    def __len__(self) -> int:
        return len(self._heap)

    def __repr__(self) -> str:
        return f"MinHeap(size={len(self._heap)})"
