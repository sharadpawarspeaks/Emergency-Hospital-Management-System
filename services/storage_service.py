"""
Storage Service for persisting and restoring hospital patient records.
Implements safe atomic JSON persistence and reconstruction of Linked List and Priority Queue.
"""

import json
import os
import tempfile
from typing import List, Dict, Any, Tuple
from models.patient import Patient, PatientStatus
from data_structures.patient_linked_list import PatientLinkedList
from data_structures.priority_queue import PriorityPatientQueue


class StorageService:
    def __init__(self, storage_path: str = "data/patients.json"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(os.path.abspath(self.storage_path)), exist_ok=True)

    def save_data(
        self,
        patients: List[Patient],
        activity_log: List[Dict[str, Any]],
        next_seq: int,
        next_id: int
    ) -> bool:
        """
        Saves all records atomically using a temporary file to prevent data corruption.
        """
        try:
            payload = {
                "metadata": {
                    "version": "1.0",
                    "next_sequence": next_seq,
                    "next_id_counter": next_id
                },
                "patients": [p.to_dict() for p in patients],
                "activity_log": activity_log[-100:]  # keep recent 100 activities
            }

            dir_name = os.path.dirname(os.path.abspath(self.storage_path))
            with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tf:
                json.dump(payload, tf, indent=2, ensure_ascii=False)
                temp_name = tf.name

            # Atomically replace target file
            os.replace(temp_name, self.storage_path)
            return True
        except Exception as e:
            print(f"[StorageService Error] Failed to save data: {e}")
            return False

    def load_data(
        self
    ) -> Tuple[PatientLinkedList, PriorityPatientQueue, Optional[Patient], List[Dict[str, Any]], int, int]:
        """
        Loads saved data and reconstructs:
        - Master PatientLinkedList
        - PriorityPatientQueue (only including patients who are actively WAITING)
        - Active In-Treatment Patient (if any)
        - Activity logs and counters
        """
        master_list = PatientLinkedList()
        waiting_queue = PriorityPatientQueue()
        active_patient: Optional[Patient] = None
        activity_log: List[Dict[str, Any]] = []
        next_seq = 1
        next_id = 1001

        if not os.path.exists(self.storage_path):
            return master_list, waiting_queue, active_patient, activity_log, next_seq, next_id

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                payload = json.load(f)

            meta = payload.get("metadata", {})
            next_seq = meta.get("next_sequence", 1)
            next_id = meta.get("next_id_counter", 1001)
            activity_log = payload.get("activity_log", [])

            patient_dicts = payload.get("patients", [])
            for pdata in patient_dicts:
                patient = Patient.from_dict(pdata)
                # Reconstruct master Singly Linked List
                master_list.insert_patient(patient)

                # Reconstruct waiting queue only for patients with status WAITING
                if patient.status == PatientStatus.WAITING:
                    waiting_queue.insert(patient)
                elif patient.status == PatientStatus.IN_TREATMENT and active_patient is None:
                    active_patient = patient

        except Exception as e:
            print(f"[StorageService Warning] Error reading {self.storage_path}: {e}. Starting fresh.")

        return master_list, waiting_queue, active_patient, activity_log, next_seq, next_id
