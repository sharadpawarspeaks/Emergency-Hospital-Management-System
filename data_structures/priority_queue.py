"""
Custom Priority Queue Implementation using a Binary Min-Heap.
Triage priority is primary criterion; arrival sequence is secondary criterion (FIFO tie-breaker).
"""

from typing import List, Optional, Tuple
from models.patient import Patient


class PriorityPatientQueue:
    """
    Genuine Binary Min-Heap Priority Queue.
    
    Triage Rules:
    - Primary Key: Priority Level (1 = Critical Emergency, 2 = High Priority, 3 = Normal)
      Lower numerical value represents higher emergency triage urgency.
    - Secondary Key: Arrival Sequence Number (1, 2, 3...)
      Preserves strict FIFO ordering among patients with identical triage priority.

    Time Complexities:
    - Insertion (push): O(log n)
    - Extraction of highest priority (pop): O(log n)
    - Peek at next patient: O(1)
    - Size check / Is empty: O(1)
    - Removal by ID: O(n) search + O(log n) reheapify
    """

    def __init__(self):
        # Heap elements are tuples: (priority, arrival_sequence, patient)
        self._heap: List[Tuple[int, int, Patient]] = []

    def _parent(self, index: int) -> int:
        return (index - 1) // 2

    def _left_child(self, index: int) -> int:
        return 2 * index + 1

    def _right_child(self, index: int) -> int:
        return 2 * index + 2

    def _compare(self, a: Tuple[int, int, Patient], b: Tuple[int, int, Patient]) -> bool:
        """Returns True if item 'a' has higher priority (smaller key) than item 'b'."""
        # Primary: priority (1 < 2 < 3)
        if a[0] != b[0]:
            return a[0] < b[0]
        # Secondary: arrival sequence (earlier arrival seq < later arrival seq)
        return a[1] < b[1]

    def _sift_up(self, index: int) -> None:
        """Restores min-heap property upward from index."""
        while index > 0:
            parent_idx = self._parent(index)
            if self._compare(self._heap[index], self._heap[parent_idx]):
                # Swap child and parent
                self._heap[index], self._heap[parent_idx] = self._heap[parent_idx], self._heap[index]
                index = parent_idx
            else:
                break

    def _sift_down(self, index: int) -> None:
        """Restores min-heap property downward from index."""
        heap_len = len(self._heap)
        while True:
            smallest = index
            left = self._left_child(index)
            right = self._right_child(index)

            if left < heap_len and self._compare(self._heap[left], self._heap[smallest]):
                smallest = left

            if right < heap_len and self._compare(self._heap[right], self._heap[smallest]):
                smallest = right

            if smallest != index:
                self._heap[index], self._heap[smallest] = self._heap[smallest], self._heap[index]
                index = smallest
            else:
                break

    def insert(self, patient: Patient) -> None:
        """
        Inserts a patient into the priority queue.
        Time Complexity: O(log n)
        """
        item = (patient.priority, patient.arrival_sequence, patient)
        self._heap.append(item)
        self._sift_up(len(self._heap) - 1)

    def pop_highest_priority(self) -> Optional[Patient]:
        """
        Extracts and returns the patient with the highest emergency priority.
        If priority is tied, extracts the one who arrived first (FIFO).
        Time Complexity: O(log n)
        """
        if self.is_empty():
            return None

        highest = self._heap[0][2]
        last_item = self._heap.pop()

        if self._heap:
            self._heap[0] = last_item
            self._sift_down(0)

        return highest

    def peek(self) -> Optional[Patient]:
        """
        Inspects the highest priority patient without removing them.
        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        return self._heap[0][2]

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def size(self) -> int:
        return len(self._heap)

    def remove_by_id(self, patient_id: str) -> bool:
        """
        Removes a patient from the queue by ID.
        Time Complexity: O(n) search + O(log n) heap restoration.
        """
        clean_id = patient_id.strip().upper()
        target_idx = -1
        for i, item in enumerate(self._heap):
            if item[2].patient_id.upper() == clean_id:
                target_idx = i
                break

        if target_idx == -1:
            return False

        last_item = self._heap.pop()
        if target_idx < len(self._heap):
            self._heap[target_idx] = last_item
            self._sift_down(target_idx)
            self._sift_up(target_idx)

        return True

    def get_all_ordered(self) -> List[Patient]:
        """
        Returns a list of all queued patients in exact triage order without mutating the heap.
        Preserves original heap structure by sorting an internal copy.
        """
        # Sort based on primary (priority) and secondary (arrival_sequence)
        sorted_items = sorted(self._heap, key=lambda x: (x[0], x[1]))
        return [item[2] for item in sorted_items]

    def clear(self) -> None:
        self._heap.clear()

    def to_heap_array_visualization(self) -> str:
        """
        Returns a visual representation of the internal binary heap array.
        """
        if not self._heap:
            return "Heap Array: [] (Empty Queue)"
        items_str = ", ".join(
            f"[{i}]: {item[2].patient_id}(P{item[0]}, seq={item[1]})"
            for i, item in enumerate(self._heap)
        )
        return f"Heap Array ({len(self._heap)} elements): {items_str}"
