"""
Treatment Management Page for Hospital Emergency Management System.
Handles the complete clinical treatment workflow:
- Active Emergency Bay monitoring
- Dispatching next highest-priority patient from Binary Min-Heap
- Recording treatment start time, attending doctor, and bay location
- Completing treatment with clinical notes and archiving into history
"""

import customtkinter as ctk
from datetime import datetime
from typing import Callable, Optional
from ui.theme import Theme
from ui.components import CardFrame, PriorityBadge, StatusBadge, AlertBanner, EmptyState
from models.patient import Patient, PriorityLevel, PatientStatus
from services.hospital_service import HospitalService


class TreatmentPage(ctk.CTkScrollableFrame):
    def __init__(self, master, service: HospitalService, on_navigate: Callable[[str], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = service
        self.on_navigate = on_navigate

        self.doctor_var = ctk.StringVar(value="Dr. S. Nair (Chief ER)")
        self.room_var = ctk.StringVar(value="Bay 1 - Trauma Care & Resuscitation")

        self.build_ui()
        self.refresh_view()

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title = ctk.CTkLabel(
            header,
            text="Emergency Treatment Bay Management",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        title.pack(anchor="w")

        sub = ctk.CTkLabel(
            header,
            text="Active treatment monitoring, physician assignment, and emergency care completion workflow",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_MUTED
        )
        sub.pack(anchor="w")

        # Feedback banner container (only packed when an alert is active)
        self.banner_container = ctk.CTkFrame(self, fg_color="transparent")

        # Main Bay Container
        self.bay_card = CardFrame(self)
        self.bay_card.pack(fill="both", expand=True, pady=(0, 20))

        self.bay_content = ctk.CTkFrame(self.bay_card, fg_color="transparent")
        self.bay_content.pack(fill="both", expand=True, padx=24, pady=24)

    def _show_banner(self, message: str, alert_type: str = "info"):
        for w in self.banner_container.winfo_children():
            w.destroy()
        self.banner_container.pack(fill="x", pady=(0, 10), before=self.bay_card)
        AlertBanner(self.banner_container, message=message, alert_type=alert_type).pack(fill="x")

    def refresh_view(self):
        for w in self.bay_content.winfo_children():
            w.destroy()

        active = self.service.active_patient

        if active:
            self._render_active_patient_view(active)
        else:
            self._render_vacant_bay_view()

    def _render_active_patient_view(self, patient: Patient):
        """Displays full interface for patient currently undergoing treatment."""
        # Top status bar
        top_bar = ctk.CTkFrame(self.bay_content, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 16))

        bay_badge = ctk.CTkLabel(
            top_bar,
            text="🚨  BAY 1 OCCUPIED — EMERGENCY TREATMENT IN PROGRESS",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13, weight="bold"),
            text_color="#1E40AF",
            fg_color="#DBEAFE",
            corner_radius=6,
            padx=10,
            pady=4
        )
        bay_badge.pack(side="left")

        # Patient Info Hero Card
        info_card = ctk.CTkFrame(self.bay_content, fg_color=Theme.BG_HERO_CARD, corner_radius=Theme.RADIUS_CARD)
        info_card.pack(fill="x", pady=(0, 20))

        info_inner = ctk.CTkFrame(info_card, fg_color="transparent")
        info_inner.pack(fill="x", padx=20, pady=20)

        # Name and ID
        title_row = ctk.CTkFrame(info_inner, fg_color="transparent")
        title_row.pack(fill="x")

        ctk.CTkLabel(
            title_row,
            text=f"{patient.name} ({patient.patient_id})",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=24, weight="bold"),
            text_color="#FFFFFF"
        ).pack(side="left")

        # Priority Badge
        p_badge = PriorityBadge(title_row, priority=patient.priority)
        p_badge.pack(side="right")

        # Grid of clinical stats
        grid_frame = ctk.CTkFrame(info_inner, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(14, 0))
        grid_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        def make_stat_box(parent, col, label, val):
            b = ctk.CTkFrame(parent, fg_color="#1E293B", corner_radius=8)
            b.grid(row=0, column=col, padx=4, sticky="nsew")
            ctk.CTkLabel(b, text=label.upper(), font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10, weight="bold"), text_color="#94A3B8").pack(anchor="w", padx=10, pady=(8, 2))
            ctk.CTkLabel(b, text=val, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13, weight="bold"), text_color="#F8FAFC").pack(anchor="w", padx=10, pady=(0, 8))

        make_stat_box(grid_frame, 0, "Age / Gender", f"{patient.age}y  |  {patient.gender}")
        make_stat_box(grid_frame, 1, "Triage Facility", patient.triage_room or "Bay 1")
        make_stat_box(grid_frame, 2, "Attending Physician", patient.attending_doctor or "Dr. S. Nair")
        make_stat_box(grid_frame, 3, "Treatment Started", patient.treatment_start_time or "Just now")

        # Symptoms Callout
        symp_card = CardFrame(self.bay_content, fg_color=Theme.BG_CARD_SECONDARY)
        symp_card.pack(fill="x", pady=(0, 20))
        s_inner = ctk.CTkFrame(symp_card, fg_color="transparent")
        s_inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(s_inner, text="Triage Chief Complaints & Symptoms:", font=ctk.CTkFont(size=12, weight="bold"), text_color=Theme.TEXT_MUTED).pack(anchor="w")
        ctk.CTkLabel(s_inner, text=patient.symptoms, font=ctk.CTkFont(size=13), text_color=Theme.TEXT_MAIN, wraplength=700, justify="left").pack(anchor="w", pady=(4, 0))

        # Complete Treatment Action Card
        act_card = CardFrame(self.bay_content)
        act_card.pack(fill="x")

        act_inner = ctk.CTkFrame(act_card, fg_color="transparent")
        act_inner.pack(fill="x", padx=18, pady=16)

        ctk.CTkLabel(
            act_inner,
            text="Complete Treatment & Clinical Discharge Summary",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=15, weight="bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(anchor="w")

        ctk.CTkLabel(
            act_inner,
            text="Document clinical treatment outcome, medications administered, and discharge status before releasing bay:",
            font=ctk.CTkFont(size=12),
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(2, 10))

        self.notes_box = ctk.CTkTextbox(
            act_inner,
            height=85,
            corner_radius=Theme.RADIUS_BUTTON,
            font=ctk.CTkFont(size=12),
            border_width=1,
            border_color=Theme.BORDER_LIGHT
        )
        self.notes_box.insert("1.0", "Patient stabilized in emergency care bay. Vital signs normal. Prescriptions provided.")
        self.notes_box.pack(fill="x", pady=(0, 16))

        btn_row = ctk.CTkFrame(act_inner, fg_color="transparent")
        btn_row.pack(fill="x")

        btn_complete = ctk.CTkButton(
            btn_row,
            text="✓ Complete Treatment & Discharge Patient",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=14, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=42,
            corner_radius=Theme.RADIUS_BUTTON,
            command=self._handle_complete_treatment
        )
        btn_complete.pack(side="left")

    def _render_vacant_bay_view(self):
        """Displays state when Emergency Bay is vacant and ready for next patient."""
        # Top banner
        top_bar = ctk.CTkFrame(self.bay_content, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            top_bar,
            text="✨  BAY 1 READY — AVAILABLE FOR EMERGENCY ADMISSION",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13, weight="bold"),
            text_color="#047857",
            fg_color="#D1FAE5",
            corner_radius=6,
            padx=10,
            pady=4
        ).pack(side="left")

        # Next Patient in Priority Queue
        next_pt = self.service.get_next_patient_in_queue()

        dispatch_card = CardFrame(self.bay_content)
        dispatch_card.pack(fill="x", pady=(0, 20))

        disp_inner = ctk.CTkFrame(dispatch_card, fg_color="transparent")
        disp_inner.pack(fill="x", padx=20, pady=20)

        if not next_pt:
            EmptyState(
                disp_inner,
                title="Waiting Queue is Currently Empty",
                message="No emergency patients are currently awaiting treatment in the queue. Register a new incoming patient to begin triage.",
                icon_symbol="🏥"
            ).pack(fill="x", pady=20)

            btn_box = ctk.CTkFrame(disp_inner, fg_color="transparent")
            btn_box.pack(pady=10)

            ctk.CTkButton(
                btn_box,
                text="+ Register New Patient",
                fg_color=Theme.PRIMARY_BLUE,
                hover_color=Theme.PRIMARY_HOVER,
                command=lambda: self.on_navigate("register"),
                height=38
            ).pack(side="left", padx=6)
            return

        # Next Patient Details
        ctk.CTkLabel(
            disp_inner,
            text="Next Eligible Emergency Patient (Binary Min-Heap Root):",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            text_color=Theme.PRIMARY_BLUE
        ).pack(anchor="w")

        p_row = ctk.CTkFrame(disp_inner, fg_color="transparent")
        p_row.pack(fill="x", pady=(4, 12))

        ctk.CTkLabel(
            p_row,
            text=f"{next_pt.name} ({next_pt.patient_id})",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=Theme.TEXT_MAIN
        ).pack(side="left")

        badge = PriorityBadge(p_row, priority=next_pt.priority)
        badge.pack(side="left", padx=12)

        # Quick summary
        ctk.CTkLabel(
            disp_inner,
            text=f"• Symptoms: {next_pt.symptoms}\n• Age: {next_pt.age} years ({next_pt.gender})  |  Contact: {next_pt.contact or 'None'}\n• Arrival Time: {next_pt.arrival_time} ({next_pt.waiting_duration_minutes} minutes elapsed, Arrival Seq #{next_pt.arrival_sequence})",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_MUTED,
            justify="left"
        ).pack(anchor="w", pady=(0, 16))

        # Doctor & Room Selectors
        config_row = ctk.CTkFrame(disp_inner, fg_color="transparent")
        config_row.pack(fill="x", pady=(0, 18))
        config_row.grid_columnconfigure(0, weight=1)
        config_row.grid_columnconfigure(1, weight=1)

        # Doctor
        doc_box = ctk.CTkFrame(config_row, fg_color="transparent")
        doc_box.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ctk.CTkLabel(doc_box, text="Attending ER Physician", font=ctk.CTkFont(size=11, weight="bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        ctk.CTkOptionMenu(
            doc_box,
            variable=self.doctor_var,
            values=[
                "Dr. S. Nair (Chief ER Triage)",
                "Dr. A. Verma (Trauma Surgeon)",
                "Dr. P. Mehta (Critical Care Specialist)",
                "Dr. N. Patel (Emergency Resident)"
            ],
            height=36,
            corner_radius=Theme.RADIUS_BUTTON
        ).pack(fill="x")

        # Room / Bay
        room_box = ctk.CTkFrame(config_row, fg_color="transparent")
        room_box.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ctk.CTkLabel(room_box, text="Assigned Treatment Bay", font=ctk.CTkFont(size=11, weight="bold"), text_color=Theme.TEXT_MAIN).pack(anchor="w", pady=(0, 2))
        ctk.CTkOptionMenu(
            room_box,
            variable=self.room_var,
            values=[
                "Bay 1 - Trauma Care & Resuscitation",
                "Bay 2 - Acute Cardiac Care",
                "Bay 3 - Minor Trauma & Lacerations",
                "Bay 4 - General ER Observation"
            ],
            height=36,
            corner_radius=Theme.RADIUS_BUTTON
        ).pack(fill="x")

        # Start Treatment Button
        btn_start = ctk.CTkButton(
            disp_inner,
            text=f"⚡ Dispatch & Start Treatment for {next_pt.patient_id}",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=14, weight="bold"),
            fg_color=Theme.PRIMARY_BLUE,
            hover_color=Theme.PRIMARY_HOVER,
            height=44,
            corner_radius=Theme.RADIUS_BUTTON,
            command=self._handle_start_treatment
        )
        btn_start.pack(fill="x")

    def _handle_start_treatment(self):
        doc = self.doctor_var.get()
        room = self.room_var.get()
        ok, msg, patient = self.service.start_treatment(doctor_name=doc, room_name=room)
        if ok:
            self._show_banner(f"Treatment started for {patient.name} ({patient.patient_id}) in {patient.triage_room}.", "success")
        else:
            self._show_banner(msg, "error")
        self.refresh_view()

    def _handle_complete_treatment(self):
        notes = self.notes_box.get("1.0", "end-1c").strip()
        ok, msg, patient = self.service.complete_treatment(treatment_notes=notes)
        if ok:
            self._show_banner(f"Treatment completed for {patient.name} ({patient.patient_id}). Record archived into Treatment History.", "success")
        else:
            self._show_banner(msg, "error")
        self.refresh_view()


