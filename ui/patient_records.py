"""
Master Patient Records Page for Hospital Emergency Management System.
Demonstrates the authoritative Singly Linked List data structure.
Includes search, in-place record updates, deletion with pointer safety, and live pointer visualization.
"""

import customtkinter as ctk
from typing import Callable, Optional, List
from ui.theme import Theme
from ui.components import CardFrame, PriorityBadge, StatusBadge, EmptyState, PatientDetailsModal
from models.patient import Patient, PatientStatus, PriorityLevel
from services.hospital_service import HospitalService


class EditPatientDialog(ctk.CTkToplevel):
    """Dialog allowing modification of patient information stored in the Linked List."""
    def __init__(self, master, patient: Patient, on_saved: Callable[[str, str, str, str], None]):
        super().__init__(master)
        self.patient = patient
        self.on_saved = on_saved

        self.title(f"Update Patient Record - {patient.patient_id}")
        self.geometry("480x480")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.configure(fg_color=Theme.BG_APP)

        header = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, height=60)
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text=f"Edit Record: {patient.name} ({patient.patient_id})",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=16, weight="bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(side="left", padx=20, pady=16)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Name
        ctk.CTkLabel(body, text="Patient Full Name", font=ctk.CTkFont(size=11, weight="bold"), text_color=Theme.TEXT_MUTED).pack(anchor="w", pady=(0, 2))
        self.name_entry = ctk.CTkEntry(body, height=36, corner_radius=6)
        self.name_entry.insert(0, patient.name)
        self.name_entry.pack(fill="x", pady=(0, 10))

        # Age
        ctk.CTkLabel(body, text="Age (Years)", font=ctk.CTkFont(size=11, weight="bold"), text_color=Theme.TEXT_MUTED).pack(anchor="w", pady=(0, 2))
        self.age_entry = ctk.CTkEntry(body, height=36, corner_radius=6)
        self.age_entry.insert(0, str(patient.age))
        self.age_entry.pack(fill="x", pady=(0, 10))

        # Contact
        ctk.CTkLabel(body, text="Contact Phone Number", font=ctk.CTkFont(size=11, weight="bold"), text_color=Theme.TEXT_MUTED).pack(anchor="w", pady=(0, 2))
        self.contact_entry = ctk.CTkEntry(body, height=36, corner_radius=6)
        self.contact_entry.insert(0, patient.contact)
        self.contact_entry.pack(fill="x", pady=(0, 10))

        # Symptoms
        ctk.CTkLabel(body, text="Clinical Symptoms / Notes", font=ctk.CTkFont(size=11, weight="bold"), text_color=Theme.TEXT_MUTED).pack(anchor="w", pady=(0, 2))
        self.symptoms_entry = ctk.CTkTextbox(body, height=80, corner_radius=6)
        self.symptoms_entry.insert("1.0", patient.symptoms)
        self.symptoms_entry.pack(fill="x", pady=(0, 16))

        # Action Buttons
        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x")

        btn_cancel = ctk.CTkButton(
            btn_row, text="Cancel", fg_color=Theme.BG_CARD_SECONDARY,
            text_color=Theme.TEXT_MAIN, hover_color=Theme.BORDER_MEDIUM,
            command=self.destroy, height=36
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_save = ctk.CTkButton(
            btn_row, text="Save Updates", fg_color=Theme.PRIMARY_BLUE,
            hover_color=Theme.PRIMARY_HOVER, command=self._save, height=36
        )
        btn_save.pack(side="right")

    def _save(self):
        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        contact = self.contact_entry.get().strip()
        symptoms = self.symptoms_entry.get("1.0", "end-1c").strip()
        self.on_saved(name, age, contact, symptoms)
        self.destroy()


class ConfirmDeleteDialog(ctk.CTkToplevel):
    """Confirmation modal before deleting a node from the Master Linked List."""
    def __init__(self, master, patient: Patient, on_confirm: Callable[[], None]):
        super().__init__(master)
        self.title("Confirm Patient Deletion")
        self.geometry("440x240")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.configure(fg_color=Theme.BG_APP)

        header = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, height=55)
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text="⚠️ Confirm Linked List Node Deletion",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=15, weight="bold"),
            text_color=Theme.COLOR_CRITICAL
        ).pack(side="left", padx=20, pady=16)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(
            body,
            text=f"Are you sure you want to permanently delete patient node {patient.patient_id} ({patient.name}) from the Master Linked List? This will unlink pointers and safely remove any active queue entries.",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_MAIN,
            wraplength=400,
            justify="left"
        ).pack(anchor="w", pady=(0, 20))

        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x")

        btn_cancel = ctk.CTkButton(
            btn_row, text="Cancel", fg_color=Theme.BG_CARD_SECONDARY,
            text_color=Theme.TEXT_MAIN, hover_color=Theme.BORDER_MEDIUM,
            command=self.destroy, height=36
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_delete = ctk.CTkButton(
            btn_row, text="Delete Permanently", fg_color=Theme.COLOR_CRITICAL,
            hover_color="#B91C1C", command=lambda: [on_confirm(), self.destroy()], height=36
        )
        btn_delete.pack(side="right")


class PatientRecordsPage(ctk.CTkScrollableFrame):
    def __init__(self, master, service: HospitalService, on_navigate: Callable[[str], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = service
        self.on_navigate = on_navigate

        self.status_filter: Optional[str] = None
        self.search_query = ""

        self.build_ui()
        self.refresh_records()

    def build_ui(self):
        # 1. Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title = ctk.CTkLabel(
            header,
            text="Master Patient Records (Singly Linked List)",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        title.pack(anchor="w")

        sub = ctk.CTkLabel(
            header,
            text="Authoritative in-memory repository dynamically allocating PatientNode instances with sequential pointer traversal",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_MUTED
        )
        sub.pack(anchor="w")

        # 2. Linked List Pointer Chain Visualization Card
        self.pointer_card = CardFrame(self)
        self.pointer_card.pack(fill="x", pady=(0, 16))

        p_inner = ctk.CTkFrame(self.pointer_card, fg_color="transparent")
        p_inner.pack(fill="x", padx=18, pady=14)

        top_p = ctk.CTkFrame(p_inner, fg_color="transparent")
        top_p.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            top_p,
            text="🔗 Dynamic Memory Pointer Chain (Linked Node Traversal):",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=Theme.PRIMARY_BLUE
        ).pack(side="left")

        self.lbl_node_count = ctk.CTkLabel(
            top_p,
            text="Total Nodes: 0",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_node_count.pack(side="right")

        self.pointer_text = ctk.CTkLabel(
            p_inner,
            text="HEAD -> None",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY_MONO, size=11),
            text_color=Theme.TEXT_MAIN,
            wraplength=850,
            justify="left",
            anchor="w"
        )
        self.pointer_text.pack(anchor="w")

        # 3. Controls & Filter Bar
        ctrl_card = CardFrame(self)
        ctrl_card.pack(fill="x", pady=(0, 14))

        ctrl_inner = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        ctrl_inner.pack(fill="x", padx=16, pady=12)

        self.search_entry = ctk.CTkEntry(
            ctrl_inner,
            placeholder_text="🔍 Search records by ID, Name, or Symptoms...",
            width=320,
            height=36,
            corner_radius=Theme.RADIUS_BUTTON
        )
        self.search_entry.pack(side="left", padx=(0, 12))
        self.search_entry.bind("<KeyRelease>", lambda e: self._on_search_change())

        filter_box = ctk.CTkFrame(ctrl_inner, fg_color="transparent")
        filter_box.pack(side="right")

        self.btn_f_all = ctk.CTkButton(filter_box, text="All Records", width=85, height=32, corner_radius=6, command=lambda: self._set_status_filter(None))
        self.btn_f_all.pack(side="left", padx=2)

        self.btn_f_wait = ctk.CTkButton(filter_box, text="Waiting", width=75, height=32, corner_radius=6, command=lambda: self._set_status_filter(PatientStatus.WAITING))
        self.btn_f_wait.pack(side="left", padx=2)

        self.btn_f_treat = ctk.CTkButton(filter_box, text="In Treatment", width=95, height=32, corner_radius=6, command=lambda: self._set_status_filter(PatientStatus.IN_TREATMENT))
        self.btn_f_treat.pack(side="left", padx=2)

        self.btn_f_comp = ctk.CTkButton(filter_box, text="Completed", width=85, height=32, corner_radius=6, command=lambda: self._set_status_filter(PatientStatus.COMPLETED))
        self.btn_f_comp.pack(side="left", padx=2)

        self._update_filter_buttons()

        # 4. Master Records Table
        self.table_card = CardFrame(self)
        self.table_card.pack(fill="both", expand=True, pady=(0, 20))

        th = ctk.CTkFrame(self.table_card, fg_color=Theme.BG_CARD_SECONDARY, height=38, corner_radius=6)
        th.pack(fill="x", padx=16, pady=(16, 6))

        ctk.CTkLabel(th, text="PATIENT ID", width=95, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="PATIENT NAME", width=150, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="AGE/SEX", width=75, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="PRIORITY", width=135, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="STATUS", width=125, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="ARRIVAL TIME", width=140, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="ACTIONS", width=170, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="e").pack(side="right", padx=12)

        self.rows_container = ctk.CTkFrame(self.table_card, fg_color="transparent")
        self.rows_container.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def _set_status_filter(self, status: Optional[str]):
        self.status_filter = status
        self._update_filter_buttons()
        self.refresh_records()

    def _update_filter_buttons(self):
        btns = [
            (None, self.btn_f_all),
            (PatientStatus.WAITING, self.btn_f_wait),
            (PatientStatus.IN_TREATMENT, self.btn_f_treat),
            (PatientStatus.COMPLETED, self.btn_f_comp)
        ]
        for val, btn in btns:
            if val == self.status_filter:
                btn.configure(fg_color=Theme.PRIMARY_BLUE, text_color="#FFFFFF")
            else:
                btn.configure(fg_color=Theme.BG_CARD_SECONDARY, text_color=Theme.TEXT_MAIN)

    def _on_search_change(self):
        self.search_query = self.search_entry.get().strip().lower()
        self.refresh_records()

    def refresh_records(self):
        # Update Pointer Chain Visualization
        pointer_str = self.service.master_list.to_pointer_visualization()
        self.pointer_text.configure(text=pointer_str)
        count = self.service.master_list.get_patient_count()
        self.lbl_node_count.configure(text=f"Total Nodes: {count}")

        # Clear rows
        for w in self.rows_container.winfo_children():
            w.destroy()

        # Retrieve all patients via linked list traversal
        patients = self.service.master_list.display_all_patients()

        # Apply filtering
        filtered: List[Patient] = []
        for p in patients:
            if self.status_filter is not None and p.status != self.status_filter:
                continue
            if self.search_query:
                query_match = (
                    self.search_query in p.patient_id.lower() or
                    self.search_query in p.name.lower() or
                    self.search_query in p.symptoms.lower()
                )
                if not query_match:
                    continue
            filtered.append(p)

        if not filtered:
            EmptyState(
                self.rows_container,
                title="No Patient Records Found",
                message="No records match your search or filter criteria in the master linked list.",
                icon_symbol="🔍"
            ).pack(fill="both", expand=True, pady=30)
            return

        for idx, p in enumerate(filtered):
            row = ctk.CTkFrame(
                self.rows_container,
                fg_color=Theme.BG_CARD if idx % 2 == 0 else Theme.BG_CARD_SECONDARY,
                height=48,
                corner_radius=6
            )
            row.pack(fill="x", pady=2)

            # Patient ID
            ctk.CTkLabel(
                row,
                text=p.patient_id,
                width=95,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY_MONO, size=12, weight="bold"),
                text_color=Theme.TEXT_MAIN,
                anchor="w"
            ).pack(side="left", padx=4)

            # Name
            ctk.CTkLabel(
                row,
                text=p.name,
                width=150,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
                text_color=Theme.TEXT_MAIN,
                anchor="w"
            ).pack(side="left", padx=4)

            # Age/Sex
            ctk.CTkLabel(
                row,
                text=f"{p.age}y / {p.gender[0]}",
                width=75,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
                text_color=Theme.TEXT_MUTED,
                anchor="w"
            ).pack(side="left", padx=4)

            # Priority Badge
            b_box = ctk.CTkFrame(row, fg_color="transparent", width=135)
            b_box.pack(side="left", padx=4)
            badge = PriorityBadge(b_box, priority=p.priority)
            badge.pack(anchor="w")

            # Status Badge
            s_box = ctk.CTkFrame(row, fg_color="transparent", width=125)
            s_box.pack(side="left", padx=4)
            s_badge = StatusBadge(s_box, status=p.status)
            s_badge.pack(anchor="w")

            # Arrival Time
            ctk.CTkLabel(
                row,
                text=p.arrival_time,
                width=140,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
                text_color=Theme.TEXT_MUTED,
                anchor="w"
            ).pack(side="left", padx=4)

            # Actions Box
            act_box = ctk.CTkFrame(row, fg_color="transparent")
            act_box.pack(side="right", padx=10)

            # Details
            ctk.CTkButton(
                act_box, text="View", width=46, height=26, font=ctk.CTkFont(size=11),
                fg_color=Theme.BG_CARD_SECONDARY, text_color=Theme.TEXT_MAIN, hover_color=Theme.BORDER_MEDIUM,
                command=lambda pt=p: PatientDetailsModal(self, pt)
            ).pack(side="left", padx=2)

            # Edit
            ctk.CTkButton(
                act_box, text="Edit", width=46, height=26, font=ctk.CTkFont(size=11),
                fg_color="#EFF6FF", text_color=Theme.PRIMARY_BLUE, hover_color="#DBEAFE",
                command=lambda pt=p: self._open_edit_dialog(pt)
            ).pack(side="left", padx=2)

            # Delete
            ctk.CTkButton(
                act_box, text="Del", width=44, height=26, font=ctk.CTkFont(size=11),
                fg_color="#FEE2E2", text_color="#991B1B", hover_color="#FECACA",
                command=lambda pt=p: ConfirmDeleteDialog(self, pt, lambda pt_id=p.patient_id: self._delete_record(pt_id))
            ).pack(side="left", padx=2)

    def _open_edit_dialog(self, patient: Patient):
        def on_saved(name: str, age: str, contact: str, symptoms: str):
            ok, msg = self.service.update_patient_details(patient.patient_id, name, age, contact, symptoms)
            self.refresh_records()

        EditPatientDialog(self, patient, on_saved)

    def _delete_record(self, patient_id: str):
        self.service.delete_patient_record(patient_id)
        self.refresh_records()
