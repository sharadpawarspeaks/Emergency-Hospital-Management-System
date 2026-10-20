"""
Hospital Service coordinating triage, queuing algorithms, linked-list records, and treatment workflows.
Acts as the central facade separating GUI from pure Data Structures.
"""

import csv
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from models.patient import Patient, PriorityLevel, PatientStatus
from data_structures.patient_linked_list import PatientLinkedList
from data_structures.priority_queue import PriorityPatientQueue
from services.storage_service import StorageService


class HospitalService:
    def __init__(self, storage_path: str = "data/patients.json"):
        self.storage = StorageService(storage_path)
        (
            self.master_list,
            self.waiting_queue,
            self.active_patient,
            self.activity_log,
            self.sequence_counter,
            self.id_counter
        ) = self.storage.load_data()

    def log_activity(self, action_type: str, message: str, level: str = "info") -> None:
        """Records an event in the real-time activity feed."""
        timestamp = datetime.now().strftime("%I:%M %p")
        self.activity_log.append({
            "timestamp": timestamp,
            "action": action_type,
            "message": message,
            "level": level  # "critical", "warning", "success", "info"
        })
        if len(self.activity_log) > 100:
            self.activity_log.pop(0)

    def _persist(self) -> None:
        """Autosaves all records."""
        all_patients = self.master_list.display_all_patients()
        self.storage.save_data(
            patients=all_patients,
            activity_log=self.activity_log,
            next_seq=self.sequence_counter,
            next_id=self.id_counter
        )

    def validate_patient_input(
        self,
        name: str,
        age_str: str,
        gender: str,
        contact: str,
        symptoms: str,
        priority: int
    ) -> Tuple[bool, str]:
        """
        Validates patient registration input data.
        Returns (is_valid, error_message).
        """
        if not name or not name.strip():
            return False, "Patient Full Name is required."
        
        if len(name.strip()) < 2:
            return False, "Patient Name must be at least 2 characters."

        try:
            age = int(age_str.strip())
            if age <= 0 or age > 125:
                return False, "Please enter a valid age between 1 and 125."
        except ValueError:
            return False, "Age must be a valid positive integer."

        if not gender or gender not in ["Male", "Female", "Other"]:
            return False, "Please select a valid gender."

        if contact and contact.strip():
            clean_phone = re.sub(r"[\s\-\(\)\+]", "", contact.strip())
            if not clean_phone.isdigit() or len(clean_phone) < 7 or len(clean_phone) > 15:
                return False, "Contact number must be between 7 and 15 digits."

        if not symptoms or not symptoms.strip():
            return False, "Please specify primary symptoms or reason for visit."

        if priority not in [PriorityLevel.CRITICAL, PriorityLevel.HIGH, PriorityLevel.NORMAL]:
            return False, "Invalid triage priority selected."

        return True, ""

    def register_patient(
        self,
        name: str,
        age_str: str,
        gender: str,
        symptoms: str,
        priority: int,
        contact: str = "",
        attending_doctor: Optional[str] = None,
        triage_room: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Patient]]:
        """
        Registers a new emergency patient:
        1. Validates inputs
        2. Generates unique PAT-XXXX ID
        3. Inserts into Singly Linked List (authoritative storage)
        4. Inserts into Priority Queue (binary heap with FIFO tie-breaker)
        5. Logs activity and saves
        """
        is_valid, err_msg = self.validate_patient_input(name, age_str, gender, contact, symptoms, priority)
        if not is_valid:
            return False, err_msg, None

        patient_id = f"PAT-{self.id_counter}"
        self.id_counter += 1
        self.sequence_counter += 1

        patient = Patient(
            patient_id=patient_id,
            name=name.strip(),
            age=int(age_str.strip()),
            gender=gender,
            contact=contact.strip() if contact else "",
            symptoms=symptoms.strip(),
            priority=priority,
            arrival_sequence=self.sequence_counter,
            status=PatientStatus.WAITING,
            attending_doctor=attending_doctor,
            triage_room=triage_room
        )

        # Insert dynamically into master linked list
        self.master_list.insert_patient(patient)

        # Enqueue into priority queue
        self.waiting_queue.insert(patient)

        # Activity logging
        level = "critical" if priority == PriorityLevel.CRITICAL else ("warning" if priority == PriorityLevel.HIGH else "info")
        self.log_activity(
            "PATIENT_REGISTERED",
            f"Registered {patient.name} ({patient.patient_id}) as {patient.priority_label}",
            level=level
        )

        self._persist()
        return True, f"Patient {patient.name} ({patient.patient_id}) registered successfully!", patient

    def get_next_patient_in_queue(self) -> Optional[Patient]:
        """Peeks at the next eligible patient according to priority triage."""
        return self.waiting_queue.peek()

    def get_waiting_queue_ordered(self) -> List[Patient]:
        """Returns snapshot of waiting queue in exact priority triage order."""
        return self.waiting_queue.get_all_ordered()

    def start_treatment(self, doctor_name: Optional[str] = None, room_name: Optional[str] = None) -> Tuple[bool, str, Optional[Patient]]:
        """
        Dispatches highest priority patient to Active Treatment Bay:
        1. Verifies no current active treatment exists
        2. Dequeues highest priority patient from heap
        3. Updates status to 'In Treatment'
        4. Records start time
        """
        if self.active_patient is not None:
            return False, f"Treatment Bay is currently occupied by {self.active_patient.name} ({self.active_patient.patient_id}). Complete their treatment first.", None

        if self.waiting_queue.is_empty():
            return False, "No patients are currently waiting in the emergency queue.", None

        # Extract highest priority patient from binary min-heap
        patient = self.waiting_queue.pop_highest_priority()
        if patient is None:
            return False, "Waiting queue is empty.", None

        patient.status = PatientStatus.IN_TREATMENT
        patient.treatment_start_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        if doctor_name:
            patient.attending_doctor = doctor_name
        if room_name:
            patient.triage_room = room_name

        self.active_patient = patient

        # Update in master linked list
        self.master_list.update_patient(
            patient.patient_id,
            status=patient.status,
            treatment_start_time=patient.treatment_start_time,
            attending_doctor=patient.attending_doctor,
            triage_room=patient.triage_room
        )

        self.log_activity(
            "TREATMENT_STARTED",
            f"Started treatment for {patient.name} ({patient.patient_id}) in {patient.triage_room}",
            level="success"
        )

        self._persist()
        return True, f"Treatment started for {patient.name} ({patient.patient_id})", patient

    def complete_treatment(self, treatment_notes: str = "") -> Tuple[bool, str, Optional[Patient]]:
        """
        Completes current active treatment:
        1. Validates an active patient exists
        2. Records completion timestamp
        3. Updates status to 'Completed' in master linked list
        4. Clears active bay
        """
        if self.active_patient is None:
            return False, "There is currently no patient undergoing treatment.", None

        patient = self.active_patient
        patient.status = PatientStatus.COMPLETED
        patient.treatment_completion_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        if treatment_notes:
            patient.treatment_notes = treatment_notes.strip()

        # Update in master linked list
        self.master_list.update_patient(
            patient.patient_id,
            status=patient.status,
            treatment_completion_time=patient.treatment_completion_time,
            treatment_notes=patient.treatment_notes
        )

        self.active_patient = None

        self.log_activity(
            "TREATMENT_COMPLETED",
            f"Completed treatment for {patient.name} ({patient.patient_id}).",
            level="success"
        )

        self._persist()
        return True, f"Treatment successfully completed for {patient.name} ({patient.patient_id})", patient

    def remove_waiting_patient(self, patient_id: str, reason: str = "Patient left / Transferred") -> Tuple[bool, str]:
        """
        Removes a patient from the waiting queue safely.
        """
        clean_id = patient_id.strip().upper()
        if self.active_patient and self.active_patient.patient_id.upper() == clean_id:
            return False, "Cannot remove patient who is currently undergoing treatment. Complete treatment instead."

        # Check if in waiting queue
        removed = self.waiting_queue.remove_by_id(clean_id)
        if not removed:
            return False, f"Patient {clean_id} is not currently in the active waiting queue."

        # Update status in linked list to CANCELLED
        self.master_list.update_patient(
            clean_id,
            status=PatientStatus.CANCELLED,
            treatment_notes=f"Removed from queue: {reason}"
        )

        self.log_activity(
            "PATIENT_REMOVED",
            f"Removed {clean_id} from queue. Reason: {reason}",
            level="warning"
        )

        self._persist()
        return True, f"Patient {clean_id} removed from emergency queue."

    def update_patient_details(self, patient_id: str, name: str, age_str: str, contact: str, symptoms: str) -> Tuple[bool, str]:
        """Updates editable patient information in the linked list and queue."""
        clean_id = patient_id.strip().upper()
        patient = self.master_list.search_patient(clean_id)
        if not patient:
            return False, f"Patient with ID {clean_id} not found."

        if not name.strip():
            return False, "Name cannot be empty."

        try:
            age = int(age_str.strip())
            if age <= 0 or age > 125:
                return False, "Age must be between 1 and 125."
        except ValueError:
            return False, "Age must be a valid positive integer."

        patient.name = name.strip()
        patient.age = age
        patient.contact = contact.strip()
        patient.symptoms = symptoms.strip()

        self.log_activity(
            "RECORD_UPDATED",
            f"Updated records for {patient.name} ({patient.patient_id})",
            level="info"
        )

        self._persist()
        return True, f"Patient record {patient.patient_id} updated successfully."

    def delete_patient_record(self, patient_id: str) -> Tuple[bool, str]:
        """Permanently deletes record from linked list and removes from queue if waiting."""
        clean_id = patient_id.strip().upper()
        
        if self.active_patient and self.active_patient.patient_id.upper() == clean_id:
            return False, "Cannot delete patient who is currently receiving treatment."

        # Remove from waiting queue if present
        self.waiting_queue.remove_by_id(clean_id)

        # Remove from singly linked list
        deleted = self.master_list.delete_patient(clean_id)
        if not deleted:
            return False, f"Patient {clean_id} was not found in records."

        self.log_activity(
            "RECORD_DELETED",
            f"Deleted record for {clean_id} permanently.",
            level="warning"
        )

        self._persist()
        return True, f"Patient record {clean_id} deleted successfully."

    def get_all_patients(self) -> List[Patient]:
        """Returns all patients from master linked list."""
        return self.master_list.display_all_patients()

    def get_treatment_history(self) -> List[Patient]:
        """Returns all completed patient records."""
        return [p for p in self.master_list.display_all_patients() if p.status == PatientStatus.COMPLETED]

    def export_treatment_history_csv(self, filepath: str) -> Tuple[bool, str]:
        """Exports completed treatments to CSV format."""
        try:
            history = self.get_treatment_history()
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Patient ID",
                    "Patient Name",
                    "Age",
                    "Gender",
                    "Priority",
                    "Priority Label",
                    "Symptoms",
                    "Arrival Time",
                    "Treatment Start Time",
                    "Treatment Completion Time",
                    "Duration (Mins)",
                    "Attending Doctor",
                    "Treatment Notes",
                    "Final Status"
                ])
                for p in history:
                    writer.writerow([
                        p.patient_id,
                        p.name,
                        p.age,
                        p.gender,
                        p.priority,
                        p.priority_label,
                        p.symptoms,
                        p.arrival_time,
                        p.treatment_start_time or "N/A",
                        p.treatment_completion_time or "N/A",
                        p.treatment_duration_minutes or "N/A",
                        p.attending_doctor or "N/A",
                        p.treatment_notes or "",
                        p.status
                    ])
            return True, f"Exported {len(history)} records to {filepath}"
        except Exception as e:
            return False, f"Failed to export CSV: {e}"

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Computes live real-time statistics from master linked list and queues."""
        all_patients = self.master_list.display_all_patients()
        total_patients = len(all_patients)
        
        waiting_patients = self.waiting_queue.get_all_ordered()
        waiting_count = len(waiting_patients)
        
        critical_count = sum(1 for p in waiting_patients if p.priority == PriorityLevel.CRITICAL)
        high_count = sum(1 for p in waiting_patients if p.priority == PriorityLevel.HIGH)
        normal_count = sum(1 for p in waiting_patients if p.priority == PriorityLevel.NORMAL)
        
        completed_count = sum(1 for p in all_patients if p.status == PatientStatus.COMPLETED)
        in_treatment_count = 1 if self.active_patient else 0

        # Calculate average waiting duration of waiting queue
        if waiting_patients:
            total_wait = sum(p.waiting_duration_minutes for p in waiting_patients)
            avg_wait = int(total_wait / len(waiting_patients))
        else:
            avg_wait = 0

        return {
            "total_patients": total_patients,
            "waiting_count": waiting_count,
            "critical_count": critical_count,
            "high_count": high_count,
            "normal_count": normal_count,
            "completed_count": completed_count,
            "in_treatment_count": in_treatment_count,
            "avg_wait_time": avg_wait,
            "active_patient": self.active_patient,
            "priority_distribution": {
                "Critical Emergency": critical_count,
                "High Priority": high_count,
                "Normal": normal_count
            }
        }


