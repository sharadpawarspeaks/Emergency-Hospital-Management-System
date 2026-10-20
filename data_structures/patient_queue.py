"""
Custom FIFO Queue Implementation for Hospital Emergency Management.
Demonstrates standard First-In, First-Out queue using pointer-linked nodes.
"""

from typing import Optional, List
from models.patient import Patient


class QueueNode:
    """Node representing an element in the FIFO Queue."""
    def __init__(self, patient: Patient):
        self.patient = patient
        self.next: Optional["QueueNode"] = None


class PatientQueue:
    """
    Pointer-linked First-In First-Out (FIFO) Queue.
    Used for maintaining arrival order among patients with identical priority.
    
    Time Complexities:
    - Enqueue: O(1)
    - Dequeue: O(1)
    - Peek: O(1)
    - Size: O(1)
    """

    def __init__(self):
        self.front: Optional[QueueNode] = None
        self.rear: Optional[QueueNode] = None
        self._size: int = 0

    def enqueue(self, patient: Patient) -> None:
        """Adds a patient to the rear of the queue in O(1) time."""
        new_node = QueueNode(patient)
        if self.rear is None:
            self.front = new_node
            self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self._size += 1

    def dequeue(self) -> Optional[Patient]:
        """Removes and returns the patient at the front of the queue in O(1) time."""
        if self.is_empty():
            return None
        
        target_node = self.front
        assert target_node is not None
        self.front = self.front.next
        
        if self.front is None:
            self.rear = None
            
        target_node.next = None
        self._size -= 1
        return target_node.patient

    def peek(self) -> Optional[Patient]:
        """Returns the patient at the front without removing it. O(1) time."""
        if self.is_empty():
            return None
        assert self.front is not None
        return self.front.patient

    def is_empty(self) -> bool:
        """Checks if the queue is empty. O(1) time."""
        return self.front is None

    def size(self) -> int:
        """Returns number of elements in queue. O(1) time."""
        return self._size

    def to_list(self) -> List[Patient]:
        """Returns a snapshot of queued patients from front to rear."""
        patients = []
        curr = self.front
        while curr is not None:
            patients.append(curr.patient)
            curr = curr.next
        return patients

    def remove_by_id(self, patient_id: str) -> bool:
        """
        Removes a patient anywhere in the FIFO queue by ID.
        Useful when a waiting patient is cancelled. O(n) time.
        """
        if self.is_empty():
            return False

        clean_id = patient_id.strip().upper()
        curr = self.front
        prev: Optional[QueueNode] = None

        while curr is not None:
            if curr.patient.patient_id.upper() == clean_id:
                if prev is None:
                    self.front = curr.next
                    if self.front is None:
                        self.rear = None
                else:
                    prev.next = curr.next
                    if curr == self.rear:
                        self.rear = prev
                
                curr.next = None
                self._size -= 1
                return True

            prev = curr
            curr = curr.next

        return False
