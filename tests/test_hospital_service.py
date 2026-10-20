"""
Unit tests for HospitalService lifecycle, triage rules, and data persistence.
"""

import os
import unittest
from models.patient import PriorityLevel, PatientStatus
from services.hospital_service import HospitalService


class TestHospitalService(unittest.TestCase):
    def setUp(self):
        self.test_storage = "data/test_patients.json"
        if os.path.exists(self.test_storage):
            os.remove(self.test_storage)
        self.service = HospitalService(self.test_storage)

    def tearDown(self):
        if os.path.exists(self.test_storage):
            os.remove(self.test_storage)

    def test_registration_and_priority_triage_ordering(self):
        # Register:
        # A: Normal
        # B: Critical
        # C: High
        # D: Critical
        # E: Normal
        ok, _, pA = self.service.register_patient("Patient A", "30", "Male", "Headache", PriorityLevel.NORMAL)
        self.assertTrue(ok)
        ok, _, pB = self.service.register_patient("Patient B", "60", "Female", "Heart Attack", PriorityLevel.CRITICAL)
        self.assertTrue(ok)
        ok, _, pC = self.service.register_patient("Patient C", "45", "Male", "Fracture", PriorityLevel.HIGH)
        self.assertTrue(ok)
        ok, _, pD = self.service.register_patient("Patient D", "50", "Male", "Stroke", PriorityLevel.CRITICAL)
        self.assertTrue(ok)
        ok, _, pE = self.service.register_patient("Patient E", "25", "Female", "Allergy", PriorityLevel.NORMAL)
        self.assertTrue(ok)

        # Verify ordering in waiting queue
        waiting = self.service.get_waiting_queue_ordered()
        expected_names = ["Patient B", "Patient D", "Patient C", "Patient A", "Patient E"]
        actual_names = [p.name for p in waiting]
        self.assertEqual(actual_names, expected_names)

    def test_treatment_workflow_lifecycle(self):
        # Register 1 critical, 1 normal
        self.service.register_patient("John Normal", "30", "Male", "Cough", PriorityLevel.NORMAL)
        self.service.register_patient("Sarah Critical", "55", "Female", "Severe trauma", PriorityLevel.CRITICAL)

        # Start treatment: should pick Sarah Critical first!
        ok, msg, treated = self.service.start_treatment()
        self.assertTrue(ok)
        self.assertEqual(treated.name, "Sarah Critical")
        self.assertEqual(treated.status, PatientStatus.IN_TREATMENT)
        self.assertIsNotNone(self.service.active_patient)

        # Attempt to start treatment while occupied should fail
        ok2, err2, _ = self.service.start_treatment()
        self.assertFalse(ok2)

        # Complete treatment
        ok3, msg3, comp = self.service.complete_treatment("Stabilized in trauma bay.")
        self.assertTrue(ok3)
        self.assertEqual(comp.status, PatientStatus.COMPLETED)
        self.assertIsNone(self.service.active_patient)

        # Verify Sarah Critical remains in Master Records
        all_patients = self.service.get_all_patients()
        sarah = [p for p in all_patients if p.name == "Sarah Critical"][0]
        self.assertEqual(sarah.status, PatientStatus.COMPLETED)

        # Verify Treatment History contains Sarah
        history = self.service.get_treatment_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].name, "Sarah Critical")

        # Now start next treatment: should pick John Normal
        ok4, _, next_treated = self.service.start_treatment()
        self.assertTrue(ok4)
        self.assertEqual(next_treated.name, "John Normal")

    def test_persistence_reload(self):
        self.service.register_patient("Alice Waiting", "28", "Female", "Sprain", PriorityLevel.HIGH)
        self.service.register_patient("Bob InTreatment", "60", "Male", "Arrhythmia", PriorityLevel.CRITICAL)
        self.service.start_treatment()  # Bob starts treatment

        # Simulate app restart by instantiating new service pointing to same file
        reloaded_service = HospitalService(self.test_storage)
        self.assertEqual(len(reloaded_service.get_all_patients()), 2)
        
        # Verify active treatment restored
        self.assertIsNotNone(reloaded_service.active_patient)
        self.assertEqual(reloaded_service.active_patient.name, "Bob InTreatment")
        
        # Verify waiting queue has Alice
        waiting = reloaded_service.get_waiting_queue_ordered()
        self.assertEqual(len(waiting), 1)
        self.assertEqual(waiting[0].name, "Alice Waiting")


if __name__ == "__main__":
    unittest.main()
