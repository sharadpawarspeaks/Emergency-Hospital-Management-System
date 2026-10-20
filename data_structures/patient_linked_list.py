"""
Custom Singly Linked List Implementation for Master Patient Records.
Provides dynamic memory node allocation, traversal, search, update, and deletion.
"""

from typing import List, Optional, Dict, Any
from models.patient import Patient


class PatientNode:
    """
    Node in the Singly Linked List holding a Patient record and pointer to next node.
    """

    def __init__(self, patient: Patient):
        self.patient: Patient = patient
        self.next: Optional["PatientNode"] = None

    def __repr__(self) -> str:
        return f"PatientNode({self.patient.patient_id}: {self.patient.name})"


class PatientLinkedList:
    """
    Authoritative In-Memory Singly Linked List for Patient Records.
    
    Time Complexities:
    - Insertion at Tail (with tail pointer): O(1)
    - Insertion at Head: O(1)
    - Search by Patient ID: O(n)
    - Update Patient Record: O(n) (traversal to node)
    - Deletion by Patient ID: O(n) (traversal + pointer relinking)
    - Display All / Traversal: O(n)
    """

    def __init__(self):
        self.head: Optional[PatientNode] = None
        self.tail: Optional[PatientNode] = None
        self._count: int = 0

    def insert_patient(self, patient: Patient) -> None:
        """
        Dynamically allocates a new PatientNode and appends it to the linked list.
        O(1) time complexity with tail pointer.
        """
        new_node = PatientNode(patient)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            assert self.tail is not None
            self.tail.next = new_node
            self.tail = new_node
        self._count += 1

    def insert_at_head(self, patient: Patient) -> None:
        """
        Inserts a new PatientNode at the beginning of the list.
        O(1) time complexity.
        """
        new_node = PatientNode(patient)
        new_node.next = self.head
        self.head = new_node
        if self.tail is None:
            self.tail = new_node
        self._count += 1

    def search_patient(self, patient_id: str) -> Optional[Patient]:
        """
        Linear search through linked list nodes by Patient ID.
        O(n) time complexity.
        """
        curr = self.head
        clean_id = patient_id.strip().upper()
        while curr is not None:
            if curr.patient.patient_id.upper() == clean_id:
                return curr.patient
            curr = curr.next
        return None

    def search_by_name(self, name_query: str) -> List[Patient]:
        """
        Searches for patients matching name substring.
        O(n) traversal.
        """
        results: List[Patient] = []
        curr = self.head
        query = name_query.strip().lower()
        while curr is not None:
            if query in curr.patient.name.lower():
                results.append(curr.patient)
            curr = curr.next
        return results

    def update_patient(self, patient_id: str, **kwargs: Any) -> bool:
        """
        Locates patient node and updates attributes.
        O(n) time complexity.
        """
        target = self.search_patient(patient_id)
        if target is None:
            return False
        
        for key, value in kwargs.items():
            if hasattr(target, key):
                setattr(target, key, value)
        return True

    def delete_patient(self, patient_id: str) -> bool:
        """
        Removes patient node from linked list by pointer manipulation.
        O(n) time complexity.
        """
        clean_id = patient_id.strip().upper()
        curr = self.head
        prev: Optional[PatientNode] = None

        while curr is not None:
            if curr.patient.patient_id.upper() == clean_id:
                # Found node to delete
                if prev is None:
                    # Deleting head node
                    self.head = curr.next
                    if self.head is None:
                        self.tail = None
                else:
                    # Relink previous node's next pointer
                    prev.next = curr.next
                    if curr == self.tail:
                        self.tail = prev

                curr.next = None  # Clear reference
                self._count -= 1
                return True

            prev = curr
            curr = curr.next

        return False

    def display_all_patients(self) -> List[Patient]:
        """
        Traverses the linked list from head to tail and returns all patient records.
        O(n) time complexity.
        """
        patients: List[Patient] = []
        curr = self.head
        while curr is not None:
            patients.append(curr.patient)
            curr = curr.next
        return patients

    def get_patient_count(self) -> int:
        """Returns total number of patient nodes in the linked list."""
        return self._count

    def clear(self) -> None:
        """Resets the linked list."""
        curr = self.head
        while curr is not None:
            next_node = curr.next
            curr.next = None
            curr = next_node
        self.head = None
        self.tail = None
        self._count = 0

    def to_pointer_visualization(self, max_nodes: int = 7) -> str:
        """
        Generates a text pointer representation of the linked list.
        Example: [PAT-1001] -> [PAT-1002] -> [PAT-1003] -> None
        """
        if self.head is None:
            return "HEAD -> None (List is empty)"
        
        parts = ["HEAD"]
        curr = self.head
        idx = 0
        while curr is not None and idx < max_nodes:
            parts.append(f"[{curr.patient.patient_id}: {curr.patient.name} (P{curr.patient.priority})]")
            curr = curr.next
            idx += 1
        
        if curr is not None:
            parts.append(f"... (+{self._count - max_nodes} more nodes)")
        parts.append("None")
        return " -> ".join(parts)
