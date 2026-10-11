"""
Custom array-backed binary heaps (MaxHeap & MinHeap) and top-k item selection.

Strategy: Array-backed binary tree with 0-indexed parent/child pointer arithmetic.
Time Complexity: push: O(log n), pop: O(log n), peek: O(1), top_k: O(n log k).
Space Complexity: O(n) for storing items.
Correctness: Maintains heap-order invariant recursively after every insertion (sift-up) and extraction (sift-down).
"""

from typing import List, Tuple, Any, Callable, TypeVar, Optional

T = TypeVar('T')

class MaxHeap:
    """
    Max-Heap storing (key, payload) tuples.
    Root always holds the element with the maximum key.
    """
    def __init__(self):
        self._heap: List[Tuple[Any, Any]] = []

    def __len__(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def peek(self) -> Tuple[Any, Any]:
        """
        Returns the top (key, payload) without removing it.
        Raises IndexError if empty.
        """
        if not self._heap:
            raise IndexError("peek from empty heap")
        return self._heap[0]

    def push(self, key: Any, payload: Any) -> None:
        """
        Pushes a new (key, payload) into the max-heap.
        Strategy: Append to array end and sift-up.
        Complexity: O(log n) time, O(1) space.
        Correctness: Sift-up swaps with parent until parent key >= item key.
        """
        self._heap.append((key, payload))
        self._sift_up(len(self._heap) - 1)

    def pop(self) -> Tuple[Any, Any]:
        """
        Pops and returns the maximum (key, payload) from the max-heap.
        Strategy: Swap root with last element, pop last element, sift-down root.
        Complexity: O(log n) time, O(1) space.
        Correctness: Sift-down swaps root with larger child until max-heap property is restored.
        """
        if not self._heap:
            raise IndexError("pop from empty heap")
        if len(self._heap) == 1:
            return self._heap.pop()
        
        root = self._heap[0]
        self._heap[0] = self._heap.pop()
        self._sift_down(0)
        return root

    def _sift_up(self, idx: int) -> None:
        while idx > 0:
            parent_idx = (idx - 1) // 2
            if self._heap[idx][0] > self._heap[parent_idx][0]:
                self._heap[idx], self._heap[parent_idx] = self._heap[parent_idx], self._heap[idx]
                idx = parent_idx
            else:
                break

    def _sift_down(self, idx: int) -> None:
        n = len(self._heap)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            largest = idx

            if left < n and self._heap[left][0] > self._heap[largest][0]:
                largest = left
            if right < n and self._heap[right][0] > self._heap[largest][0]:
                largest = right

            if largest != idx:
                self._heap[idx], self._heap[largest] = self._heap[largest], self._heap[idx]
                idx = largest
            else:
                break


class MinHeap:
    """
    Min-Heap storing (key, payload) tuples.
    Root always holds the element with the minimum key.
    """
    def __init__(self):
        self._heap: List[Tuple[Any, Any]] = []

    def __len__(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def peek(self) -> Tuple[Any, Any]:
        if not self._heap:
            raise IndexError("peek from empty heap")
        return self._heap[0]

    def push(self, key: Any, payload: Any) -> None:
        """
        Pushes a new (key, payload) into the min-heap.
        Strategy: Append to end and sift-up.
        Complexity: O(log n) time.
        Correctness: Maintains min-heap property parent key <= child key.
        """
        self._heap.append((key, payload))
        self._sift_up(len(self._heap) - 1)

    def pop(self) -> Tuple[Any, Any]:
        """
        Pops and returns the minimum (key, payload).
        Strategy: Swap root with last element and sift-down.
        Complexity: O(log n) time.
        Correctness: Restores min-heap property at each step.
        """
        if not self._heap:
            raise IndexError("pop from empty heap")
        if len(self._heap) == 1:
            return self._heap.pop()

        root = self._heap[0]
        self._heap[0] = self._heap.pop()
        self._sift_down(0)
        return root

    def _sift_up(self, idx: int) -> None:
        while idx > 0:
            parent_idx = (idx - 1) // 2
            if self._heap[idx][0] < self._heap[parent_idx][0]:
                self._heap[idx], self._heap[parent_idx] = self._heap[parent_idx], self._heap[idx]
                idx = parent_idx
            else:
                break

    def _sift_down(self, idx: int) -> None:
        n = len(self._heap)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            smallest = idx

            if left < n and self._heap[left][0] < self._heap[smallest][0]:
                smallest = left
            if right < n and self._heap[right][0] < self._heap[smallest][0]:
                smallest = right

            if smallest != idx:
                self._heap[idx], self._heap[smallest] = self._heap[smallest], self._heap[idx]
                idx = smallest
            else:
                break


def top_k(items: List[T], k: int, key: Callable[[T], Any]) -> List[T]:
    """
    Returns top-k items from items based on key function using a MinHeap of size k.
    
    Strategy: Bounded MinHeap of size k. Keep largest k elements seen so far.
    Time Complexity: O(n log k) where n is len(items).
    Space Complexity: O(k) for storing heap elements.
    Correctness: Any element larger than current min in heap replaces the min, keeping top-k elements.
    """
    if k <= 0 or not items:
        return []

    heap = MinHeap()
    for item in items:
        item_key = key(item)
        if len(heap) < k:
            heap.push(item_key, item)
        else:
            if item_key > heap.peek()[0]:
                heap.pop()
                heap.push(item_key, item)

    result = []
    while len(heap) > 0:
        result.append(heap.pop()[1])
    
    # Sort top-k result descending by key
    result.reverse()
    return result
