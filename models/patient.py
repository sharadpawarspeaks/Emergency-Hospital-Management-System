"""
Patient Model module for Hospital Emergency Management System.
Defines patient entity, priority levels, and triage attributes.
"""

from datetime import datetime
from typing import Dict, Any, Optional


class PriorityLevel:
    """Standard emergency triage priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3

    LABELS = {
        CRITICAL: "Critical Emergency",
        HIGH: "High Priority",
        NORMAL: "Normal"
    }

    COLORS = {
        CRITICAL: "#E53E3E",  # Medical Red
        HIGH: "#DD6B20",      # Alert Orange
        NORMAL: "#38A169"     # Stable Green
    }

    BG_COLORS = {
        CRITICAL: "#FFF5F5",  # Light soft red tint
        HIGH: "#FFFAF0",      # Light soft orange tint
        NORMAL: "#F0FFF4"     # Light soft green tint
    }

    @classmethod
    def get_label(cls, priority: int) -> str:
        return cls.LABELS.get(priority, "Normal")

    @classmethod
    def get_color(cls, priority: int) -> str:
        return cls.COLORS.get(priority, "#38A169")

    @classmethod
    def get_bg_color(cls, priority: int) -> str:
        return cls.BG_COLORS.get(priority, "#F0FFF4")


class PatientStatus:
    WAITING = "Waiting"
    IN_TREATMENT = "In Treatment"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Patient:
    """
    Patient entity representing an individual in the hospital system.
    Maintains triage attributes, arrival timing, and treatment lifecycle status.
    """

    def __init__(
        self,
        patient_id: str,
        name: str,
        age: int,
        gender: str,
        symptoms: str,
        priority: int,
        contact: str = "",
        arrival_time: Optional[str] = None,
        arrival_timestamp: Optional[float] = None,
        arrival_sequence: int = 0,
        status: str = PatientStatus.WAITING,
        treatment_start_time: Optional[str] = None,
        treatment_completion_time: Optional[str] = None,
        treatment_notes: Optional[str] = None,
        attending_doctor: Optional[str] = None,
        triage_room: Optional[str] = None
    ):
        self.patient_id = patient_id.strip()
        self.name = name.strip()
        self.age = int(age)
        self.gender = gender.strip()
        self.contact = contact.strip()
        self.symptoms = symptoms.strip()
        self.priority = int(priority)
        self.arrival_sequence = arrival_sequence
        
        now = datetime.now()
        self.arrival_time = arrival_time or now.strftime("%Y-%m-%d %I:%M %p")
        self.arrival_timestamp = arrival_timestamp or now.timestamp()
        
        self.status = status
        self.treatment_start_time = treatment_start_time
        self.treatment_completion_time = treatment_completion_time
        self.treatment_notes = treatment_notes or ""
        self.attending_doctor = attending_doctor or "Dr. S. Nair (Chief ER)"
        self.triage_room = triage_room or "Bay 1 - Trauma Care"

    @property
    def priority_label(self) -> str:
        return PriorityLevel.get_label(self.priority)

    @property
    def priority_color(self) -> str:
        return PriorityLevel.get_color(self.priority)

    @property
    def waiting_duration_minutes(self) -> int:
        """Calculate waiting duration in minutes from arrival."""
        if self.arrival_timestamp:
            elapsed_sec = datetime.now().timestamp() - self.arrival_timestamp
            return max(0, int(elapsed_sec // 60))
        return 0

    @property
    def treatment_duration_minutes(self) -> Optional[int]:
        """Calculates duration of treatment in minutes if both timestamps exist."""
        if self.treatment_start_time and self.treatment_completion_time:
            try:
                fmt = "%Y-%m-%d %I:%M %p"
                t_start = datetime.strptime(self.treatment_start_time, fmt)
                t_end = datetime.strptime(self.treatment_completion_time, fmt)
                mins = int((t_end - t_start).total_seconds() // 60)
                return max(1, mins)
            except Exception:
                return 15  # Fallback reasonable estimate
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize patient for JSON storage."""
        return {
            "patient_id": self.patient_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "contact": self.contact,
            "symptoms": self.symptoms,
            "priority": self.priority,
            "arrival_time": self.arrival_time,
            "arrival_timestamp": self.arrival_timestamp,
            "arrival_sequence": self.arrival_sequence,
            "status": self.status,
            "treatment_start_time": self.treatment_start_time,
            "treatment_completion_time": self.treatment_completion_time,
            "treatment_notes": self.treatment_notes,
            "attending_doctor": self.attending_doctor,
            "triage_room": self.triage_room
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Patient":
        """Deserialize patient from dictionary."""
        return cls(
            patient_id=data["patient_id"],
            name=data["name"],
            age=data["age"],
            gender=data.get("gender", "Other"),
            contact=data.get("contact", ""),
            symptoms=data.get("symptoms", ""),
            priority=data.get("priority", PriorityLevel.NORMAL),
            arrival_time=data.get("arrival_time"),
            arrival_timestamp=data.get("arrival_timestamp"),
            arrival_sequence=data.get("arrival_sequence", 0),
            status=data.get("status", PatientStatus.WAITING),
            treatment_start_time=data.get("treatment_start_time"),
            treatment_completion_time=data.get("treatment_completion_time"),
            treatment_notes=data.get("treatment_notes", ""),
            attending_doctor=data.get("attending_doctor"),
            triage_room=data.get("triage_room")
        )

    def __repr__(self) -> str:
        return f"<Patient {self.patient_id}: {self.name} | P{self.priority} ({self.priority_label}) | {self.status}>"
