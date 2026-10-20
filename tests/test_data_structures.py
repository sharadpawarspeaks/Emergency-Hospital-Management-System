"""
Unit tests for custom data structures and priority scheduling algorithm.
Verifies requirement scenarios:
1. Critical Emergency treated before High and Normal
2. High Priority treated before Normal
3. Strict FIFO ordering for identical priorities
4. Singly Linked List operations (insert, search, update, delete)
5. Queue cancellation and heap restoration
"""

import unittest
from models.patient import Patient, PriorityLevel, PatientStatus
from data_structures.patient_linked_list import PatientLinkedList
from data_structures.patient_queue import PatientQueue
from data_structures.priority_queue import PriorityPatientQueue


class TestPatientLinkedList(unittest.TestCase):
    def setUp(self):
        self.ll = PatientLinkedList()
        self.p1 = Patient(patient_id="PAT-1001", name="Alice", age=30, gender="Female", symptoms="Fever", priority=PriorityLevel.NORMAL)
        self.p2 = Patient(patient_id="PAT-1002", name="Bob", age=45, gender="Male", symptoms="Chest Pain", priority=PriorityLevel.CRITICAL)
        self.p3 = Patient(patient_id="PAT-1003", name="Charlie", age=22, gender="Male", symptoms="Fracture", priority=PriorityLevel.HIGH)

    def test_insertion_and_display(self):
        self.assertEqual(self.ll.get_patient_count(), 0)
        self.ll.insert_patient(self.p1)
        self.ll.insert_patient(self.p2)
        self.ll.insert_patient(self.p3)
        self.assertEqual(self.ll.get_patient_count(), 3)
        
        all_patients = self.ll.display_all_patients()
        self.assertEqual(len(all_patients), 3)
        self.assertEqual(all_patients[0].patient_id, "PAT-1001")
        self.assertEqual(all_patients[1].patient_id, "PAT-1002")
        self.assertEqual(all_patients[2].patient_id, "PAT-1003")

    def test_search_by_id(self):
        self.ll.insert_patient(self.p1)
        self.ll.insert_patient(self.p2)
        
        found = self.ll.search_patient("PAT-1002")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Bob")
        
        not_found = self.ll.search_patient("PAT-9999")
        self.assertIsNone(not_found)

    def test_search_by_name(self):
        self.ll.insert_patient(self.p1)
        self.ll.insert_patient(self.p2)
        
        matches = self.ll.search_by_name("li")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].name, "Alice")

    def test_update_patient(self):
        self.ll.insert_patient(self.p1)
        updated = self.ll.update_patient("PAT-1001", contact="999-888-7777", symptoms="Severe Migraine")
        self.assertTrue(updated)
        
        patient = self.ll.search_patient("PAT-1001")
        self.assertEqual(patient.contact, "999-888-7777")
        self.assertEqual(patient.symptoms, "Severe Migraine")

    def test_delete_patient(self):
        self.ll.insert_patient(self.p1)
        self.ll.insert_patient(self.p2)
        self.ll.insert_patient(self.p3)
        
        # Delete middle node
        deleted = self.ll.delete_patient("PAT-1002")
        self.assertTrue(deleted)
        self.assertEqual(self.ll.get_patient_count(), 2)
        self.assertIsNone(self.ll.search_patient("PAT-1002"))
        
        # Delete head node
        deleted_head = self.ll.delete_patient("PAT-1001")
        self.assertTrue(deleted_head)
        self.assertEqual(self.ll.get_patient_count(), 1)
        self.assertEqual(self.ll.head.patient.patient_id, "PAT-1003")
        
        # Delete tail node
        deleted_tail = self.ll.delete_patient("PAT-1003")
        self.assertTrue(deleted_tail)
        self.assertEqual(self.ll.get_patient_count(), 0)
        self.assertIsNone(self.ll.head)
        self.assertIsNone(self.ll.tail)


class TestFIFOQueue(unittest.TestCase):
    def test_enqueue_dequeue(self):
        q = PatientQueue()
        self.assertTrue(q.is_empty())
        
        p1 = Patient(patient_id="P1", name="P1", age=20, gender="F", symptoms="Test", priority=3)
        p2 = Patient(patient_id="P2", name="P2", age=30, gender="M", symptoms="Test", priority=3)
        
        q.enqueue(p1)
        q.enqueue(p2)
        self.assertEqual(q.size(), 2)
        self.assertEqual(q.peek().patient_id, "P1")
        
        dequeued = q.dequeue()
        self.assertEqual(dequeued.patient_id, "P1")
        self.assertEqual(q.size(), 1)
        self.assertEqual(q.peek().patient_id, "P2")


class TestPriorityPatientQueue(unittest.TestCase):
    def test_priority_and_fifo_order(self):
        """
        Verify priority scheduling and FIFO tie-breaking scenario:
        Patient A — Normal (P3, seq 1)
        Patient B — Critical (P1, seq 2)
        Patient C — High (P2, seq 3)
        Patient D — Critical (P1, seq 4)
        Patient E — Normal (P3, seq 5)
        
        Expected treatment order:
        1. Patient B (Critical, seq 2)
        2. Patient D (Critical, seq 4)
        3. Patient C (High, seq 3)
        4. Patient A (Normal, seq 1)
        5. Patient E (Normal, seq 5)
        """
        pq = PriorityPatientQueue()
        
        patient_a = Patient("PAT-A", "Patient A", 20, "M", "Flu", PriorityLevel.NORMAL, arrival_sequence=1)
        patient_b = Patient("PAT-B", "Patient B", 50, "F", "Cardiac arrest", PriorityLevel.CRITICAL, arrival_sequence=2)
        patient_c = Patient("PAT-C", "Patient C", 35, "M", "Deep laceration", PriorityLevel.HIGH, arrival_sequence=3)
        patient_d = Patient("PAT-D", "Patient D", 60, "M", "Severe stroke", PriorityLevel.CRITICAL, arrival_sequence=4)
        patient_e = Patient("PAT-E", "Patient E", 25, "F", "Mild rash", PriorityLevel.NORMAL, arrival_sequence=5)
        
        # Insert in arbitrary arrival order
        pq.insert(patient_a)
        pq.insert(patient_b)
        pq.insert(patient_c)
        pq.insert(patient_d)
        pq.insert(patient_e)
        
        self.assertEqual(pq.size(), 5)
        
        # Extraction order must match specification exactly
        served = []
        while not pq.is_empty():
            served.append(pq.pop_highest_priority())
            
        expected_ids = ["PAT-B", "PAT-D", "PAT-C", "PAT-A", "PAT-E"]
        served_ids = [p.patient_id for p in served]
        self.assertEqual(served_ids, expected_ids)

    def test_remove_by_id(self):
        pq = PriorityPatientQueue()
        p1 = Patient("P1", "P1", 20, "F", "Flu", PriorityLevel.HIGH, arrival_sequence=1)
        p2 = Patient("P2", "P2", 30, "M", "Chest pain", PriorityLevel.CRITICAL, arrival_sequence=2)
        p3 = Patient("P3", "P3", 40, "M", "Broken arm", PriorityLevel.NORMAL, arrival_sequence=3)
        
        pq.insert(p1)
        pq.insert(p2)
        pq.insert(p3)
        
        # Remove P1 from middle of heap
        removed = pq.remove_by_id("P1")
        self.assertTrue(removed)
        self.assertEqual(pq.size(), 2)
        
        # Next should still be P2 (Critical) then P3 (Normal)
        self.assertEqual(pq.pop_highest_priority().patient_id, "P2")
        self.assertEqual(pq.pop_highest_priority().patient_id, "P3")
        self.assertTrue(pq.is_empty())


if __name__ == "__main__":
    unittest.main()
