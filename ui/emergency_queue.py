"""
Emergency Queue Page for Hospital Emergency Management System.
Displays the prioritized treatment queue managed by the custom Binary Min-Heap Priority Queue.
"""

import customtkinter as ctk
from typing import Callable, Optional, List
from ui.theme import Theme
from ui.components import CardFrame, PriorityBadge, StatusBadge, EmptyState, PatientDetailsModal
from models.patient import Patient, PriorityLevel, PatientStatus
from services.hospital_service import HospitalService


class RemovePatientDialog(ctk.CTkToplevel):
    """Dialog to confirm and record reason for removing a patient from waiting queue."""
    def __init__(self, master, patient: Patient, on_confirm: Callable[[str], None]):
        super().__init__(master)
        self.patient = patient
        self.on_confirm = on_confirm

        self.title("Remove Patient from Queue")
        self.geometry("450x300")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.configure(fg_color=Theme.BG_APP)

        header = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, height=60)
        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text=f"Remove {patient.name} ({patient.patient_id})",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=15, weight="bold"),
            text_color=Theme.COLOR_CRITICAL
        ).pack(side="left", padx=20, pady=16)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        ctk.CTkLabel(
            body,
            text="Please specify the reason for removing this patient from the waiting queue:",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_MAIN,
            wraplength=410,
            justify="left"
        ).pack(anchor="w", pady=(0, 8))

        self.reason_menu = ctk.CTkOptionMenu(
            body,
            values=[
                "Patient left against medical advice (LAMA)",
                "Transferred to specialized trauma facility",
                "Condition resolved / Patient declined care",
                "Admitted directly via ICU/Specialist team",
                "Duplicate / Registration error"
            ],
            height=36,
            corner_radius=Theme.RADIUS_BUTTON
        )
        self.reason_menu.pack(fill="x", pady=(0, 16))

        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x")

        btn_cancel = ctk.CTkButton(
            btn_row,
            text="Cancel",
            fg_color=Theme.BG_CARD_SECONDARY,
            text_color=Theme.TEXT_MAIN,
            hover_color=Theme.BORDER_MEDIUM,
            command=self.destroy,
            height=36,
            corner_radius=Theme.RADIUS_BUTTON
        )
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_remove = ctk.CTkButton(
            btn_row,
            text="Confirm Removal",
            fg_color=Theme.COLOR_CRITICAL,
            hover_color="#B91C1C",
            command=self._confirm,
            height=36,
            corner_radius=Theme.RADIUS_BUTTON
        )
        btn_remove.pack(side="right")

    def _confirm(self):
        reason = self.reason_menu.get()
        self.on_confirm(reason)
        self.destroy()


class EmergencyQueuePage(ctk.CTkScrollableFrame):
    def __init__(self, master, service: HospitalService, on_navigate: Callable[[str], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.service = service
        self.on_navigate = on_navigate

        self.filter_priority: Optional[int] = None
        self.search_query = ""

        self.build_ui()
        self.refresh_queue()

    def build_ui(self):
        # 1. Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        title = ctk.CTkLabel(
            header,
            text="Priority-Based Emergency Triage Queue",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        title.pack(anchor="w")

        sub = ctk.CTkLabel(
            header,
            text="Ordered strictly by Clinical Severity (Critical P1 → High P2 → Normal P3) with FIFO arrival tie-breaking",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_MUTED
        )
        sub.pack(anchor="w")

        # 2. Next Patient in Line Callout Banner
        self.next_banner = CardFrame(self)
        self.next_banner.pack(fill="x", pady=(0, 16))
        self._build_next_patient_banner()

        # 3. Filter & Search Controls Bar
        control_card = CardFrame(self)
        control_card.pack(fill="x", pady=(0, 14))

        ctrl_inner = ctk.CTkFrame(control_card, fg_color="transparent")
        ctrl_inner.pack(fill="x", padx=16, pady=12)

        # Search Box
        self.search_entry = ctk.CTkEntry(
            ctrl_inner,
            placeholder_text="🔍 Search queue by Patient ID or Name...",
            width=300,
            height=36,
            corner_radius=Theme.RADIUS_BUTTON
        )
        self.search_entry.pack(side="left", padx=(0, 12))
        self.search_entry.bind("<KeyRelease>", lambda e: self._on_search_change())

        # Priority Filters (All, Critical, High, Normal)
        filter_box = ctk.CTkFrame(ctrl_inner, fg_color="transparent")
        filter_box.pack(side="right")

        self.btn_filter_all = ctk.CTkButton(
            filter_box, text="All", width=55, height=32, corner_radius=6,
            fg_color=Theme.PRIMARY_BLUE, hover_color=Theme.PRIMARY_HOVER,
            command=lambda: self._set_priority_filter(None)
        )
        self.btn_filter_all.pack(side="left", padx=3)

        self.btn_filter_crit = ctk.CTkButton(
            filter_box, text="🚨 Critical", width=85, height=32, corner_radius=6,
            fg_color=Theme.BG_CARD_SECONDARY, text_color=Theme.TEXT_MAIN, hover_color=Theme.BORDER_MEDIUM,
            command=lambda: self._set_priority_filter(PriorityLevel.CRITICAL)
        )
        self.btn_filter_crit.pack(side="left", padx=3)

        self.btn_filter_high = ctk.CTkButton(
            filter_box, text="⚠️ High", width=75, height=32, corner_radius=6,
            fg_color=Theme.BG_CARD_SECONDARY, text_color=Theme.TEXT_MAIN, hover_color=Theme.BORDER_MEDIUM,
            command=lambda: self._set_priority_filter(PriorityLevel.HIGH)
        )
        self.btn_filter_high.pack(side="left", padx=3)

        self.btn_filter_norm = ctk.CTkButton(
            filter_box, text="🟢 Normal", width=80, height=32, corner_radius=6,
            fg_color=Theme.BG_CARD_SECONDARY, text_color=Theme.TEXT_MAIN, hover_color=Theme.BORDER_MEDIUM,
            command=lambda: self._set_priority_filter(PriorityLevel.NORMAL)
        )
        self.btn_filter_norm.pack(side="left", padx=3)

        # 4. Queue Table Card
        self.table_card = CardFrame(self)
        self.table_card.pack(fill="both", expand=True, pady=(0, 20))

        # Table Header
        th = ctk.CTkFrame(self.table_card, fg_color=Theme.BG_CARD_SECONDARY, height=38, corner_radius=6)
        th.pack(fill="x", padx=16, pady=(16, 6))

        ctk.CTkLabel(th, text="POS", width=45, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED).pack(side="left", padx=4)
        ctk.CTkLabel(th, text="PATIENT ID", width=95, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="PATIENT NAME", width=160, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="AGE/SEX", width=75, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="PRIORITY", width=140, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="SYMPTOMS / TRIAGE", width=200, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="WAIT TIME", width=85, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(th, text="ACTIONS", width=140, font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"), text_color=Theme.TEXT_MUTED, anchor="e").pack(side="right", padx=12)

        # Dynamic Rows container
        self.rows_container = ctk.CTkFrame(self.table_card, fg_color="transparent")
        self.rows_container.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def _build_next_patient_banner(self):
        container = ctk.CTkFrame(self.next_banner, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=16)

        left = ctk.CTkFrame(container, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        self.next_eyebrow = ctk.CTkLabel(
            left,
            text="⚡ NEXT PATIENT IN QUEUE (BINARY HEAP ROOT)",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=Theme.PRIMARY_BLUE
        )
        self.next_eyebrow.pack(anchor="w")

        self.next_title = ctk.CTkLabel(
            left,
            text="Queue Empty",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=18, weight="bold"),
            text_color=Theme.TEXT_MAIN
        )
        self.next_title.pack(anchor="w", pady=(2, 2))

        self.next_details = ctk.CTkLabel(
            left,
            text="No patients waiting for treatment.",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12),
            text_color=Theme.TEXT_MUTED
        )
        self.next_details.pack(anchor="w")

        self.btn_next_dispatch = ctk.CTkButton(
            container,
            text="Start Treatment →",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=13, weight="bold"),
            fg_color=Theme.PRIMARY_BLUE,
            hover_color=Theme.PRIMARY_HOVER,
            command=self._handle_dispatch_next,
            height=38,
            corner_radius=Theme.RADIUS_BUTTON
        )
        self.btn_next_dispatch.pack(side="right")

    def _set_priority_filter(self, priority: Optional[int]):
        self.filter_priority = priority
        # Update button highlights
        buttons = [
            (None, self.btn_filter_all),
            (PriorityLevel.CRITICAL, self.btn_filter_crit),
            (PriorityLevel.HIGH, self.btn_filter_high),
            (PriorityLevel.NORMAL, self.btn_filter_norm)
        ]
        for p_val, btn in buttons:
            if p_val == priority:
                btn.configure(fg_color=Theme.PRIMARY_BLUE, text_color="#FFFFFF")
            else:
                btn.configure(fg_color=Theme.BG_CARD_SECONDARY, text_color=Theme.TEXT_MAIN)
        self.refresh_queue()

    def _on_search_change(self):
        self.search_query = self.search_entry.get().strip().lower()
        self.refresh_queue()

    def refresh_queue(self):
        # Update Next Patient Callout
        next_pt = self.service.get_next_patient_in_queue()
        if next_pt:
            self.next_title.configure(
                text=f"{next_pt.name} ({next_pt.patient_id}) - {next_pt.priority_label}",
                text_color=next_pt.priority_color
            )
            self.next_details.configure(
                text=f"Reason: {next_pt.symptoms} | Arrival Seq #{next_pt.arrival_sequence} | Waiting: {next_pt.waiting_duration_minutes}m"
            )
            self.btn_next_dispatch.configure(
                text=f"⚡ Start Treatment ({next_pt.patient_id})",
                state="normal"
            )
        else:
            self.next_title.configure(text="No Patients Waiting in Emergency Queue", text_color=Theme.TEXT_MUTED)
            self.next_details.configure(text="All registered patients have been treated or discharged.")
            self.btn_next_dispatch.configure(text="Queue Clear", state="disabled")

        # Clear existing rows
        for w in self.rows_container.winfo_children():
            w.destroy()

        # Fetch ordered list from custom binary heap
        all_waiting = self.service.get_waiting_queue_ordered()

        # Apply filtering
        filtered: List[Patient] = []
        for p in all_waiting:
            if self.filter_priority is not None and p.priority != self.filter_priority:
                continue
            if self.search_query:
                if self.search_query not in p.patient_id.lower() and self.search_query not in p.name.lower():
                    continue
            filtered.append(p)

        if not filtered:
            msg = "No patients match the current filter or search criteria." if (self.filter_priority or self.search_query) else "No patients are currently awaiting treatment in the emergency room."
            empty = EmptyState(
                self.rows_container,
                title="No Queue Entries",
                message=msg,
                icon_symbol="📭"
            )
            empty.pack(fill="both", expand=True, pady=30)
            return

        # Render rows
        for idx, p in enumerate(filtered):
            row = ctk.CTkFrame(
                self.rows_container,
                fg_color=Theme.BG_CARD if idx % 2 == 0 else Theme.BG_CARD_SECONDARY,
                height=48,
                corner_radius=6
            )
            row.pack(fill="x", pady=2)

            # Pos
            ctk.CTkLabel(
                row,
                text=f"#{idx + 1}",
                width=45,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
                text_color=Theme.PRIMARY_BLUE if idx == 0 else Theme.TEXT_MUTED
            ).pack(side="left", padx=4)

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
                width=160,
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
            b_box = ctk.CTkFrame(row, fg_color="transparent", width=140)
            b_box.pack(side="left", padx=4)
            badge = PriorityBadge(b_box, priority=p.priority)
            badge.pack(anchor="w")

            # Symptoms
            ctk.CTkLabel(
                row,
                text=p.symptoms,
                width=200,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
                text_color=Theme.TEXT_MAIN,
                anchor="w"
            ).pack(side="left", padx=4)

            # Wait Time
            ctk.CTkLabel(
                row,
                text=f"{p.waiting_duration_minutes}m (seq #{p.arrival_sequence})",
                width=85,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
                text_color=Theme.TEXT_MUTED,
                anchor="w"
            ).pack(side="left", padx=4)

            # Actions
            act_box = ctk.CTkFrame(row, fg_color="transparent")
            act_box.pack(side="right", padx=10)

            # View Details
            btn_view = ctk.CTkButton(
                act_box,
                text="Details",
                width=60,
                height=28,
                font=ctk.CTkFont(size=11),
                fg_color=Theme.BG_CARD_SECONDARY,
                text_color=Theme.TEXT_MAIN,
                hover_color=Theme.BORDER_MEDIUM,
                command=lambda pt=p: PatientDetailsModal(self, pt)
            )
            btn_view.pack(side="left", padx=2)

            # Remove / Cancel
            btn_rem = ctk.CTkButton(
                act_box,
                text="Remove",
                width=60,
                height=28,
                font=ctk.CTkFont(size=11),
                fg_color="#FEE2E2",
                text_color="#991B1B",
                hover_color="#FECACA",
                command=lambda pt=p: self._open_remove_dialog(pt)
            )
            btn_rem.pack(side="left", padx=2)

    def _open_remove_dialog(self, patient: Patient):
        def on_confirm(reason: str):
            self.service.remove_waiting_patient(patient.patient_id, reason)
            self.refresh_queue()

        RemovePatientDialog(self, patient, on_confirm)

    def _handle_dispatch_next(self):
        ok, msg, _ = self.service.start_treatment()
        self.refresh_queue()
        if ok:
            self.on_navigate("treatment")
